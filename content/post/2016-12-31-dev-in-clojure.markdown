---
title: Clojure 开发那些事
date: 2016-12-31 16:49:17
categories: [编程语言]
tags: [Clojure]
---

Clojure —— 新世纪的 Lisp 方言，相信大多数同学多多少少都听过，毕竟有个杀手级应用 [Storm](http://storm.apache.org/)，但是真正去写 Clojure 的同学估计不多，国内也罕见哪个公司招 Clojure 程序员。
作为推广 Clojure 万里长城的第一步，这篇文章首先介绍为什么要使用 Lisp 开发，之后开始介绍 Clojure 语法入门，紧接着介绍 Clojure 开发环境搭建，然后介绍使用第三方库时的一些注意点，最后介绍一下常见的测试方法。本篇文章所介绍内容都是我自己实践得出，不足之处请各位 Clojurians 指出。

## Why Lisp

Lisp 语言诞生这么久了，为什么一直那么小众？原因就在于 Lisp 语言过于强大，不必也不可能像 Java 那么普及。你能要求每个人都能为 CTO 吗？
硅谷创业之父 [Paul Graham](http://www.paulgraham.com/) 在其著作[《黑客与画家》](https://book.douban.com/subject/6021440/)中极力推荐 Lisp 语言，并且讲到很多 Lisp 的特性逐渐融入到其他语言中。该书中列举了 Lisp 中 9 种新思想，依次为：

1. 条件结构 if-then-else
2. 函数也是一种数据类型
3. 递归
4. 变量的动态类型，所有变量都是指针
5. 垃圾回收机制
6. 程序由表达式组成
7. 符号类型，符合实际是一种指针，指向存储在哈希表中的字符串
8. 代码使用符号和常量组成的树形表示法
9. 无论什么时刻，整个语言都是可用。Lisp 并不真正区分读取期、编译期和运行期

前 7 种特性可以在如今较流行的编程语言找到，但最后两种是 Lisp 特有的。Lisp 最擅长的领域是写编辑器（元编程）、领域特定语言DSL，现在用的最广的是 Emacs 与 AutoACD，其对应的脚本语言分别是 [Emacs Lisp](https://en.wikipedia.org/wiki/Emacs_Lisp)、[AutoLisp](https://en.wikipedia.org/wiki/AutoLISP)。
可以好不夸张的说，软件也复杂，越适合用 Lisp。其次，Clojure 作为新世纪的 Lisp 方言，在 Web 、大数据、数据库等现在常见领域都有丰富的类库与文档。

目前国内使用 Clojure 成功案例较少，[LeanCloud](https://leancloud.cn/jobs/) 在其招聘网页上写到其成员都是 Clojure 社区成员，但并不了解其内部使用情况。国外的就比较多了，可以参考 Clojure 之父 Rich Hickey 所在公司 Congitect 列举的 [Success Stories](http://cognitect.com/resources#success-stories)。

## 语法入门

### 括号
Lisp 语法最显著的特点是“括号多”，不过这只是其外在表现，内在表现是阅读代码的方式，需要从最里面的表达式开始，比如：

```
;; Clojure
> (split (upper-case "hello, world") #", ")
["HELLO" "WORLD"]

;; Python
>>> "hello, world".upper().split(", ")
['HELLO', 'WORLD']
```

为了防止过度嵌套，需要经常定义一些辅助函数，很幸运，Clojure 里面函数是一级成员，这意味着函数可以作为参数传入，也可以作为函数值返回，能够进行这两类操作的函数称为“高阶函数”（high-order functions），这在任何一门函数式语言中都很普及。

除了最基本的圆括号`()`外，方括号`[]`与花括号`{}`在 Clojure 用的也比其他 Lisp 方言中多。

```
[1 2 "buckle my shoe"]        ;; 数组
{:ace 1, :deuce 2, "trey" 3}  ;; 哈希表
#{:a :b :c}                   ;; 集合
```

Clojure 中基本的数据结构可以参考其[官方网站](http://clojure.org/reference/data_structures)，我个人觉得，Lisp 方言的英文介绍往往过于精炼、晦涩，不适合初学者直接阅读，为了夯实基础，还是建议大家找本书来看，看书的好处是不仅仅知道某个知识点，更重要的是了解不同知识点之间的区别与联系，初学期间，我阅读了下面两本书：

- [The Joy of Clojure](https://book.douban.com/subject/4743790/)，这本书对我帮助比较大，但是网上普遍说这本书比较难懂，我只能说萝卜青菜各有所爱。
- [Clojure编程](https://book.douban.com/subject/21661495/)，这本书应该毋庸置疑是新手的必须书

除了看书外，下面的文档也非常 newbie-friendly，推荐大家多去逛逛：

- [http://clojure-doc.org/](http://clojure-doc.org/)，对 Clojure 语言的整个生态有非常详细的介绍
- [https://clojuredocs.org/](https://clojuredocs.org/)，可以方便查看具体函数的使用方法

### 数据不可变

括号问题适应后，另一个比较挑战的是数据的不可变性，这融合在 Clojure 语言的设计之中，表象就是没有赋值语句了，但在实现时，为了达到时间、空间上的高效，采用了非常复杂的算法，我到现在也还是一知半解，不是很清楚。《The Joy of Clojure》一书中有简单介绍，不过我觉得初学者可以完全不用去关心实现的细节，在遇到性能问题时在考虑去优化。我这里放一些相关的资料，有兴趣的读者可以自取：

- [Understanding Clojure's Persistent Vectors](http://hypirion.com/musings/understanding-persistent-vector-pt-1)
- [What Lies Beneath - A Deep Dive Into Clojure's Data Structures](https://www.youtube.com/watch?v=7BFF50BHPPo) YouTube 视频，需翻墙

### 托管型语言

> [Clojure is desgined to be a hosted language](http://clojure.org/about/jvm_hosted).

这一点非常重要，估计也是为什么 Clojure 较其他 Lisp 方言更流行的原因。Clojure 的宿主平台现在主要有两个：一个是 JVM；另一个是微软 .NET （[Clojure-CLR](https://github.com/clojure/clojure-clr)），现在还有一个发展迅猛的 ClojureScript，可以将 Clojure 代码编译为无处不在的 Javascript。

这也就意味我们或多或少需要了解这些宿主语言，比如 Clojure 里面没有提供直接操作文件系统、网络的类库，而是采用间接的方法去调用其宿主语言的相应类库。这一点也让 Clojure 在生产环境中使用变得可能，比如 [clj-http](https://github.com/dakrone/clj-http) 就是对 [Apache HttpComponents](http://hc.apache.org/httpcomponents-client-ga/) 的包装，更符合 Clojure 使用习惯而已。



## 开发环境搭建

工欲善其事，必先利其器。
这里主要介绍 Intellj + Cursive 与 Emacs + Cider 两个环境，这两个是我用的最顺手，也是现在较为流行的方式。

### Intellj + Cursive

在上面语法入门部分就介绍了，Clojure 与宿主语言经常需要交互，毋庸置疑 [Intellj](https://www.jetbrains.com/idea/) 是 Java 开发的利器，社区版足以满足需要，不用再去做找破解版那些不道德的事情，如果你还在用 Eclipse，可以考虑迁移了。
[Cursive](https://cursive-ide.com/) 做到了开箱即用，而且足够的好用，而且也有[非商业免费版](https://cursive-ide.com/buy.html)，这极大方便了学生党，适应了中国国情。

安装、使用比较简单，通过 Intellj 插件管理器安装后，设置下[快捷键类型](https://cursive-ide.com/userguide/keybindings.html)就可以使用了。

![Cursive 快捷键设置](https://img.alicdn.com/imgextra/i1/581166664/TB2McCFcbxmpuFjSZJiXXXauVXa_!!581166664.png)

![Cursive REPL](https://img.alicdn.com/imgextra/i2/581166664/TB2th5wcohnpuFjSZFpXXcpuXXa_!!581166664.png)

### Emacs + Cider

作为一门 Lisp 方言，怎么能没有一个好的 Emacs mode 呢？[Cider](https://github.com/clojure-emacs/cider) 全称

> The Clojure Interactive Development Environment that Rocks for Emacs

而且 Emacs 本身就是个用 Lisp 方言写的“操作系统”，对以括号著称的 Lisp 语言有天然的支持，括号匹配主要是 Paredit mode，可以方便的把括号作为一个整体操作，不过像 Cursive 这种插件也集成了 Paredit 的主要功能，所以不用 Emacs 的同学也不用担心，毕竟 Emacs 学习成本实在是太高，我个人觉得比 Vim 有过之而无不及，相对于 Vim 的模态概念，Emacs 里面通过 Ctrl 与 Meta 键来与一般按键区别，这里我们不必对某个编辑器有过多的偏见，它们都是生产力的工具而已，写好代码才是重要的。

初学者如果要尝试 Emacs 建议参考《Clojure For the Brave and True》的第二章[How to Use Emacs, an Excellent Clojure Editor](http://www.braveclojure.com/basic-emacs/)，我最初的环境也是仿照这份配置，然后一点点根据自己的需求增加的。[ .emacs.d](https://github.com/jiacai2050/conf/tree/master/.emacs.d) 是我的配置，供大家参考。

![Emacs + Cider 编程环境](https://img.alicdn.com/imgextra/i4/581166664/TB26VWrchtmpuFjSZFqXXbHFpXa_!!581166664.png)

Emacs + Cider 的组合相比 Intellj ＋ Cursive 最大的优势就是对宏的支持，Cider 提供了对宏展开的快捷键，但在 Cursive 中我没找到，不过宏也是比较高级的功能，初学者应该用不到，等到用的多的时候，就可以把 Emacs 环境熟悉起来了。

最后还是建议初学者不要用 Emacs，学习成本太大，而且很容易就把注意力转移到编辑器的学习上，等到学习了一段时间后在尝试不迟。


## 第三方类库的选择

由于 Clojure 语言定位就是个寄宿语言，所以无论是 Web 框架，还是数据库连接池，Clojure 里都有与 Java 版相对应包装类库，大家不必担心要使用某个功能，而没有相应库的问题，但是这里我必须说明一点，Clojure 类库的文档对初学者不够友好，最起码对我来说是的，我相信我不可能是个例。就拿打印日志来说，Github 上搜一下，应该能够找到最 idiomatic 应该是 [timbre](https://github.com/ptaoussanis/timbre)，通读其 README 后，怎么配置还不是很清楚，继续 Google，找到

- [log-config](https://github.com/palletops/log-config)
- [Custom logging with timbre](http://www.filmspringopen.eu/blog-entry-blogentryid-447808.html)

这时我才能够知道怎么去定制他的`appenders`等各种参数，也可能是我个人的理解能力比较差，不过这里介绍一个非常实用并且适用于所有语言的方法，那就是看这个项目的test，test 里面核心的功能肯定会涉及到，然后照猫画虎就可以了。

其实，在使用第三方类库之余，多去了解其实现，代码从 Github 上 Clone 下来，慢慢看，Clojure 里面提供了很多实用的小方法，像`partition`, `juxt`, `group-by`等等不一而足，最好带着 issue 里面的问题去看代码，说不定你就从使用者变成了开发者呢，我第一个尝试给了 [http-clj](https://github.com/dakrone/clj-http/pull/341)。

## 调试 debug

代码一次写对的几率基本为0，掌握一定的测试技能是每个同学的基本功，下面简单介绍下 Clojure里面常用的调试方法。

### println
```
(let [headers         (:headers ring-request)
      header-names    (keys headers)
      ;; The following underscore is a convention for "unused variable"
      _               (println "Headers:" header-names)  ;; <-- this
      header-keywords (map keyword header-names)]
;; etc
)
```
最简单实用的 `println`，但问题是我们需要把要监控的变量打两次，这在变量比较多的时候比较麻烦，可以采用下面的 spyscope

### spyscope

[Spyscope](https://github.com/dgrnbrg/spyscope) 库可以解决上`println`的问题，他提供三个`reader tags`来监控变量，用法极为简单：
```
(let [headers         (:headers ring-request)
      header-names    #spy/p (keys headers)       ;; <-- print out what header-names is
      header-keywords (map keyword header-names)]
;; etc
)
```

### [debux](https://github.com/philoskim/debux)

一个非常好用的测试库，可以把嵌套函数调用的每一步打印出来。

```
(dbg (-> "a b c d"
         .toUpperCase
         (.replace "A" "X")
         (.split " ")
         first))
;=> "X"
```
REPL 中会打印：
```
dbg: (-> "a b c d" .toUpperCase (.replace "A" "X") (.split " ") first)
  "a b c d" =>
    "a b c d"
  .toUpperCase =>
    "A B C D"
  (.replace "A" "X") =>
    "X B C D"
  (.split " ") =>
    ["X", "B", "C", "D"]
  first =>
    "X"
=>
  "X"
```

### tools.trace

上面介绍的方法都需要修改源代码，有没有不用修改的呢？答案是肯定的，[clojure.tools.trace](https://github.com/clojure/tools.trace)，Github 上的 README 比较详细，大家可以可以去了解，我目前在自己的项目里面还没有采用过这个方法。

### Intellj Debug

借助于 IDE 的优势，我们可以打断点，一步一步调试，但是 Cursive 对宏的支持比较有限，目前出来把宏展开外，没找到好的调试宏的好方法。
![Intellj debug](https://img.alicdn.com/imgextra/i2/581166664/TB2HEWIcb4npuFjSZFmXXXl4FXa_!!581166664.png_620x10000.jpg)

### nrepl

Clojure 的 REPL 可以连接到远程服务器上的进程中，直接对进程中的函数或变量进行修改，这是非常便利的，对于很多运行时的错误可以采用这种方式解决，Emacs 与 Intellj 里面都提供了连接远程 REPL server 的方式。

![Intellj 连接远程 REPL](https://img.alicdn.com/imgextra/i1/581166664/TB2KcGIcbBmpuFjSZFuXXaG_XXa_!!581166664.png)

Emacs 里面是：`M-x cider-connect`
lein 里面是：`lein repl :connect 192.168.50.101:4343`

## 总结

Clojure 在国内算是非常非常小众，介绍 Clojure 开发的文章也比较少，仅有的也只是一些简单的语法介绍或者概念阐述。
我从[读完 SICP](https://github.com/jiacai2050/sicp) 后就一直想把 Lisp 作为我的主力语言，正好趁着这次机会，希望能够弥补国内 Clojure 文档较匮乏的情况，之后我会陆陆续续把自己使用 Clojure 开发的经历分享出来，供后来的 Clojurians 参考，这也算是 17 年的第一个小目标吧。

![关于 Clojure 的 RSS 收集 ](https://img.alicdn.com/imgextra/i2/581166664/TB2OEGwcmVmpuFjSZFFXXcZApXa_!!581166664.png)

上面是我目前收集关于 Clojure 的 RSS，大家可以根据标题去搜索，热爱 Clojure ，从不做伸手党开始。😊

## 扩展阅读

- [A Concise Guide to Clojure](https://www.cis.upenn.edu/~matuszek/Concise%20Guides/Concise%20Clojure.html#basic_types)
- [The Beauty of Clojure](http://owenrh.me.uk/blog/2015/08/24/)
- [An In-Depth Look at Clojure Collections](https://www.infoq.com/articles/in-depth-look-clojure-collections)
- [Clojure TV on YouTube](https://www.youtube.com/channel/UCaLlzGqiPE2QRj6sSOawJRg) 里面有很多大牛分享 Clojure 实战，还能锻炼英文
- [LeanCloud 工程师庄晓丹个人博客](http://blog.fnil.net/blog/categories/clojure/)
