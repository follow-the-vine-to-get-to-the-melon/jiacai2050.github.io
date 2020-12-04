---
categories:
- 编程语言
date: 2017-02-09 21:51:29
tags:
- Clojure
title: Clojure 运行原理之字节码生成篇
---

[上一篇文章](/blog/2017/02/05/clojure-compiler-analyze/)讲述了 Clojure 编译器工作的整体流程，主要涉及 LispReader 与 Compiler 这两个类，而且指出编译器并没有把 Clojure 转为相应的 Java 代码，而是直接使用 ASM 生成可运行在 JVM 中的 bytecode。本文将主要讨论 Clojure 编译成的 bytecode 如何实现动态运行时以及为什么 Clojure 程序启动慢，这会涉及到 JVM 的类加载机制。

## 类生成规则

JVM 设计之初只是为 Java 语言考虑，所以最基本的概念是 class，除了八种基本类型，其他都是对象。Clojure 作为一本函数式编程语言，最基本的概念是函数，没有类的概念，那么 Clojure 代码生成以类为主的 bytecode 呢？

一种直观的想法是，每个命名空间（namespace）是一个类，命名空间里的函数相当于类的成员函数。但仔细想想会有如下问题：

1. 在 REPL 里面，可以动态添加、修改函数，如果一个命名空间相当于一个类，那么这个类会被反复加载
2. 由于函数和字符串一样是一等成员，这意味这函数既可以作为参数、也可以作为返回值，如果函数作为类的方法，是无法实现的

上述问题 2 就要求必须将函数编译成一个类。根据 [Clojure 官方文档](https://clojure.org/reference/compilation)，对应关系是这样的：

- 函数生成一个类
- 每个文件（相当于一个命名空间）生成一个`<filename>__init` 的加载类
- `gen-class` 生成固定名字的类，方便与 Java 交互
- `defrecord`、`deftype`生成同名的类，`proxy`、`reify`生成匿名的类

需要明确一点，只有在 AOT 编译时，Clojure 才会在本地生成 `.class` 文件，其他情况下生成的类均在内存中。

## 动态运行时

明确了 Clojure 类生成规则后，下面介绍 Clojure 是如何实现动态运行时。这一问题将分为 AOT 编译与 DynamicClassLoader 类的实现两部分。

### AOT 编译

![](https://img.alicdn.com/imgextra/i3/581166664/TB26GwHd4xmpuFjSZFNXXXrRXXa_!!581166664.png)
```
$ cat src/how_clojure_work/core.clj

(ns how-clojure-work.core)

(defn -main [& _]
 (println "Hello, World!"))

```
使用 `lein compile` 编译这个文件，会在`*compile-path*`指定的文件夹（一般是项目的`target`）下生成如下文件：

```
$ ls target/classes/how_clojure_work/

core$fn__38.class
core$loading__5569__auto____36.class
core$main.class
core__init.class
```
`core$main.class`与`core__init.class`分别表示原文件的`main`函数与命名空间加载类，那么剩下两个类是从那里来的呢？

我们知道 Clojure 里面很多“函数”其实是用宏实现的，宏在编译时会进行展开，生成新代码，上面代码中的`ns`、`defn`都是宏，展开后（在 Cider + Emacs 开发环境下，`C-c  M-m`）可得
```
(do
  (in-ns 'how-clojure-work.core)
  ((fn*
     loading__5569__auto__
     ([]
       (. clojure.lang.Var
        (clojure.core/pushThreadBindings
          {clojure.lang.Compiler/LOADER
           (. (. loading__5569__auto__ getClass) getClassLoader)}))
       (try
         (refer 'clojure.core)
         (finally
           (. clojure.lang.Var (clojure.core/popThreadBindings)))))))
  (if (. 'how-clojure-work.core equals 'clojure.core)
    nil
    (do
      (. clojure.lang.LockingTransaction
       (clojure.core/runInTransaction
         (fn*
           ([]
             (commute
               (deref #'clojure.core/*loaded-libs*)
               conj
               'how-clojure-work.core)))))
      nil)))

(def main (fn* ([& _] (println "Hello, World!"))))      
```
可以看到，`ns`展开后的代码里面包含了两个匿名函数，对应本地上剩余的两个文件。下面依次分析这四个`class`文件

#### core__init

```
$ javap core__init.class
public class how_clojure_work.core__init {
  public static final clojure.lang.Var const__0;
  public static final clojure.lang.AFn const__1;
  public static final clojure.lang.AFn const__2;
  public static final clojure.lang.Var const__3;
  public static final clojure.lang.AFn const__11;
  public static void load();
  public static void __init0();
  public static {};
}
```

> Clojure 里面所有的函数都继承 [IFn 接口](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/IFn.java)，该接口有 20 个重载的 invoke 方法，之所以有这么多 invoke 方法，是因为 [JVM 擅长根据参数数目进行方法调度（dispatch）](http://stackoverflow.com/a/2736636/2163429)。
[抽象类 AFn](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/AFn.java) 为 IFn 里的 20 个 invoke 方法提供了的默认实现（通过抛 throwArity 异常），这样其他函数就只需要继承 AFn 并重写相应 invoke 方法即可。

可以看到，命名空间加载类里面有一些`Var`与`AFn`变量，可以认为一个`Var`对应一个`AFn`。使用 Intellj 或 [JD](http://jd.benow.ca/) 打开这个类文件，首先查看静态代码快。
```
static {
    __init0();
    Compiler.pushNSandLoader(RT.classForName("how_clojure_work.core__init").getClassLoader());
    try {
        load();
    } catch (Throwable var1) {
        Var.popThreadBindings();
        throw var1;
    }
    Var.popThreadBindings();
}
```
这里面会先调用`__init0`：
```
public static void __init0() {
    const__0 = (Var)RT.var("clojure.core", "in-ns");
    const__1 = (AFn)Symbol.intern((String)null, "how-clojure-work.core");
    const__2 = (AFn)Symbol.intern((String)null, "clojure.core");
    const__3 = (Var)RT.var("how-clojure-work.core", "main");
    const__11 = (AFn)RT.map(new Object[] {
        RT.keyword((String)null, "arglists"), PersistentList.create(Arrays.asList(new Object[] {
            Tuple.create(Symbol.intern((String)null, "&"),
            Symbol.intern((String)null, "_"))
        })),
        RT.keyword((String)null, "line"), Integer.valueOf(3),
        RT.keyword((String)null, "column"), Integer.valueOf(1),
        RT.keyword((String)null, "file"), "how_clojure_work/core.clj"
    });
}
```
`RT` 是 Clojure runtime 的实现，在`__init0`里面会对命名空间里面出现的 var 进行赋值。

接下来是`pushNSandLoader`（内部用`pushThreadBindings`实现），它与后面的 `popThreadBindings` 形成一个 binding，功能等价下面的代码：
```
(binding [clojure.core/*ns* nil
          clojure.core/*fn-loader* RT.classForName("how_clojure_work.core__init").getClassLoader()
          clojure.core/*read-eval true]
  (load))
```
接着查看`load`的实现：
```
public static void load() {
    // 调用 in-ns，传入参数 how-clojure-work.core
    ((IFn)const__0.getRawRoot()).invoke(const__1);
    // 执行 loading__5569__auto____36，功能等价于 (refer clojure.core)
    ((IFn)(new loading__5569__auto____36())).invoke();
    Object var10002;
    // 如果当前的命名空间不是 clojure.core 那么会在一个 LockingTransaction 里执行 fn__38
    // 功能等价与(commute (deref #'clojure.core/*loaded-libs*) conj 'how-clojure-work.core)
    if(((Symbol)const__1).equals(const__2)) {
        var10002 = null;
    } else {
        LockingTransaction.runInTransaction((Callable)(new fn__38()));
        var10002 = null;
    }

    Var var10003 = const__3;
    // 为 main 设置元信息，包括行号、列号等
    const__3.setMeta((IPersistentMap)const__11);
    var10003.bindRoot(new main());
}
```
至此，命名空间加载类就分析完了。
#### loading_5569_auto____36

```
$ javap core\$loading__5569__auto____36.class
Compiled from "core.clj"
public final class how_clojure_work.core$loading__5569__auto____36 extends clojure.lang.AFunction {
  public static final clojure.lang.Var const__0;
  public static final clojure.lang.AFn const__1;
  public how_clojure_work.core$loading__5569__auto____36(); // 构造函数
  public java.lang.Object invoke();
  public static {};
}
```
与 `core__init` 类结构，包含一些 var 赋值与初始化函数，同时它还继承了`AFunction`，从名字就可以看出这是一个函数的实现。

```
// 首先是 var 赋值
public static final Var const__0 = (Var)RT.var("clojure.core", "refer");
public static final AFn const__1 = (AFn)Symbol.intern((String)null, "clojure.core");
// invoke 是方法调用时的入口函数
public Object invoke() {
    Var.pushThreadBindings((Associative)RT.mapUniqueKeys(new Object[]{Compiler.LOADER, ((Class)this.getClass()).getClassLoader()}));

    Object var1;
    try {
        var1 = ((IFn)const__0.getRawRoot()).invoke(const__1);
    } finally {
        Var.popThreadBindings();
    }

    return var1;
}
```
上面的`invoke`方法等价于
```
(binding [Compiler.LOADER (Class)this.getClass()).getClassLoader()]
  (refer 'clojure.core))
```
`fn__38`与`loading__5569__auto____36` 类似， 这里不在赘述。

#### core$main

```
$ javap  core\$main.class
Compiled from "core.clj"
public final class how_clojure_work.core$main extends clojure.lang.RestFn {
  public static final clojure.lang.Var const__0;
  public how_clojure_work.core$main();
  public static java.lang.Object invokeStatic(clojure.lang.ISeq);
  public java.lang.Object doInvoke(java.lang.Object);
  public int getRequiredArity();
  public static {};
}
```
由于`main`函数的参数数量是可变的，所以它继承了`RestFn`，除了 var 赋值外，重要的是以下两个函数：
```
public static Object invokeStatic(ISeq _) {
    // const__0 = (Var)RT.var("clojure.core", "println");
    return ((IFn)const__0.getRawRoot()).invoke("Hello, World!");
}
public Object doInvoke(Object var1) {
    ISeq var10000 = (ISeq)var1;
    var1 = null;
    return invokeStatic(var10000);
}
```

通过上面的分析，我们可以发现，每个函数在被调用时，会去调用`getRawRoot`函数得到该函数的实现，这种重定向是 Clojure 实现动态运行时非常重要一措施。这种重定向在开发时非常方便，可以用 [nrepl](https://github.com/clojure/tools.nrepl) 连接到正在运行的 Clojure 程序，动态修改程序的行为，无需重启。
但是在正式的生产环境，这种重定向对性能有影响，而且也没有重复定义函数的必要，所以可以在服务启动时指定`-Dclojure.compiler.direct-linking=true`来避免这类重定向，官方称为 [Direct linking](https://clojure.org/reference/compilation#directlinking)。可以在定义 var 时指定`^:redef`表示必须重定向。`^:dynamic`的 var 永远采用重定向的方式确定最终值。

需要注意的是，var 重定义对那些已经 direct linking 的代码是透明的。

### DynamicClassLoader

熟悉 JVM 类加载机制（不清楚的推荐我另一篇文章[《JVM 的类初始化机制》](/blog/2014/07/12/order-of-initialization-in-java/)）的都会知道，
> 一个类只会被一个 ClassLoader 加载一次。

仅仅有上面介绍的重定向机制是无法实现动态运行时的，还需要一个灵活的 ClassLoader，可以在 REPL 做如下实验：
```
user> (defn foo [] 1)
#'user/foo
user> (.. foo getClass getClassLoader)
#object[clojure.lang.DynamicClassLoader 0x72d256 "clojure.lang.DynamicClassLoader@72d256"]
user> (defn foo [] 1)
#'user/foo
user> (.. foo getClass getClassLoader)
#object[clojure.lang.DynamicClassLoader 0x57e2068e "clojure.lang.DynamicClassLoader@57e2068e"]

```
可以看到，只要对一个函数进行了重定义，与之相关的 ClassLoader 随之也改变了。下面来看看 [DynamicClassLoader](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/DynamicClassLoader.java#L72-L82) 的核心实现：
```
// 用于存放已经加载的类
static ConcurrentHashMap<String, Reference<Class>>classCache =
        new ConcurrentHashMap<String, Reference<Class> >();

// loadClass 会在一个类第一次主动使用时被 JVM 调用
Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
	Class c = findLoadedClass(name);
	if (c == null) {
		c = findInMemoryClass(name);
		if (c == null)
			c = super.loadClass(name, false);
    }
	if (resolve)
		resolveClass(c);
	return c;
}

// 用户可以调用 defineClass 来动态生成类
// 每次调用时会先清空缓存里已加载的类
public Class defineClass(String name, byte[] bytes, Object srcForm){
	Util.clearCache(rq, classCache);
	Class c = defineClass(name, bytes, 0, bytes.length);
    classCache.put(name, new SoftReference(c,rq));
    return c;
}        
```
通过搜索 Clojure 源码，只有在 [RT.java 的 makeClassLoader 函数](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/RT.java#L2126) 里面有`new DynamicClassLoader`语句，继续通过 Intellj 的 Find Usages 发现有如下三处调用`makeClassLoader`：[Compiler/compile1](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/Compiler.java#L7455)、[Compiler/eval](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/Compiler.java#L6897)、[Compiler/load](https://github.com/clojure/clojure/blob/clojure-1.8.0/src/jvm/clojure/lang/Compiler.java#L7352)。

正如[上一篇文章](/blog/2017/02/05/clojure-compiler-analyze/#Compiler-java)的介绍，这三个方法正是 Compiler 的入口函数，这也就解释了上面 REPL 中的实验：

> 每次重定义一个函数，都会生成一个新 DynamicClassLoader 实例去加载其实现。

## 慢启动

明白了 Clojure 是如何实现动态运行时，下面分析 Clojure 程序为什么启动慢。

首先需要明确一点，[JVM 并不慢](http://stackoverflow.com/questions/2163411/is-java-really-slow)，我们可以将之前的 Hello World 打成 uberjar，运行测试下时间。
```
;; (:gen-class) 指令能够生成与命名空间同名的类
(ns how-clojure-work.core
  (:gen-class))

(defn -main [& _]
  (println "Hello, World!"))

# 为了能用 java -jar 方式运行，需要在 project.clj 中添加
# :main how-clojure-work.core
$ lein uberjar
$ time java -jar target/how-clojure-work-0.1.0-SNAPSHOT-standalone.jar
Hello, World!

real	0m0.900s
user	0m1.422s
sys	0m0.087s
```
在启动时加入`-verbose:class` 参数，可以看到很多 clojure.core 开头的类
```
...
[Loaded clojure.core$cond__GT__GT_ from file:/Users/liujiacai/codes/clojure/how-clojure-work/target/how-clojure-work-0.1.0-SNAPSHOT-standalone.jar]
[Loaded clojure.core$as__GT_ from file:/Users/liujiacai/codes/clojure/how-clojure-work/target/how-clojure-work-0.1.0-SNAPSHOT-standalone.jar]
[Loaded clojure.core$some__GT_ from file:/Users/liujiacai/codes/clojure/how-clojure-work/target/how-clojure-work-0.1.0-SNAPSHOT-standalone.jar]
[Loaded clojure.core$some__GT__GT_ from file:/Users/liujiacai/codes/clojure/how-clojure-work/target/how-clojure-work-0.1.0-SNAPSHOT-standalone.jar]
...
```
把生成的 uberjar 解压打开，可以发现 clojure.core 里面的函数都在，这些函数在程序启动时都会被加载。

<center>
![Clojure 版本 Hello World](https://img.alicdn.com/imgextra/i2/581166664/TB2Hb_NdHXlpuFjSszfXXcSGXXa_!!581166664.png)
</center>

这就是 Clojure 启动慢的原因：加载大量用不到的类。


## 总结

Clojure 作为一门 host 在 JVM 上的语言，其独特的实现方式让其拥动态的运行时的同时，方便与 Java 进行交互。当然，Clojure 还有很多可以提高的地方，比如上面的慢启动问题。另外，JVM 7 中增加了 [invokedynamic](http://docs.oracle.com/javase/7/docs/technotes/guides/vm/multiple-language-support.html) 指令，可以让运行在 JVM 上的动态语言通过实现一个 CallSite （可以认为是函数调用）的 `MethodHandle` 函数来帮助编译器找到正确的实现，这无异会提升程序的执行速度。

## 参考

- http://blog.ndk.io/clojure-compilation2.html
- http://stackoverflow.com/questions/7471316/how-does-clojure-class-reloading-work
- http://blog.headius.com/2011/10/why-clojure-doesnt-need-invokedynamic.html
- http://www.deepbluelambda.org/programming/clojure/how-clojure-works-a-simple-namespace
- https://8thlight.com/blog/aaron-lahey/2016/07/20/relationship-between-clojure-functions-symbols-vars-namespaces.html
- http://blog.cognitect.com/blog/2016/9/15/works-on-my-machine-understanding-var-bindings-and-roots
