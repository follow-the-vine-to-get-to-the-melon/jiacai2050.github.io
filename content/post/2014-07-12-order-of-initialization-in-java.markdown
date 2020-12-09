---
categories:
- 编程语言
date: 2014-07-12 13:02:29 +0800
tags:
- Java
title: JVM 的类初始化机制
---

当你在 Java 程序中`new`对象时，有没有考虑过 JVM 是如何把静态的字节码（byte code）转化为运行时对象的呢，这个问题看似简单，但里面的细节很多，而且由于开发者在平时与之打交道较少，很少有同学会去主动探索这块知识，但这个知识点却是面试时常考的地方，而且熟练掌握类加载是实现代码热部署的关键。

本文将结合几个具体案例，来阐述 JVM 类初始化这个问题，希望引起大家对这个知识点的注意。

## 什么是类的加载

通俗来讲，类的加载就是指将 .class 文件中的字节码读入内存，将其放在运行时数据区的方法区（method code）内，最终在堆区（heap）中创建一个 java.lang.Class 对象。

![JVM 内部结构](https://img.alicdn.com/imgextra/i3/581166664/TB2iQhEcYFlpuFjy0FgXXbRBVXa_!!581166664.png)

Class 对象封装了类在方法区内的数据结构，并且向提供了访问方法区内的数据结构的接口。

## 何时进行类加载

一般来说，只有在**第一次** **主动调用** 某个类时才会去进行类加载。如果一个类有父类，会先去加载其父类，然后再加载其自身。

上面这段话有两个关键词：**第一次** 与 **主动调用**。**第一次** 是说只在第一次时才会有初始化过程，以后就不需要了，可以理解为每个类 **有且仅有一次** 初始化的机会。那么什么是 **主动调用** 呢？
JVM 规定了以下六种情况为 **主动调用**，其余的皆为 **被动调用**：

1. 一个类的实例被创建（`new`操作、反射、`cloning`，反序列化）
2. 调用类的`static`方法
3. 使用或对类/接口的`static`属性进行赋值时（这不包括`final`的与在编译期确定的常量表达式）
4. 当调用 API 中的某些反射方法时
5. 子类被初始化
6. 被设定为 JVM 启动时的启动类（具有`main`方法的类）

关于主动加载与被动加载的区别，可以参考下面这个例子：

```java
class NewParent {

    static int hoursOfSleep = (int) (Math.random() * 3.0);

    static {
        System.out.println("NewParent was initialized.");
    }
}

class NewbornBaby extends NewParent {

    static int hoursOfCrying = 6 + (int) (Math.random() * 2.0);

    static {
        System.out.println("NewbornBaby was initialized.");
    }
}

public class ActiveUsageDemo {

    // Invoking main() is an active use of ActiveUsageDemo
    public static void main(String[] args) {

        // Using hoursOfSleep is an active use of NewParent,
        // but a passive use of NewbornBaby
        System.out.println(NewbornBaby.hoursOfSleep);
    }

    static {
        System.out.println("ActiveUsageDemo was initialized.");
    }
}
```
上面的程序最终输出：
```
ActiveUsageDemo was initialized.
NewParent was initialized.
1
```
之所以没有输出`NewbornBaby was initialized.`是因为没有主动去调用`NewbornBaby`，如果把打印的内容改为`NewbornBaby.hoursOfCrying` 那么这时就是主动调用`NewbornBaby`了，相应的语句也会打印出来。



## 类加载的生命周期

JVM 将字节码转化为运行时对象分为三个阶段，分别是：loading 、Linking、initialization。

![The beginning of a class's lifetime](https://img.alicdn.com/imgextra/i1/581166664/TB2kGtOc88lpuFjy0FnXXcZyXXa_!!581166664.gif)

下面分别介绍这三个过程：

### Loading

Loading 过程主要工作是由`ClassLoader`完成。该过程具体包括三件事：

1. 根据类的全名，生成一份二进制字节码来表示该类
2. 将二进制的字节码解析成[方法区](http://www.artima.com/insidejvm/ed2/jvm5.html)对应的数据结构
3. 最后生成一 `Class` 对象的实例来表示该类

![ClassLoader 继承关系，不同 CL 负责加载不同类](https://img.alicdn.com/imgextra/i2/581166664/TB2HtNyc4dkpuFjy0FbXXaNnpXa_!!581166664.gif)

JVM 中除了最顶层的`Boostrap ClassLoader`是用 C/C++ 实现外，其余类加载器均由 Java 实现，我们可以用`getClassLoader`方法来获取当前类的类加载器：
```java
public class ClassLoaderDemo {
    public static void main(String[] args) {
        System.out.println(ClassLoaderDemo.class.getClassLoader());
    }
}

# sun.misc.Launcher$AppClassLoader@30a4effe
# AppClassLoader 也就是上图中的 System Class Loader
```
此外，我们在启动`java`传入`-verbose:class`来查看加载的类有那些。
```
java -verbose:class ClassLoaderDemo

[Opened /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Object from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.io.Serializable from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Comparable from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.CharSequence from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]

....
....

[Loaded java.security.BasicPermissionCollection from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded ClassLoaderDemo from file:/Users/liujiacai/codes/IdeaProjects/mysql-test/target/classes/]
[Loaded sun.launcher.LauncherHelper$FXHelper from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Class$MethodArray from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Void from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
sun.misc.Launcher$AppClassLoader@2a139a55
[Loaded java.lang.Shutdown from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Shutdown$Lock from /Library/Java/JavaVirtualMachines/jdk1.8.0_112.jdk/Contents/Home/jre/lib/rt.jar]
```

ClassLoader 还具有一重要特性：双亲委派模型。具体来说就是：

> 如果一个类加载器收到了类加载的请求，它首先不会自己去尝试加载这个类，而是把请求委托给父加载器去完成，依次向上，因此，所有的类加载请求最终都应该被传递到顶层的启动类加载器中，只有当父加载器在它的搜索范围中没有找到所需的类时，即无法完成该加载，子加载器才会尝试自己去加载该类。




### Linking

#### Verification

`Verification` 主要是保证类符合 Java 语法规范，确保不会影响 JVM 的运行。包括但不限于以下事项：

- bytecode 的完整性（integrity）
- 检查`final`类没有被继承，`final`方法没有被覆盖
- 确保没有不兼容的方法签名

#### Preparation

在这个阶段，JVM 会为 **类成员变量**（不包括实例变量）分配内存空间并且赋予默认初始值，需要注意的是这个阶段不会执行任何代码，而只是根据`变量类型`决定初始值。如果不进行默认初始化，分配的空间的值是随机的，有点类型c语言中的[野指针](http://zh.wikipedia.org/zh/%E8%BF%B7%E9%80%94%E6%8C%87%E9%92%88)问题。
```
Type	Initial Value
int	0
long	0L
short	(short) 0
char	'\u0000'
byte	(byte) 0
boolean	false
reference	null
float	0.0f
double	0.0d
```

另一个需要注意的是实例
在这个阶段，JVM 也可能会为有助于提高程序性能的数据结构分配内存，常见的一个称为`method table`的数据结构，它包含了指向所有类方法（也包括也从父类继承的方法）的指针，这样再调用父类方法时就不用再去搜索了。

#### Resolution

`Resolution` 阶段主要工作是确认类、接口、属性和方法在类`run-time constant pool`的位置，并且把这些符号引用（symbolic references）替换为直接引用（direct references）。

> locating classes, interfaces, fields, and methods referenced symbolically from a type's constant pool, and replacing those symbolic references with direct references.

这个过程不是必须的，也可以发生在第一次使用某个符号引用时。

### Initialization

经过了上面的`load`、`link`后，就到了 `Initialization`。这个阶段会去真正执行代码，具体包括：代码块（static与static）、构造函数、变量显式赋值。

这些代码执行的顺序遵循以下两个原则：

1. 有static先初始化static，然后是非static的
2. 显式初始化，构造块初始化，最后调用构造函数进行初始化


## 示例

### 属性在不同时期的赋值

```java
class Singleton {

    private static Singleton mInstance = new Singleton();// 位置1
    public static int counter1;
    public static int counter2 = 0;

//    private static Singleton mInstance = new Singleton();// 位置2

    private Singleton() {
        counter1++;
        counter2++;
    }

    public static Singleton getInstantce() {
        return mInstance;
    }
}

public class InitDemo {

    public static void main(String[] args) {

        Singleton singleton = Singleton.getInstantce();
        System.out.println("counter1: " + singleton.counter1);
        System.out.println("counter2: " + singleton.counter2);
    }
}
```
当`mInstance`在位置1时，打印出
```
counter1: 1
counter2: 0
```
当`mInstance`在位置2时，打印出
```
counter1: 1
counter2: 1
```
`Singleton`中的三个属性在`Preparation`阶段会根据类型赋予默认值，在`Initialization`阶段会根据显示赋值的表达式再次进行赋值（按顺序自上而下执行）。根据这两点，就不难理解上面的结果了。

### 首次主动调用才会初始化

```java
public class Alibaba {

    public static int k = 0;
    public static Alibaba t1 = new Alibaba("t1");
    public static Alibaba t2 = new Alibaba("t2");
    public static int i = print("i");
    public static int n = 99;
    private int a = 0;
    public int j = print("j");
    {
        print("构造块");
    }
    static {
        print("静态块");
    }

    public Alibaba(String str) {
        System.out.println((++k) + ":" + str + "   i=" + i + "    n=" + n);
        ++i;
        ++n;
    }

    public static int print(String str) {
        System.out.println((++k) + ":" + str + "   i=" + i + "    n=" + n);
        ++n;
        return ++i;
    }

    public static void main(String args[]) {
        Alibaba t = new Alibaba("init");
    }
}
```

上面这个例子是阿里巴巴在14年的校招附加题，我当时看到这个题，就觉得与阿里无缘了。囧

```
1:j   i=0    n=0
2:构造块   i=1    n=1
3:t1   i=2    n=2
4:j   i=3    n=3
5:构造块   i=4    n=4
6:t2   i=5    n=5
7:i   i=6    n=6
8:静态块   i=7    n=99
9:j   i=8    n=100
10:构造块   i=9    n=101
11:init   i=10    n=102
```

上面是程序的输出结果，下面我来一行行分析之。

1. 由于`Alibaba`是 JVM 的启动类，属于主动调用，所以会依此进行 loading、linking、initialization 三个过程。
2. 经过 loading与 linking 阶段后，所有的属性都有了默认值，然后进入最后的 initialization 阶段。
3. 在 initialization 阶段，先对 static 属性赋值，然后在非 static 的。`k` 第一个显式赋值为 0 。
4. 接下来是`t1`属性，由于这时`Alibaba`这个类已经处于 initialization 阶段，static 变量无需再次初始化了，所以忽略 static 属性的赋值，只对非 static 的属性进行赋值，所有有了开始的：

        1:j   i=0    n=0
        2:构造块   i=1    n=1
        3:t1   i=2    n=2

5. 接着对`t2`进行赋值，过程与t1相同

        4:j   i=3    n=3
        5:构造块   i=4    n=4
        6:t2   i=5    n=5

6. 之后到了 static 的 `i` 与 `n`：

        7:i   i=6    n=6

7. 到现在为止，所有的static的成员变量已经赋值完成，接下来就到了 static 代码块

        8:静态块   i=7    n=99

8. 至此，所有的 static 部分赋值完毕，接下来是非 static 的 `j`

        9:j   i=8    n=100

9. 所有属性都赋值完毕，最后是构造块与构造函数

        10:构造块   i=9    n=101
        11:init   i=10    n=102

经过上面这9步，`Alibaba`这个类的初始化过程就算完成了。这里面比较容易出错的是第3步，认为会再次初始化 static 变量或代码块。而实际上是没必要，否则会出现多次初始化的情况。

希望大家能多思考思考这个例子的结果，加深 JVM 初始化类过程的理解。

## 总结

经过最后这三个例子，相信大家对 JVM 的类加载机制都有了更深的理解，如果大家还是有疑问，欢迎留言讨论。

## 参考

- [Java Virtual Machine Specification Chapter 5](https://docs.oracle.com/javase/specs/jvms/se7/html/jvms-5.html)
- [Chapter 7 of Inside the Java Virtual Machine](http://www.artima.com/insidejvm/ed2/lifetypeP.html)
- [JVM Internals](http://blog.jamesdbloom.com/JVMInternals.html)
- [What kind of method is Constructor, static or non static?](https://www.quora.com/What-kind-of-method-is-Constructor-static-or-non-static)
- [Understanding the Java ClassLoader](http://www.ibm.com/developerworks/java/tutorials/j-classloader/j-classloader.html)

## 更新日志

- 2014-07-12, 根据校招经验，完成[初稿](https://github.com/jiacai2050/jiacai2050.github.io/blob/c7a3e971d8906841eb2ac8b592ea2453d3ad2533/source/_posts/2014-07-12-order-of-initialization-in-java.markdown)，很多地方没写清楚
- 2017-01-15，全部重写，[增加 Load、Link、Initialization 过程与三个示例](https://github.com/jiacai2050/jiacai2050.github.io/blob/c9f20af48feec16904c666b87f5cc44b3408b765/source/_posts/2014-07-12-order-of-initialization-in-java.markdown)
- 2018-03-30，调整示例代码，增加「什么是类的加载」、「双亲委托模式」两小节
-------
