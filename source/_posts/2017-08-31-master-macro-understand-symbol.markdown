title: 由浅入深学习 Lisp 宏之理论篇
date: 2017-08-31 22:17:52
tags: Clojure
categories: 编程语言
---

宏（macro）是 Lisp 语言中最重要的武器，它可以自动生成运行时的代码。宏也是编写领域特定语言（DSL）的利器，可以在不改动语言本身的基础上，增加新的程序构造体，这在其他语言中是不可能。比如，现在比较流行的同步方式写异步代码的 async/await，在非 Lisp 语言需要语言本身支持，但是在 Lisp 里面可以通过几个宏来解决，可以参考：[core.async](https://github.com/clojure/core.async)。

> With great power comes great responsibility.

由于宏的强大，掌握编写它的方法有较大的难度，所以社区一般会建议能不用就不要用它，我个人也比较认同这一点，但是对于一些场景用宏确实也很方便，能使程序简洁明了，所以还是有必要掌握它的，等有一定经验，就可以知道在什么场景下使用最合适了。

为了由浅入深、系统地介绍宏，打算分两篇文章来介绍，第一篇为理论篇，主要介绍 
- Symbol 数据类型，为什么需要它，以及其他非 Lisp 语言为什么没有
- 宏的本质，宏运行时期

第二篇是实战篇，介绍宏的一些常见技巧以及一些通用宏。这两篇均以 Clojure 方言为示例，但其概念原理在其他 Lisp 中都是相通的。本文为第一篇。

## Symbol 数据类型

在 Clojure 里面，除了 number，string，list，map 等常见基本数据类型外，还有一个比较特殊的 [Symbol 类型](https://clojure.org/reference/data_structures#Symbols)，定义如下：

> Symbols are identifiers that are normally used to refer to something else.

可以说 symbol 就是一些标识符，用来代指其他东西，和英文中 he/she/it 等「代词」的作用差不多。
现在编程使用的都是高级语言，其语言构造体（language's constructs）是由一些关键字与用户自定义变量组成，而这些都是 symbol，比如下面一个 Hello World 的示例：
```
(defn hello [greeting]
  (println "Hello " greeting))

(hello "world")
```
上面的 defn, hello, greeting, println 都是 symbol，用来指向其他数据类型，在进行求值（eval）时，Compiler 会计算出相应值。Clojure 里面提供了 def 这个[special form](https://clojure.org/reference/special_forms)来建立 symbol 到其他值的映射关系。例如：
```
user> (def cat "Tom")
#'user/cat
```
简单来说上面这一句把 symbol 执行了字符串`Tom`，但是由于 Clojure 里面为了实现其动态特性，真实的情况稍微复杂一些，见下图：
![](https://img.alicdn.com/imgextra/i4/581166664/TB2vBerXioaPuJjSsplXXbg7XXa_!!581166664.png)

Var 是Clojure里面提供的[四种引用类型](http://clojure-doc.org/articles/language/concurrency_and_parallelism.html#clojure-reference-types)中最常用的，支持动态作用域以及 thread-local 值。动态作用域是指函数内的自由变量的值是在运行时确定的，这里不清楚的可以参考我的另一篇文章[《编程语言中的变量作用域与闭包》](/blog/2016/05/28/scope-closure/)，这里不在赘述。

继续回到上面的图，def 会把 cat 这个 symbol 指向同名的 var，同时把 var 指向字符串 Tom（叫做 root binding）。symbol 到 var 的映射关系保存在每个 namespace 中，可以用`resolve`来查询这个映射关系：
```
user> (resolve 'cat)
#'user/cat
```
最后一点需要注意的是，symbol 在 var 的映射关系只有在用 def 定义全局 var 是才具有，使用 let, loop 定义的词法作用域（lexical context）里面的 binding 不算是变量，[一旦创建后无法修改](https://groups.google.com/forum/#!topic/clojure/PCKzXweeDeY)。可以使用 `with-local-vars` 宏来定义局部变量：
```
(with-local-vars [x 1 y 2]
  (var-set x 11)
  (+ (var-get x) (var-get y)))

;; => 13  
```

### 字面量

由上面介绍我们可以知道，Clojure 编译器在遇到 symbol 时，会对其进行求值，可以用`'`来表示其字面量

```
user> (def tom 'tom)  ;; 这里指向的值为一个 symbol 类型的 tom
#'user/tom
user> tom
tom
```
有一点非常重要，任何两个同名的 symbol 是不相等的
```
user> (identical? 'tom 'tom)
false
```
初次接触可能会有些疑惑，但也比较好理解，可以想想
> 相同名的变量，在不同地方，不同时刻具有不同的值是再正常不过的了。

而且 symbol 可以带有元数据，所以很有可能同名的 symbol 具有不同的元数据。

最后比较重要的一点，宏传入的参数都是 symbol 字面量，比如：
```
user> (def a 1)
#'user/a
user> (defmacro demo-macro [params] (println params))
#'user/demo-macro
user> (demo-macro a)
a
nil
```
可以看到这里打印的是symbol `a`，而不是数字 1。由于`demo-macro`什么也没返回，所以在打印出 a 之后输出了 nil。

### keyword

首先明确一点，这里的 keyword 不是指程序语言里面的关键字，而是一种与 symbol 相近的数据类型，为什么说相近呢？上面介绍了 symbol 是用来指向其他值的符号，keyword 也是这么一种符号，只不过其值指向自身（self-evaluation）。
```
user> :cat
:cat
user> (identical? :cat :cat)
true
```
可以看到，同名的 keyword 是同一对象，因为它的定义就说了，其值指向自身，所以它们是不能带元数据的
```
(with-meta :cat {:some-prop true})   ;; 会报错
java.lang.ClassCastException: clojure.lang.Keyword cannot be cast to clojure.lang.IObj
```
keyword 类型存在的意义，就在于很多时候我们只是像简单区分某些东西，这一点和 Java 里的枚举类型有些相似。keyword 在 Clojure 里面最常用的地方是作为 map 的 key。比如：
```
(def student {:name "张三" :birth "2010-10-10" :sex "F"})
```
有些地方也会称 keyword 为“轻量级的 string”。

## 宏的本质

由于 Lisp 采用 s-expression 作为其语法，所以天然具有 code as data 的特点，也就是说 Lisp 程序本身就是一个 Lisp 数据，可以像操作其他数据类型一样来操作程序本身，这其实就是宏做的事情。老牌 Lisp hacker [Paul Graham](http://www.paulgraham.com) 在黑客与画家一书中有[提到](/blog/2016/12/31/dev-in-clojure/#Why-Lisp)：

> Lisp 并不严格区分读取期、编译器、运行期。在编译期去运行就是宏，可以用来扩展语言。

关于这三个时期的关系，可以用下面的图来表示
![Lisp 中不同时期的交互图](https://img.alicdn.com/imgextra/i3/581166664/TB27iCQbiIRMeJjy0FbXXbnqXXa_!!581166664.png)

由于运行期主要进行的是函数的调用，结合上面 symbol 的知识可以这么定义宏

> 宏是编译期执行的函数，参数为 symbol 类型，返回由 symbol 组成的程序（也是数据）。返回值在运行时执行。

定义宏的`defmacro`本身也是个宏，可以将其展开：
```
user> (macroexpand '(defmacro demo-macro [params] params))

(do
  (defn demo-macro ([&form &env params] params))
  (. #'demo-macro (setMacro))
  #'demo-macro)
```
可以看到，Clojure 里面是调用 `setMacro` 来将宏与一般的函数分开。

### macroexpand

关于宏展开（一般不说宏调用）在整个 Clojure 程序生命周期中的位置，可以参考下图：

![Clojure 编译器工作流程](https://img.alicdn.com/imgextra/i3/581166664/TB2j7k3dZtnpuFjSZFKXXalFFXa_!!581166664.png)

如果对实现细节感兴趣，可以参考我之前的文章：[《Clojure 运行原理之编译器剖析篇》](/blog/2017/02/05/clojure-compiler-analyze/#macroexpand)。

## 总结

对于初学 Lisp 的同学，对 symbol 类型不是很清楚，究其原因是这个类型在非 Lisp 语言中是不存在的，为什么不存在呢？主要是因为它们没法像 Lisp 一样具有 code as data 的特点，有些非 Lisp 语言可能也有所谓的 symbol 类型，像 ruby，但是 DSL 在 ruby 中与 Lisp 是完全不一样的。区别可以参考[下图](https://www.slideshare.net/antoniogarrote/lisp-vs-ruby-metaprogramming-3222908)

![Metaprogramming Ruby vs Lisp](https://img.alicdn.com/imgextra/i4/581166664/TB2FQO3bnZRMeJjSspoXXcCOFXa_!!581166664.png)

> What makes Lisp macros possible, is so far still unique to Lisp, perhaps because (a) it requires those parens, or something just as bad, and (b) if you add that final increment of power, you can no longer claim to have invented a new language, but only to have designed a new dialect of Lisp ; -)
>> Paul Graham 「[What makes Lisp different](http://www.paulgraham.com/diff.html)」

## 参考

- [WORKS ON MY MACHINE: UNDERSTANDING VAR BINDINGS AND ROOTS](http://blog.cognitect.com/blog/2016/9/15/works-on-my-machine-understanding-var-bindings-and-roots)