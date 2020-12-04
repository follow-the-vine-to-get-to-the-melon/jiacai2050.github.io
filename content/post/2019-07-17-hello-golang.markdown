---
title: 写给新手的 Go 开发指南
date: 2019-07-17 21:52:33
categories: [编程语言]
tags: [Go]
---

转眼加入蚂蚁已经三个多月，这期间主要维护一 Go 写的服务器。虽然用的时间不算长，但还是积累了一些心得体会，这里总结归纳一下，供想尝试 Go 的同学参考。
本文会依次介绍 Go 的设计理念、开发环境、语言特性。本文在谈及语言特性的时也会讨论一些 Go 的不足之处，旨在给读者提供一个全面的视角。

## 简介

一般来说，编程语言都会有一个 slogan 来表示它们的特点。比如提到 Clojure，一般会想到这么几个词汇：lisp on JVM、immutable、persistent；Java 的话我能想到的是企业级开发、中规中矩。对于 Go ，官网介绍到：

> Go is an open source programming language that makes it easy to build simple, reliable, and efficient software.

提取几个关键词：open（开放）、simple（简洁）、reliable（可靠）、efficient（高效）。这也可以说是它的设计目标。除了上面这些口号外，初学者还需要知道 Go 是一门命令式的静态语言（是指在编译时检查变量类型是否匹配），与 Java 属于同一类别。

|         | Imperative             | Functional          |
|---------|------------------------|---------------------|
| Dynamic | Python/Ruby/Javascript | Lisp/Scheme/Clojure |
| Static  | Java/C\+\+/Rust/Go     | OCaml/Scala/Haskell |

由于 [Hello World](https://play.golang.org/) 太简洁，不具备展示 Go 的特点，所以下面展示一段访问 httpbin，打印 response 的完整代码。

```go
package main

import (
    "fmt"
    "io/ioutil"
    "net/http"
)

func main() {
    // http://httpbin.org/#/Anything/get_anything
    r, err := http.Get("http://httpbin.org/anything?hello=world")
    if err != nil {
        panic(err)
    }
    defer r.Body.Close()

    bs, err := ioutil.ReadAll(r.Body)
    if err != nil {
        panic(err)
    }
    fmt.Printf("body = %s\n", bs)
}

```
上面的代码片段包括了 Go 的主要组成：包的声明与引用、函数定义、错误处理、流程控制、[defer](https://tour.golang.org/flowcontrol/12)。

## 开发环境

通过上面的代码片段，可以看出 Go 语言 simple（简洁）的特点，所以找一个最熟悉的文本编辑器，一般通过配置插件，都可以达到快速开发的目的。很久之前我就已经把所有文本编辑放到 Emacs 上，这里介绍下我的配置。

除了 [go-mode](https://github.com/dominikh/go-mode.el) 这个 major mode，为了配置像 源码跳转、API 自动补全、查看函数文档等现代 IDE 必备功能，需要安装以下命令
```sh

go get -u github.com/rogpeppe/godef
go get -u github.com/stamblerre/gocode # for go-eldoc/company-go
go get -u golang.org/x/tools/cmd/goimports
go get -u github.com/kisielk/errcheck
go get -u github.com/lukehoban/go-outline # for go-imenu
```
然后再按照 [setup-go.el](https://github.com/jiacai2050/dotfiles/blob/master/.emacs.d/customizations/setup-go.el) 里的配置，就拥有了一个功能完备的开发环境。

![Emacs Go 开发环境](https://img.alicdn.com/imgextra/i3/581166664/O1CN01TBr6Xm1z69vZesJfk_!!581166664.png)

不像 Java 语言需要运行时，Go 支持直接将整个项目 build 成一个二进制文件，方便部署，而支持[交叉编译](https://dave.cheney.net/2015/08/22/cross-compilation-with-go-1-5)，不过在开发时，直接 `go run XXX.go` 更为便利，截止到 Go 1.12，还不支持 [REPL](https://stackoverflow.com/questions/8513609/does-go-provide-repl)，官方有提供在线版的 [Playground](https://play.golang.org/) 供分享、调试代码。

我个人的习惯是建一个 go-app 项目，每个要测试的逻辑放到一个 test 里面去，这样就可以使用 `go test -v -run XXX` 来运行。之所以不选用 `go run`，是因为一个目录下只允许有一个 main 的 package，多个 IDE 会提示错误。

## 数据类型

一般编程语言，[数据类型](https://go101.org/article/type-system-overview.html)分为基本的与复杂的两类。
基本的一般比较简单，表示一个值，Go 里面就有 string, bool, int8, int32(rune), int64, float32, float64, byte(uint8) 等基本类型
复杂类型一般表示多个值或具有某些高级用法，Go 里面有：
- pointer Go 里只支持取地址 `&` 与间接访问 `*` 操作符，不支持对指针进行算术操作
- struct 类似于 C 语言里面的 struct，Java 里面的对象
- function 函数在 Go 里是一等成员
- array 大小固定的数组
- slice 动态的数组
- map 哈希表
- chan 用于在多个 goroutine 内通信
- interface 类似于 Java 里面的接口，一组方法的封装

下面将重点介绍 Go 里特有或用途最广的数据类型。

### struct/interface
Go 里面的 struct 类似于 Java 里面的 Object，但是并没有继承，仅仅是对数据的一层包装（抽象）。相对于其他复杂类型，struct 是**值类型**，也就是说作为函数参数或返回值时，会拷贝一份值。
一般来说，值类型分配在 stack 上，与之相对的引用类型，分配在 heap 上。
初学者一般会有这样的误区，认为传值比传引用要慢，实则不然，具体涉及到 Go [如何管理内存](https://www.ardanlabs.com/blog/2017/05/language-mechanics-on-stacks-and-pointers.html)，这里暂不详述，感兴趣到可以阅读：
- [The Top 10 Most Common Mistakes I’ve Seen in Go Projects](https://itnext.io/the-top-10-most-common-mistakes-ive-seen-in-go-projects-4b79d4f6cd65)
- [pointer_test.go](https://gist.github.com/teivah/a32a8e9039314a48f03538f3f9535537) 这个测试在笔者机器上运行结果：
```
BenchmarkByPointer-8    20000000                86.7 ns/op
BenchmarkByValue-8      50000000                31.9 ns/op
```
所以一般情况下推荐直接使用值类型的 struct，如果需要改变状态，再考虑改为指针类型（&struct）

如果说 struct 是对状态的封装，那么 interface 就是对行为的封装，相当于对外的契约（contract）。而且 Go 里面有这么一条[最佳实践](https://www.reddit.com/r/golang/comments/cf1lda/having_trouble_understanding_how_to_properly_use/eu7r4f3)

> Accept interfaces, return concrete structs. （函数的参数尽量为 interface，返回值为 struct）

这样的好处也很明显，作为类库的设计者，对其要求的参数尽量宽松，方便使用，返回具体值方便后续的操作处理。一个极端的情况，可以用 `interface{}` 表示任意类型的参数，因为这个接口里面没有任何行为，所以所有类型都是符合的。又由于 Go 里面不支持[范型](https://dev.to/deanveloper/go-2-draft-generics-3333)，所以`interface{}`是唯一的解决手段。

相比较 Java 这类面向对象的语言，接口需要显式（explicit）继承（使用 implements 关键字），而在 Go 里面是[隐式的（implicit）](https://golang.org/doc/faq#implements_interface)，新手往往需要一段时间来体会这一做法的巧妙，这里举一例子来说明：

Go 的 IO 操作涉及到两个基础类型：Writer/Reader ，其定义如下：

```go
type Reader interface {
        Read(p []byte) (n int, err error)
}

type Writer interface {
        Write(p []byte) (n int, err error)
}
```
自定义类型如果实现了这两个方法，那么就实现了这两个接口，下面的 Example 就是这么一个例子：

```go
type Example struct {
}
func (e *Example) Write(p byte[]) (n int, err error) {
}
func (e *Example) Read(p byte[]) (n int, err error) {
}
```
由于隐式继承过于灵活，在 Go 里面可能会看到[如下代码](https://stackoverflow.com/questions/17994519/golang-interface-compliance-compile-type-check)：
```go
var _ blob.Fetcher = (*CachingFetcher)(nil)
```
这是通过将 nil 强转为 `*CachingFetcher`，然后在赋值时，指定 `blob.Fetcher` 类型，保证 `*CachingFetcher` 实现了 `blob.Fetcher` 接口。
作为接口的设计者，如果想实现者显式继承一个接口，可以在接口中[额外加一个方法](https://golang.org/doc/faq#guarantee_satisfies_interface)。比如：
```go
type Fooer interface {
    Foo()
    ImplementsFooer()
}
```
这样，实现者必须实现 `ImplementsFooer` 方法才能说是继承了 `Fooer` 接口。所以说隐式继承有利有弊，需要开发者自己去把握。

### map/slice

Map/Slice 是 Go 里面最常用的两类数据结构，属于引用类型。在语言 runtime 层面实现，仅有的两个支持范型的结构。
Slice 是长度不固定的数组，类似于 Java 里面的 [List](https://docs.oracle.com/javase/8/docs/api/java/util/List.html)。

```go
// map 通过 make 进行初始化
// 如果提前知道 m 大小，建议通过 make 的第二个参数指定，避免后期的数据移动、复制
m := make(map[string]string, 10)
// 赋值
m["zhangsan"] = "teacher"
// 读取指定值，如不存在，返回其类型的默认值
v := m["zhangsan"]
// 判断指定 key 知否在 map 内
v, ok := m["zhangsan"]

// slice 通过 make 进行初始化
s := make([]int)
// 增加元素
s = append(s, 1)

// 也可以通过 make 第二个参数指定大小
s := make([]int, 10)
for i:=0;i<10;i++ {
    s[i] = i
}
// 也可以使用三个参数的 make 初始化 slice
// 第二个参数为初始化大小，第三个为最大容量
// 需要通过 append 增加元素
s := make([]int, 0 ,10)
s = append(s, 1)
```

### chan/goroutine

作为一门新语言，Goroutine 是 Go [借鉴 CSP 模型](https://golang.org/doc/faq#csp)提供的并发解决方案，相比传统 OS 级别的线程，它有以下[特点](https://stackoverflow.com/a/27794268/2163429)：
1. 轻量，完全在用户态调度（不涉及OS状态直接的转化）
2. 资源占用少，启动快
3. 目前，Goroutine 调度器不保证公平（fairness），抢占（pre-emption）也支持的非常有限，一个空的 `for{}` 可能会一直不被调度出去。

一般可以使用 chan/select 来进行 Goroutine 之间的调度。chan 类似于 Java 里面的 [BlockingQueue](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/BlockingQueue.html)，且能保证 Goroutine-safe，也就是说多个 Goroutine 并发进行读写是安全的。

chan 里面的元素默认为1个，也可以在创建时指定缓冲区大小，读写支持堵塞、非堵塞两种模式，关闭一个 chan 后，再写数据时会 panic。

```go
// chan 与 slice/map 一样，使用 make 初始化
ch := make(chan int, 2)

// blocking read
v := <-ch
// nonblocking read, 需要注意 default 分支不能省略，否则会堵塞住
select {
    case v:=<-ch:
    default:
} 

// blocking write
ch <- v
// nonblocking write
select {
    case ch<-v:
    default:
}
```
chan 作为 Go 内一重要数据类型，看似简单，实则暗藏玄妙，用时需要多加留意，这里不再展开叙述，后面打算专门写一篇文章去介绍，感兴趣的可以阅读下面的文章：
- [Curious Channels](https://dave.cheney.net/2013/04/30/curious-channels)
- [Prosumer](https://github.com/jiacai2050/prosumer) 基于 buffered chan 实现的生产者消费者，核心点在于关闭 chan 只意味着生产者不能再发送数据，消费者无法获知 chan 是否已经关闭，需要用其他方式去通信。


## 语言特性

Go 相比 Java 来说，语言特性真的是少太多。推荐 [Learn X in Y minutes](https://learnxinyminutes.com/docs/go/) 这个网站，快速浏览一遍即可掌握 Go 的语法。Go 的简洁程度觉得和 JavaScript 差不多，但却是一门静态语言，具有强类型，这两点又让它区别于一般的脚本语言。

### 代码风格

Go 遵循约定大于配置（convention over configuratio）的设计理念，比如在构建一个项目时，直接 `go build` 一个命令就搞定了，不需要什么 Makefile、pom.xml 等配置文件。下面介绍几个常用的约定：

- 一个包内函数、变量的可见性是通过首字母大小写确定的。大写表示可见。
- 一般 `{` 放在行末，否则 Go 编辑器会[自动插入一个逗号](https://golang.org/doc/effective_go.html#semicolons)，导致编译错误
- 一个文件夹内，只能定义一个包
- 变量、函数命名[尽量简短](https://dave.cheney.net/practical-go/presentations/qcon-china.html#_identifier_length)，标准库里面经常可以看到一个字母的变量

由于以上种种约定，在看别人代码时很舒服，有种 Python 的感觉。另外建议在编辑器中配置 [goimports](https://godoc.org/golang.org/x/tools/cmd/goimports) 来自动化格式代码。

### 错误处理

Go 内没有 try catch 机制，而且已经明确拒绝了这个 [Proposal](https://github.com/golang/go/issues/32437)，而是通过返回值的方式来处理。

```go
f, err := os.Open(filename)
if err != nil {
    return …, err  // zero values for other results, if any
}
```
Go 的函数一般通过返回多值的方式来传递 error（且一般是第二个位置），实际项目中一般使用 [pkg/errors](https://github.com/pkg/errors) 去处理、包装 err。

### 依赖管理

Go 的依赖管理，相比其他语言较弱。
在 Go 1.11 正式引入的 [modules](https://blog.golang.org/using-go-modules) 之前，项目必须放在 $GOPATH/src/xxx.com/username/project 内，这样 Go 才能去正确解析项目依赖，而且 Go 社区没有统一的包托管平台，不像 Java 中 maven 一样有中央仓库的概念，而是直接引用 Git 的库地址，所以在 Go 里，一般会使用 `github.com/username/package` 的方式来表示。
`go get` 是下载依赖的命令，但一个个去 get 库不仅仅繁碎，而且无法固化依赖版本信息，所以 [dep](https://github.com/golang/dep) 应运而生，添加新依赖后，直接运行 `dep ensure` 就可以全部下下来，而且会把当前依赖的 commit id 记录到 Gopkg.lock 里面，这就能解决版本不固定的问题。

但 modules 才是正路，且在 1.13 版本会默认开启，所以这里只介绍它的用法。

```sh
# 首先导出环境变量
export GO111MODULE=on
# 在一个空文件夹执行 init，创建一个名为 hello 的项目
go mod init hello
# 这时会在当前文件夹内创建 go.mod ，内容为

module hello

go 1.12
# 之后就可以编写 Go 文件，添加依赖后，执行 go run/test/build...
# 依赖会自动下载，并记录在 go.mod 内，版本信息记录在 go.sum
```
更多用法可以参考官方示例，这里只是想说明 [go tools](https://github.com/golang/tools) 大部分已经支持，但是 [godoc 还不支持](https://github.com/golang/go/issues/26827)，更多可参考 [#24661](https://github.com/golang/go/issues/24661)。

### GC 

Go 也是具有[垃圾回收](https://blog.golang.org/ismmkeynote)的语言，但相比于 JVM，Go GC 可能显得及其简单，从 Go 1.10 开始，Go GC 采用 Concurrent Mark & Sweep (CMS) 算法，且不具有分代、compact 特性。读者如果对相关名词不熟悉，可以阅读：
- https://engineering.linecorp.com/en/blog/go-gc/

而且 Go 里面调整 GC 的参数只有一个 `GOGC`，表示下面的比率

> 新分配对象 / 上次 GC 后剩余对象

默认 100，表示新分配对象达到上次 GC 后剩余对象的两倍时，进行 GC。
- 调大 GOGC，可以减少 GC 的总体耗时
- 减小 GOGC，意味着用更多的 GC 来换取更少的内存使用

`GOGC=off` 可以关闭 GC，[SetGCPercent](https://golang.org/pkg/runtime/debug/#SetGCPercent) 可以动态修改这个比率。

在启动一个 Go 程序时，可以设置 `GODEBUG=gctrace=1` 来打印 GC 日志，日志具体含义可参考 [pkg/runtime](https://golang.org/pkg/runtime/#hdr-Environment_Variables)，这里不再赘述。对调试感兴趣的可以阅读：
- https://new.blog.cloudflare.com/go-dont-collect-my-garbage/

## 总结

Go 最初由 Google 在 2007 为解决软件复杂度、提升开发效率的一试验品，到如今不过十二年，但无疑已经[家喻户晓](https://hackernoon.com/major-programming-trends-to-prepare-for-in-2019-169987cc75f4)，成为[云时代的首选](https://thenewstack.io/go-the-programming-language-of-the-cloud/)。其面向接口的特有编程方式，也非常灵活，兼具动态语言的简洁与静态语言的高效，推荐大家尝试一下。Go Go Go!

![Go](https://golang.org/lib/godoc/images/go-logo-blue.svg)

## 扩展阅读

- [03-包与依赖管理.md](https://github.com/overnote/golang/blob/master/01-Go初识/03-包与依赖管理.md)
- [I Love Go; I Hate Go](http://dtrace.org/blogs/ahl/2016/08/02/i-love-go-i-hate-go/)
- [The Go Programming Language Specification#Receive operator](https://golang.org/ref/spec#Receive_operator)
- [王垠：对 Go 语言的综合评价](http://www.yinwang.org/blog-cn/2014/04/18/golang)
- https://github.com/golang/go/wiki/CodeReviewComments
- https://golang.org/doc/faq
- https://blog.golang.org/go15gc
