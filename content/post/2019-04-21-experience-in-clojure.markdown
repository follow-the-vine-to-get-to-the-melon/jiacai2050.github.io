---
categories:
- 编程语言
date: 2019-04-21 13:10:52
tags:
- Clojure
title: Clojure 开发经验总结
---

大概在两年半前，我开始陆陆续续写了[一系列文章](/tags/Clojure/)，来介绍如何上手、深入 Clojure，后来有幸加入 LeanCloud 写了两年的 Clojure，期间制作了一套[七集的教学视频](https://github.com/jiacai2050/learn_clojure.mp4)，算是对这门语言有了较为全面的认识。
鉴于国内 Clojure 普及程度很低，我觉得有必要把这些年的经验整理出来，可能会有些片面，但贵在真实，希望我的这些实战经验能帮助到后面 Clojure 的学习者。

工欲善其事，必先利其器。首先，会介绍如何打造高效实用的集成开发环境（IDE）；接着会介绍 Clojure 语言特性隐藏的一些坑；之后就如何长期维护 Clojure 项目提供一些思路；然后会介绍 Clojure 社区中一些重量级的人物，通过阅读他们的代码可以极大增强自己的内功；最后想谈下对国内 Clojure 找工作的个人见解。

## IDE

在 [Clojure 开发那些事](/blog/2016/12/31/dev-in-clojure) 中，介绍了开发 Clojure 的两种组合，即 IDEA+Cursive 与 Emacs+Cider。我一直用的是 Emacs 这一组合，在编写与 Java 交互比较多的情况下，会去采用 IDEA 方案。

关于编辑器之争，这里没必要讨论，适合自己的才是最好的，都是工具而已，写出优雅的代码才是目的。这里仅仅分享个人使用 Emacs 的一些小心得。

### Emacs

Emacs 是起源最早的编辑器之一。有人说它是伪装成编辑器的操作系统，我当初怀揣着试试看的心理，反反复复用了几次，但基本上都无疾而终，相比于 VSCode 之类开箱即用的编辑器， Emacs 确实很不友好。后来才知道，入门 Emacs，最好的方式是先用前辈们的配置文件，然后逐渐去适应、学习。
这个过程比较痛苦，我大概持续了一周左右，即使到了今天，也还是有可能陶醉在配置文件的修改中，一改就是3、4个小时，因为它的配置文件就是 Elisp 代码，随着使用程度的增加，这些代码会变得比较复杂，所以隔一段时间，我就会重新整理一下，寻找最佳的管理方式。

- https://github.com/flyingmachine/emacs-for-clojure 这是我最初参考的配置
- https://github.com/jiacai2050/dotfiles/tree/master/.emacs.d 这是我目前的配置

建议感兴趣的同学专门拿出两天来学习 Emacs 一些基本操作，然后强迫自己在日常工作中使用它，这样应该能很快上手，一旦习惯了，基本上就离不开了，我目前除了 Java 用 IDEA 开发外，其余的 go/python/js/rust 等都用 Emacs 搞定。喜欢折腾的同学不要错过！
下面介绍两个 Emacs 中杀手锏：
- [Magit, A Git Porcelain inside Emacs](https://magit.vc/) 深度与 Emacs 整合的 git 客户端，非常好用
- [Org mode](https://orgmode.org/) 一个强大的标记语言，完虐 markdown

最后，国内的 Emacs 社区也是非常推荐，经常会有精彩的讨论，各种使用问题都可以在上面找到答案
- https://emacs-china.org/

### Cider + Lein

Cider 全称是 The Clojure Interactive Development Environment that Rocks for Emacs

参考 flyingmachine 的配置，能把 cider+lein 跑起来，在使用过程中，我逐渐总结出一套“最佳实践”，供大家参考：
1. 慎重升级。每次升级 cider，我都会[或多或少遇到些问题](https://github.com/clojure-emacs/cider/issues?utf8=%E2%9C%93&q=is%3Aissue+commenter%3Ajiacai2050+)，这很烦人，尤其是你要开始干活的时候，IDE 突然坏了，于是乎你不得不停下手中的活，来修复它。虽然社区反应还算快，但还是挺影响效率的。
2. [lein](https://github.com/technomancy/leiningen) 作为 Clojure 默认的项目管理工具，已够用，不需要再去折腾 [boot-clj](https://github.com/boot-clj/boot)
   - [Checkout Dependencies](https://github.com/technomancy/leiningen/blob/master/doc/TUTORIAL.md#checkout-dependencies) 多项目开发时必备的技巧，可以快速定位依赖的源码。项目目录大概是这样子的：

  ```
.
|-- project.clj
|-- README.md
|-- checkouts
|   `-- suchwow [link to ~/code/oss/suchwow]
|   `-- commons [link to ~/code/company/commons]
|-- src
|   `-- my_stuff
|       `-- core.clj
`-- test
    `-- my_stuff
        `-- core_test.clj

   ```
3. Clojure REPL 启动很慢，所以正确的姿势是启动一个 REPL 后，不去关闭它，一直在里面去调试代码，有下面几个 plugin 使用的推荐：
   - [lein-shorthand](https://github.com/palletops/lein-shorthand) + [alembic](https://github.com/pallet/alembic) 可以在已启动的 REPL 中动态添加新依赖，不需要重启，必备！
   - [scope-capture](https://github.com/vvvvalvalval/scope-capture) 让 REPL 开发、测试流程如丝般柔滑！
   - [profiles.clj](https://github.com/jiacai2050/dotfiles/blob/master/.lein/profiles.clj) 是我目前的配置，供参考
   - REPL 启动久了，难免变得比较“脏”，对于改动较多的情况，在正式 push 到 remote 前，建议重启 REPL 测试

## Clojure 踩雷区

每门语言都会过度宣扬自己的长处，而刻意回避自己不擅长的地方，这无可厚非。这一小节就会介绍下 Clojure 中容易出问题的几个地方：

### Lazy

[惰性](https://clojure.org/reference/lazy)是 Clojure 语言的一重要特性，按需求值，看起来很美好，但是用起来坑缺很多。
首先就是官方文档里介绍的 [Don’t hang (onto) your head](https://clojure.org/reference/lazy#_dont_hang_onto_your_head)，类似的变种还有 [lazy-seq + concat](https://stuartsierra.com/2015/04/26/clojure-donts-concat) 的组合，非常容易写出看似优雅、实则暗藏 bug 的代码，到现在我都必须非常小心的使用它们，并且不能完全保证没有错误。

另一个是与动态变量结合时，比如

```clojure
(def *some-predict* true)

(def do-somework [exercises]
  (binding [*some-predict* false]
    (map (fn [x] (do-with x))
         exercises)))
```
由于 map 是惰性求值的，导致 do-somework 在返回后还没有真正求值（realize），导致没有用到函数内 binding 的值。

### 动态变量

动态变量解决的问题就是在不改变函数签名（主要是参数）的情况下，改变函数的行为。但用好它并不容易，除了上面提及的与 lazy 整合的问题，还要注意，其 binding 的值是不能跨线程的，为了解决这个问题，Clojure 1.3 版本提出了 [binding conveyance](https://github.com/clojure/clojure/blob/master/changes.md#234-binding-conveyance)，但仅仅对 Clojure 自身的线程池有效，然后又增加了 [bound-fn](https://clojuredocs.org/clojure.core/bound-fn) 来解决这个问题。可以参考下面的例子：

```clojure
(def ^:dynamic *num* 1)
(binding [*num* 2]
  (future (println *num*)))
;; 因为 binding conveyance，这里打印 "2"

(let [^ExecutorService executor (Executors/newFixedThreadPool 1)]
  (binding [*num* 2]
    (.submit executor ^Callable (fn [] (println *num*)))
    (.shutdown executor)))
;; 对于自定义线程池，这里打印 "1"

(let [^ExecutorService executor (Executors/newFixedThreadPool 1)]
  (binding [*num* 2]
    (.submit executor ^Callable (bound-fn [] (println *num*)))
    (.shutdown executor)))
;; 对于 bound-fn ，这里打印 "2"

```
更多可参考：
- https://stuartsierra.com/2013/03/29/perils-of-dynamic-scope

### nil

nil 表示无，在不同场景下有不同含义，而且 Clojure 想尽量屏蔽掉这种差异性，比如：

```clojure
user> (str nil "abc")
"abc"
user> (conj nil "abc")
("abc")
user> (assoc nil :a 1)
{:a 1}
```
但时不时 nil 就会出来咬你一口。记得之前有这么一个需求，需要对消息的格式做了升级，之前可能是 map/string，升级后只能是 string 并且用 v2 标示，处理的代码需要找出这两类消息，分别处理，代码大致如下

```clojure
(let [{v1-msgs false v2-msgs true}
      (group-by #(when (string? %)
                   (.startsWith ^String % "v2:")) msgs)])
```
可以看到，代码很简单，就是判断 msg 是不是字符串，如果是，再看看版本是不是 v2，由于 nil 与 false 是不同的值，导致会丢失一部分数据，正确的写法是这样的：
```clojure
(let [{v1-msgs false v2-msgs true}
      (group-by #(boolean (when (string? %)
                   (.startsWith ^String % "v2:"))) msgs)])
```
所以这里的一个提醒就是尽量不要让自己的函数返回 nil，而是返回空值，比如空数组、空链表、空字符串等。

### future

future 可以很方便的起一个新线程来工作，但其运行的线程池是无限制的，如果无节制的使用会导致线上服务 oom，这里推荐一个并发的库 [com.climate/claypoole](https://github.com/TheClimateCorporation/claypoole) 可以完美替换 `pmap/future/run!` 等！

## 长期维护 Clojure 项目

Clojure 作为一门动态语言，同样有“编写爽，维护难”痛点，解决方式也是统一的：完备的测试，外加 lint（代码质量检测）。

### Test

测试这个问题很尴尬，是每个开发者都知道很重要但很少落实到位的一项技能，除了基本的单元测试，还要有覆盖整条链路的黑盒测试，不仅仅测正常的输入，更多的是异常情况。
下面说下 Clojure 单元测试开发中会用到的一些技巧：
1. [clojure.test](https://clojure.github.io/clojure/clojure.test-api.html) 提供了最基本的断言，[use-fixtures](https://clojuredocs.org/clojure.test/use-fixtures) 可以进行一些 setup 与 teardown
2. [with-redefs](https://clojuredocs.org/clojure.core/with-redefs) 可以去 mock 一些外部依赖的返回
3. [ultra](https://github.com/venantius/ultra/wiki/Tests) 更直观的测试结果展示

### Lint

Clojure 作为一 Lisp 方言，有非常强的表现力，几行代码就可以干很多事情，为了保证整个团队有统一的编程风格，应该在项目起始阶段，就加上质量检测。
Clojure 社区里面，[eastwood](https://github.com/jonase/eastwood) 是一个非常全面的 lint 工具，它帮助我发现了很多程序中肉眼难以识别的错误，成熟 Clojure 程序员必备。

### 跟进社区

- Clojure 1.9 引入 [spec](https://clojure.org/news/2017/12/08/clojure19)，尝试来解决一直被初学者诟病的错误信息看不懂的问题
- Clojure 1.10 更进一步，[对错误信息进行了分类](https://clojure.org/news/2018/12/17/clojure110)，适配 Java 9 带来的 module

除了 Clojure 语言本身外，Lein/JVM 等周边生态链也在不断推进，我们需要及时去了解这些新技术，现在我比较头疼的是下面这两个：
1. Lein 在 3.0 大版本中会[移除对 hook 的支持](https://github.com/technomancy/leiningen/blob/master/doc/PLUGINS.md#hooks)，这将会导致很多有用的插件不可用，包括上面推荐的 lein-shorthand
2. Java 9 为了支持 module，[改变了 classloader 的行为](https://stackoverflow.com/questions/46494112/classloaders-hierarchy-in-java-9)，导致[无法使用 alembic 提供的动态加载依赖](https://github.com/clojure-emacs/clj-refactor.el/issues/410)的功能，所以目前只能锁定在 Java 8 上

## 他山之石

Clojure 社区虽小，但不乏高手，通过阅读高手的代码，是熟悉一门语言 idioms 最有效的方式。下面介绍社区内，对我影响最大的三位：

### [Nathan Marz](http://nathanmarz.com/)

一个非常务实的 coder，文章见解独特、观点新颖。明星项目：
- [Storm](https://github.com/nathanmarz/storm) 流式数据框架
- [Specter](https://github.com/nathanmarz/specter) 号称 Clojure(Script)'s missing piece，操作复杂数据结构的利器！
- [Big Data: Principles and best practices of scalable realtime data systems](https://www.manning.com/books/big-data)，在本书中提出有名的 [Lambda 架构](https://en.wikipedia.org/wiki/Lambda_architecture)
- [Cascalog](https://github.com/nathanmarz/cascalog) 这是我 2014 年首次接触 Clojure 时用的项目，主要是分析日志。语法借鉴自声明式逻辑语言 [Datalog](https://en.wikipedia.org/wiki/Datalog)

### [Kyle Kingsbury](https://aphyr.com) a.k.a "Aphyr"

神人一个，高产 coder。明星项目：
- [Riemann](http://riemann.io/) 一个强大的监控系统，具备丰富的[数据流操作](http://riemann.io/api/riemann.streams.html)
- [Jepsen](https://jepsen.io/) 著名的分布式系统测试框架
- [Clojure from the Ground Up](https://aphyr.com/tags/Clojure-from-the-ground-up) 介绍 Clojure 的一系列文章
- https://github.com/aphyr

### [Zach Tellman](https://ideolalia.com/)

神人另一个，高产 coder，貌似与 Aphyr 共事过
- [Elements of Clojure](https://elementsofclojure.com/) This book tries to put words to what most experienced programmers already know
- https://github.com/ztellman
我目前还没直接使用过 Zach 写的库，这是由于他的库很多都是基本性质的，所以很有极有可能间接引用了他的库，比如 specter 就用了他的 riddley。下面一张图摘自他的博客：
![Zach's libraries](https://ideolalia.com/images/libraries.png)


混 Clojure 社区，应该还会经常看到 Congnitect 公司内的 [Rich](https://github.com/richhickey)/[Stuart Halloway](https://github.com/stuarthalloway)/[Alex Miller](https://github.com/puredanger)/[Michael Fogus](http://blog.fogus.me/)...

## Clojure 工作机会

首先明确一点，语言只是工具，而只会工具是找不到工作的，很多初学 Clojure 的同学都有这个误区。打个比方：一个厨师的刀工非常好，但是不知道如何去做菜（领域知识），有什么用呢？

比如，做 Web 开发，那对 HTTP 了解多少？ TCP/UDP 区别是什么？Mysql 锁有几种？这些都是必须的。再进一步，JVM 上的 gc 懂吗？多线程用过没？linux 上如何排除进程相关信息？

有了以上基础，我们也不得不承认，使用 Clojure 作为主力开发语言的公司确实少，但也不是没有，比如：北京的 LeanCloud/BearyChat、深圳的 [风林火山](https://www.bagevent.com/event/1760284) 。
即使工作中无法使用，了解这门优雅、富有表现力的语言来扩展自己的眼界，也是不错的选择。

## 总结

从 14 年实习期间接触 Clojure，到现在 19 年差不多 5 年了，学到了太多太多东西，一方面是编程语言的设计，另一方面是后端开发的整个体系。坊间甚至一度传闻 [Clojure is dead](https://news.ycombinator.com/item?id=14418013)。
Clojure 不是银弹，肯定是有一些瑕疵，但这并不妨碍它是一门优秀的语言，虽然我现在工作中用不到它了，但是业余时间肯定还是会去研究它，社区有太多有意思的项目了。
希望新入门的同学可以坚持下去，早日体味到 Clojure 的乐趣。加油！
