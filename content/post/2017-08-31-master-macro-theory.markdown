---
categories:
- 编程语言
date: 2017-08-31 22:17:52
tags:
- Clojure
title: 由浅入深学习 Lisp 宏之理论篇
---

宏（macro）是 Lisp 语言中最重要的武器，它可以自动生成运行时的代码。宏也是编写领域特定语言（DSL）的利器，可以在不改动语言本身的基础上，增加新的程序构造体，这在其他语言中是不可能。比如，现在比较流行的同步方式写异步代码的 async/await，在非 Lisp 语言需要语言本身支持，但是在 Lisp 里面可以通过几个宏来解决，可以参考：[core.async](https://github.com/clojure/core.async)。

> With great power comes great responsibility.

由于宏的强大，掌握编写它的方法有较大的难度，所以社区一般会建议能不用就不要用它，我个人也比较认同这一点，但是对于一些场景用宏确实也很方便，能使程序简洁明了，所以还是有必要掌握它的，等有一定经验，就可以知道在什么场景下使用最合适了。

为了由浅入深、系统地介绍宏，打算分两篇文章来介绍，第一篇为理论篇，主要介绍 
1. Clojure 语言中的基本语法，重点介绍 Symbol 数据类型，为什么需要它，非 Lisp 语言为什么没有
2. 宏的本质，宏运行时期

第二篇是实战篇，介绍宏的一些常见技巧以及一些通用宏。这两篇均以 Clojure 方言为示例，但其概念原理在其他 Lisp 中都是相通的。本文为第一篇。

## 基本语法

Clojure 作为一门 Lisp 方言，其语言的基本单元是表达式（expression），通过不同表达式的组合形成最终的程序。非 Lisp 语言中除了「表达式」外，还有「声明（statement）」，声明没有返回值，只会产生一些副作用，比如`int a = 1`；而每个表达式都有一个返回值，极少数表达式具有副作用。Clojure 语言中有以下表达式字面量（literals）：

```clj
;; Numeric types
42              ; Long - 64-bit integer (from -2^63 to 2^63-1)
6.022e23        ; Double - double-precision 64-bit floating point
42N             ; BigInt - arbitrary precision integer
1.0M            ; BigDecimal - arbitrary precision fixed-point decimal
22/7            ; Ratio

;; Character types
"hello"         ; String
\e              ; Character

;; Other types
nil             ; null value
true            ; Boolean (also, false)
#"[0-9]+"       ; Regular expression
:alpha          ; Keyword
:release/alpha  ; Keyword with namespace
map             ; Symbol
+               ; Symbol - most punctuation allowed
clojure.core/+  ; Namespaced symbol

;; Collection types
'(1 2 3)     ; list
[1 2 3]      ; vector
#{1 2 3}     ; set
{:a 1, :b 2} ; map
```

### 结构与语义

在 Clojure 里面，有一个非 Lisp 语言中没有的 [Symbol 类型](https://clojure.org/reference/data_structures#Symbols)，定义如下：

> Symbols are identifiers that are normally used to refer to something else.

可以说 symbol 就是一些标识符，用来代指其他东西，和英文中 he/she/it 等「代词」的作用差不多。现在大家所使用的高级语言，其语言构造体（language's constructs）是由一些关键字与用户自定义变量组成，这些都是 symbol。看下面这个表达式：
![structure-and-semantics](https://img.alicdn.com/imgextra/i3/581166664/TB2twOcjL6H8KJjSspmXXb2WXXa_!!581166664.png)

上面的绿色字标明这个表达式用到的数据结构，下面蓝色字标明这个表达式在运行时的含义。

大多数字面量进行求值（eval）时，都表示其自身，比如 `1` 就是数字 1，而 symbol 与 list 这两类则不同，它们在求值时，symbol 返回它所代指的值，list 表示函数调用。Clojure 里面提供了 def 这个[special form](https://clojure.org/reference/special_forms)来建立 symbol 到其他值的映射关系。例如：
```
user> (def cat "Tom")
#'user/cat
```
简单来说上面这一句把 symbol 字面量`cat`指向了字符串`Tom`，但是由于 Clojure 里面为了实现其动态特性，真实的情况稍微复杂一些，见下图：
![](https://img.alicdn.com/imgextra/i4/581166664/TB2vBerXioaPuJjSsplXXbg7XXa_!!581166664.png)

Var 是Clojure里面提供的[四种引用类型](http://clojure-doc.org/articles/language/concurrency_and_parallelism.html#clojure-reference-types)中最常用的，支持动态作用域以及 thread-local 值。动态作用域是指函数内的自由变量的值是在运行时确定的，这里不清楚的可以参考我的另一篇文章[《编程语言中的变量作用域与闭包》](/blog/2016/05/28/scope-closure/)，这里不在赘述。

继续回到上面的图，def 会把 cat 这个 symbol 指向同名的 var，同时把 var 指向字符串 Tom（叫做 root binding）。symbol 到 var 的映射关系保存在每个 namespace 中，可以用`resolve`来查询这个映射关系：
```
user> (resolve 'cat)
#'user/cat
```
最后一点需要注意的是，symbol 到 var 的映射关系只有在用 def（或其变体defn/defmacro） 定义时才具有，使用 let, loop 等定义的词法作用域（lexical context）里面的 binding 称为 [locals](https://groups.google.com/forum/#!topic/clojure/FLrtjyYJdRU)，没有这种映射关系，[locals 一旦创建后无法修改](https://groups.google.com/forum/#!topic/clojure/PCKzXweeDeY)。可以使用 `with-local-vars`（很少用到）宏来定义局部变量：
```
(with-local-vars [x 1 y 2]
  (var-set x 11)
  (+ (var-get x) (var-get y)))

;; => 13  
```

## quote

由上面介绍我们知道，symbol 与 list 这两类字面量在求值时有特殊的处理方式，但在一些时间，不希望进行这种特殊处理，就希望 symbol 返回一个 symbol，list 不在表示函数调用，这时候就可以使用 `quote`（一般使用简化形式`'`） 来实现：

```
user=> (quote x)
x
user=> 'x
x
user=> '(1 2 3)
(1 2 3)
```
一个常见的错误就是误把都是数据的 list 作为 code 去执行了：
```
user=> (1 2 3)
ClassCastException java.lang.Long cannot be cast to clojure.lang.IFn
```
quote 在写宏时非常重要，我们这里只需要知道宏传入的参数都是 symbol 字面量即可，实战篇会详细介绍如何使用。下面仅举一例作为说明：
```
user> (def a 1)
#'user/a
user> (defmacro demo-macro [params] (println params))
#'user/demo-macro
user> (demo-macro a)
a
nil
```
可以看到这里打印的是 symbol 字面量 `a`，而不是数字 1。由于`demo-macro`什么也没返回，所以在打印出 a 之后输出了 nil。

## 宏的本质

由于 Lisp 采用 S-表达式（s-expression）作为其语言的构造体，所以天然具有 code as data 的特点，也就是说 Lisp 程序本身就是一个标准的 Lisp 数据结构，可以像操作其他数据类型一样来操作程序本身，这其实就是宏做的事情。老牌 Lisp hacker [Paul Graham](http://www.paulgraham.com) 在黑客与画家一书中有[提到](/blog/2016/12/31/dev-in-clojure/#Why-Lisp)：

> Lisp 并不严格区分读取期、编译器、运行期。在编译期去运行就是宏，可以用来扩展语言。

关于这三个时期的关系，可以用下面的图来表示
![Lisp 中不同时期的交互图](https://img.alicdn.com/imgextra/i3/581166664/TB27iCQbiIRMeJjy0FbXXbnqXXa_!!581166664.png)

由于运行期主要进行的是函数的调用，结合上面 symbol 的知识可以这么定义宏

> 宏是编译期执行的函数，参数的类型是 symbol，返回值 symbol 数据结构（也是code）。返回值在运行时执行。

定义宏的`defmacro`本身也是个宏，可以将其展开：
```
user> (macroexpand '(defmacro demo-macro [params] params))

(do
  (defn demo-macro ([&form &env params] params))
  (. #'demo-macro (setMacro))
  #'demo-macro)
```
可以看到，Clojure 里面是调用 `setMacro` 来将宏与一般的函数分开。

## 求值过程

### Java

Clojure 语言本身 hosted 在 JVM 上，所以先看下 Java 是如何求值的：

![Java 求值过程](https://img.alicdn.com/imgextra/i4/581166664/TB2vuFjjN6I8KJjSszfXXaZVXXa_!!581166664.png)

在 Java 中，源代码（.java 文件）以字符流（characters）的形式被编译器（javac）处理，输出的 .class 文件包含了可以在 JVM 运行的 bytecode。

### Clojure

![Clojure 求值过程](https://img.alicdn.com/imgextra/i2/581166664/TB25GXJcQfb_uJkHFrdXXX2IVXa_!!581166664.png)

在 Clojure 中，源代码首先以字符流的形式被 Reader 处理，输出以 Clojure 数据结构表示的 code，之后编译器读入这些数据结构，输出 bytecode。

这里有非常重要的两点：

1. Clojure 的源代码的基本单元是表达式，而不是源文件。这里的源文件可以是存在于磁盘上的 `.clj` 文件或 REPL。源文件被转化为一系列 表达式 后才被编译器处理
2. 区分 Reader 与 Compiler 这两个过程是「宏」的基础，宏接受 Reader 处理后的code（也是数据），输出供 Compiler 执行的 code（也是数据）

具体实现细节可以参考[《Clojure 运行原理之编译器剖析篇》](/blog/2017/02/05/clojure-compiler-analyze/#macroexpand)：

![Clojure 编译器工作流程](https://img.alicdn.com/imgextra/i3/581166664/TB2j7k3dZtnpuFjSZFKXXalFFXa_!!581166664.png)

## 总结

对于初学 Lisp 的同学，对 symbol 类型不是很清楚，究其原因是这个类型在非 Lisp 语言中是不存在的，为什么不存在呢？主要是因为它们没法像 Lisp 一样具有 code as data 的特点，有些非 Lisp 语言可能也有所谓的 symbol 类型，像 ruby，但是其用法却与 Lisp 完全不同。区别可以参考[下图](https://www.slideshare.net/antoniogarrote/lisp-vs-ruby-metaprogramming-3222908)

![Metaprogramming Ruby vs Lisp](https://img.alicdn.com/imgextra/i4/581166664/TB2FQO3bnZRMeJjSspoXXcCOFXa_!!581166664.png)

> What makes Lisp macros possible, is so far still unique to Lisp, perhaps because (a) it requires those parens, or something just as bad, and (b) if you add that final increment of power, you can no longer claim to have invented a new language, but only to have designed a new dialect of Lisp ; -)
>> Paul Graham 「[What makes Lisp different](http://www.paulgraham.com/diff.html)」

## 参考


- [Learn Clojure - Syntax](https://clojure.org/guides/learn/syntax#_structure_vs_semantics)
- [WORKS ON MY MACHINE: UNDERSTANDING VAR BINDINGS AND ROOTS](http://blog.cognitect.com/blog/2016/9/15/works-on-my-machine-understanding-var-bindings-and-roots)
