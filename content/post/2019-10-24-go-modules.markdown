---
categories:
- 编程语言
date: 2019-10-24 21:30:55
tags:
- Go
title: 何处安放我们的 Go 代码
---

用了近半年的 Go，真是有种相见恨晚的感觉。简洁的语法、完善并强大的开发工具链，省去新手不少折腾的时间，可以专注写代码。
这期间也掌握了不少技巧与惯用法（idioms），比如 [prosumer](https://github.com/jiacai2050/prosumer)，就是一个踩了 chan/timer 一些坑后实现生产者/消费者模式框架。但今天不去谈 chan 的使用方式，而是来谈一个最基本的问题，Go 代码应该放在哪里，其实也就是 Go 的包管理机制，有时也称为版本化，其实是一个意思。这看似简单，却让不少 Gopher [吃了不少苦头](https://stackoverflow.com/questions/tagged/go-modules)。

本文大致顺序：包管理的历史；新的包管理方式 module；最后加上一个问题排查，彻底解决如何放置 Go 代码的问题。

![Go package manager](https://img.alicdn.com/imgextra/i4/581166664/O1CN01CCdfct1z69wzuInE9_!!581166664.png)

## GOPATH

在 go mod 出现之前，所有的 Go 项目都需要放在同一个工作空间：`$GOPATH/src` 内，比如：
```bash
src/
    github.com/golang/example/
        .git/                      # Git repository metadata
    outyet/
        main.go                # command source
        main_test.go           # test source
    stringutil/
        reverse.go             # package source
        reverse_test.go        # test source
```
相比其他语言，这个限制有些无法理解。其实，这和 Go 的一设计理念紧密相关：
> 包管理应该是去中心化的

所以 Go 里面没有 maven/npm 之类的包管理工具，只有一个 `go get`，支持从公共的代码托管平台（Bitbucket/GitHub..）下载依赖，当然也支持自己托管，具体可参考官方文档：[Remote import paths](https://tip.golang.org/cmd/go/#hdr-Remote_import_paths)。

由于没有中央仓库，所以 Go 项目位置决定了其 import path，同时为了与 go get 保持一致，所以一般来说我们的项目名称都是 `github.com/user/repo` 的形式。
当然也可以不是这种形式，只是不方便别人引用而已，后面会讲到如何在 go mod 中实现这种效果。

## 百花齐放

使用 `go get` 下载依赖的方式简单暴力，伴随了 Go 七年之久，直到 1.6（2016/02/17）才正式支持了 [vendor](https://golang.org/doc/go1.6#go_command)，可以把所有依赖下载到当前项目中，解决可重复构建（reproducible builds）的问题，但是无法管理依赖版本。社区出现了各式各样的[包管理工具](https://github.com/golang/go/wiki/PackageManagementTools#dep-tool)，来方便开发者固化依赖版本，由于不同管理工具采用不同的元信息格式（比如：godep 的 Godeps.json、Glide 的 glide.yaml），不利于社区发展，所以 Go 官方推出了 [dep](https://github.com/golang/dep)。

dep 的定位是实验、探索如何管理版本，并不会直接集成到 Go 工具链，Go 核心团队会吸取 dep 使用经验与社区反馈，开发下一代包管理工具 [modules](https://github.com/golang/go/wiki/Modules)，并于 2019/09/03 发布的 [1.13](https://golang.org/doc/go1.13) 正式支持，并随之发布 [Module Mirror, Index, Checksum](https://blog.golang.org/module-mirror-launch)，用于解决软件分发、中间人攻击等问题。下图截取自 Go [官方博客](https://blog.golang.org/modules2019)

![Module Big Picture](https://img.alicdn.com/imgextra/i3/581166664/O1CN01NxbOES1z69wxSzgy2_!!581166664.png_620x10000.jpg)

## Modules

Module 是多个 package 的集合，版本管理的基本单元，使用 go.mod 文件记录依赖的 module。

go.mod 位于项目的根目录，支持 4 条命令：module、require、replace、exclude。示例：

```golang
module github.com/my/repo

require (
    github.com/some/dependency v1.2.3
    github.com/another/dependency/v4 v4.0.0
)
```
- module 声明 module path，一个 module 内所有 package 的 import path 都以它为前缀

假如一个 module 有如下目录结构，go.mod 采用上面的示例
```
repo
|-- bar
|   `-- bar.go
|-- foo
|   `-- foo.go
`-- go.mod
```
那么 bar 包的 import path 即为：
```go
import "github.com/my/repo/bar"
```

- require 声明所依赖的 module，版本信息使用形如 `v(major).(minor).(patch)` 的语义化版本 [semver](https://semver.org/)，比如：v0.1.0
- replace/exclude 用于替换、排查指定 module path

下面重点介绍 modules 中最实用的两个方面：semantic version 与 replace 指令。

### Semantic Version

![语义化版本](https://img.alicdn.com/imgextra/i4/581166664/O1CN01bk1zqT1z69wz301hZ_!!581166664.png_620x10000.jpg)

语义化版本要求 v1 及以上的版本保证向后兼容，对于有 breaking change 的 v2 及以上的版本，需要把版本信息体现在 module path 中，比如

```
module github.com/my/mod/v2

require github.com/my/mod/v2 v2.0.1
import "github.com/my/mod/v2/mypkg"

go get github.com/my/mod/v2@v2.0.1
```
举一个场景：

![dependency hell](https://img.alicdn.com/imgextra/i3/581166664/O1CN01ZyOLHg1z69wz3Le3i_!!581166664.png_310x310.jpg)

从上图可以看的，A 通过直接或间接依赖 D 的三个不同版本，如果不把版本号放在 module path 中，如何去加载正确的版本的？当然，这里有个前提，同一个大版本内必须保证向后兼容！

下面截取 prometheus 的部分 [go.mod](https://github.com/prometheus/prometheus/blob/master/go.mod)，来进一步探索 go.mod 的用法

```
module github.com/prometheus/prometheus

go 1.13

require (
    # indirect 表示间接依赖
    cloud.google.com/go v0.44.1 // indirect
    k8s.io/klog v0.4.0
    # 这里采用 pseudo_versions 表示没有采用 go module，且没有打版本 tag
    github.com/alecthomas/units v0.0.0-20190717042225-c3de453c63f4
    # incompatible 表示 go-autorest 没有采用 go module，而且版本大于 v2
    github.com/Azure/go-autorest v11.2.8+incompatible
    github.com/aws/aws-sdk-go v1.23.12
)

replace (
    # 表示从 github.com 下载 klog，而不是 k8s.io
    k8s.io/klog => github.com/simonpasquier/klog-gokit v0.1.0
)
```
这里重点说一下伪版本 [pseudo_versions](https://golang.org/cmd/go/#hdr-Pseudo_versions)，主要用于兼容未采用 module 的依赖。一般形式：
- `v0.0.0-yyyymmddhhmmss-abcdefabcdef`

中间的时间采用 UTC 表示，用于对比两个伪版本的新旧；最后的部分为 commit id 前 12 个字符。

### Replace

go.mod 的 replace 主要用于替换 module path，这对于引用本地依赖非常有帮助。比如有一个库 `github.com/user/lib` 有 bug，你需要 fork 到本地去修复，这时在自己的项目中需要引用本地 fork 的分支，那么就可以这么用：

```
replace github.com/user/lib => /some/path/on/your/disk
```
代码里面的 import path 不用变。

类似的原理，项目的 module 名字，也不必加上托管平台前缀了。我创建了一个示例项目 [strutil](https://github.com/jiacai2050/strutil)，其 go.mod 如下：

```
module strutil

go 1.12
```
如果要引用这个项目，只需要这么做：

```go
// go.mod
replace strutil => github.com/jiacai2050/strutil v0.0.1

// str_test.go
import strutil

func TestModule(t *testing.T) {
    s := strutil.Reverse("hello")
    assert.Equal(t, "olleh", s)
}

```

### 常用命令

对于使用 module 开发的项目，使用 `go mod init {moduleName}` 初始化后，直接在源文件中 import 所需包名，go test/build 之类的命令会自动分析，将其加到 go.mod 中的 require 里面，不需要自己去修改。开发测试完成后，需要打 tag 才能让其它用户使用。
项目的版本号一般从 v0.1.0 开始，表示开始第一个 feature，当有 bugfix 时，变更第三个版本号，如 v0.1.1；当有新 feature 时，变更中间版本号，如 v0.2.0；有 breaking changes 时，变更第一个版本号，比如 v2.0.0。

对于 v2 及以上版本，一般有[两种目录组织方式](https://github.com/golang/go/wiki/Modules#releasing-modules-v2-or-higher)，一是直接在项目根目录的 go.mod 中的 module path 中增加 `v2` 后缀，例如：`github.com/my/module/v2`；二是建一个子目录 `v2`，把相关代码拷贝过来，在这个目录下创建 go.mod，module path 与第一种相同。这两种方式同样都需要打 `v2.x.x` 的 tag 表示版本信息。参考[示例](https://github.com/jiacai2050/strutil/tree/57d66f5d6b980e4a4966013f87b0c770c458e0ea)
```
.
├── go.mod          // module github.com/jiacai2050/strutil
├── string.go
├── string_test.go
└── v2
    ├── go.mod      // module github.com/jiacai2050/strutil/v2
    └── string.go
```
很明显，第二种目录方式方便同时维护多个版本。

除此之外，一般还需配置如下相关变量：

```bash
# 1.13 默认开启
export GO111MODULE=on
# 1.13 之后才支持多个地址，之前版本只支持一个
export GOPROXY=https://goproxy.cn,https://mirrors.aliyun.com/goproxy,direct
# 1.13 开始支持，配置私有 module，相当于同时设置 GONOPROXY GONOSUMDB ，表示不走代理，不检查 checksum
export GOPRIVATE=*.corp.example.com,rsc.io/private
# 关闭 checksum 校验，一般不需要设置，通过 GOPRIVATE 进行细粒度控制
# go get -insecure .. 是也不会检查 checksum
GOSUMDB=off
```
关于 module 校验的更多内容，可参考：
- https://golang.org/cmd/go/#hdr-Module_configuration_for_non_public_modules

其它常用命令有：
- `go mod download -json` 查看 module 详细信息
```
    type Module struct {
        Path     string // module path
        Version  string // module version
        Error    string // error loading module
        Info     string // absolute path to cached .info file
        GoMod    string // absolute path to cached .mod file
        Zip      string // absolute path to cached .zip file
        Dir      string // absolute path to cached source root directory
        Sum      string // checksum for path, version (as in go.sum)
        GoModSum string // checksum for go.mod (as in go.sum)
    }
```
- `go list -m all` 查看当前项目最终所使用的 module 版本
- `go list -u -m all` 查看依赖的新版本
- `go get -u ./...` 更新所有依赖到最新版
- `go get -u=patch ./...` 更新所有依赖到最新的 patch 版本
- `go mod tidy` 清理 go.mod/go.sum 中不在需要的 module
- `go mod vendor` 创建 vendor 依赖目录，这时为了与之前做兼容，后面在执行 go test/build 之类的命令时，可以加上 `-mod=vendor` 这个 build flag 声明使用 vendor 里面的依赖，这样 go mod 就不会再去 `$GOPATH/pkg/mod` 里面去找。

## 问题排查

在使用 go mod 中我遇到过一个问题，之前很是困扰，后来才发现是没清楚 go 命令参数的含义。下面首先看下项目目录结构：

```bash
cd ~/code/ceresdb-go-sdk
$ tree
.
├── Makefile
├── ceresdb
│   ├── client.go
│   ├── client_test.go
├── examples
│   ├── README.md
│   └── quickstart.go
├── go.mod
└── go.sum

$ cat go.mod
module github.com/user/ceresdb-go-sdk
require ( ... )
```
可以看到，项目根目录 ceresdb-go-sdk 内没有 go 源码，而是放在了 ceresdb 子目录中，这么设计的目的是保证 import path 与目录名一致

```
import "github.com/user/ceresdb-go-sdk/ceresdb"
c := ceresdb.NewClient(...)
```
当然也可以去掉 ceresdb 目录，将源码放在项目根目录下，这样 import 就变为 
```
import "github.com/user/ceresdb-go-sdk"
c := ceresdb.NewClient(...)
```
感觉不是很友好，有些 IDE 比较智能，会自动填充 alias
```
# 这也说明包名可以不和目录一致！但是一般都要保证一致，否则会很具备迷惑性
import ceresdb "github.com/user/ceresdb-go-sdk"
```

但现在还是假设采用子目录的方式，执行 `go test ./...`

```
time go test -v -x  ./...
can't load package: package github.com/user/ceresdb-go-sdk: unknown import path "github.com/user/ceresdb-go-sdk": cannot find module providing package github.com/user/ceresdb-go-sdk

# 注意花的时间，这期间没有任何输出，即使加了 -x flag
real	1m2.472s
user	0m0.111s
sys	0m0.082s
```
对于这个错误有些懵，我这个项目不就是  github.com/user/ceresdb-go-sdk 嘛，怎么会报找不到呢？为了解释原因，需要了解下 go 命令的一般形式：

```
go command [command_args] [build flags] [packages]
```

- command 是指 test/build/mod/list 之类命令
- command_args 是指特定命令相关的参数
- build flags 是大部分命令都支持的参数，比较常用的有：
  - `-race` 开启 race 检测
  - `-v` 输出正在编译的包名
  - `-x` 输出详细执行的命令，在 go get 卡住时可以打开定位问题
  - `-mod` 指定 module 依赖下载模式，目前只有两个值：readonly 或者 vendor
  - `-tags` 逗号分隔编译 tags，主要用于区别 build 环境，比如[集成测试](https://stackoverflow.com/a/28007631/2163429)
- packages 指定当前命令作用的包

上面的错误就出错在最后一个参数上，我们知道包的 import path 需要加上 module path，上面的错误也证明了这一点。
特殊的，对于 `./xxx` 会去找对应目录下面的包，不用写 module path 了，`./...` 则意味着递归地找当前目录下的所有包，且包括当前目录。
问题就在于项目根目录下没有任何 go 源文件，所以就找不到当前目录下的包了！解决方法也很简单：

```
go test  ./ceresdb
# go test github.com/user/ceresdb-go-sdk/ceresdb 当然也可以
...
PASS
ok  	github.com/user/ceresdb-go-sdk/ceresdb	0.017s
```
或者，在根目录下加一个 go 文件

```
# 包名可以和 import path 不一致，所以这里 abc 也是可以的
$ echo 'package abc' > abc.go
$ go test .
?   	github.com/user/ceresdb-go-sdk	[no test files]
```
这样也不会报错了。

## vgo
[vgo](https://github.com/golang/vgo) 是 Go 的核心开发者 [Russ Cox](https://swtch.com/~rsc/) 尝试给 Go 增加包管理的原型，是个单独的命令，相当于自动加上 `GO111MODULE=on` 的 go 命令，在把包管理功能集成到 go 命令时，才叫 modules。
> The reference implementation was named vgo, but support for modules is being integrated into the go command itself. The feature within the go command is called “versioned Go modules” (or “modules” for short), not “vgo”.

关于 Go 的包管理，Russ Cox 有一系列 [vgo](https://github.com/golang/go/wiki/vgo) 的文章介绍[来龙去脉](https://research.swtch.com/vgo)，感兴趣的读者可以去看看。

## 总结

通过本文的介绍，希望让大家更清楚了解 modules 的设计初衷以及如何排查问题，做到语义化版本，大版本向后兼容。如果你的项目比较复杂，项目的结构可以参考：
- https://github.com/golang-standards/project-layout

Clojure 作者 Rich Hickey 有个有名的演讲 [Simple Made Easy](https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/SimpleMadeEasy.md)，主要讲述了可以通过简单的工具来降低软件开发的复杂度，Go 作者 Rob Pike 在 2015 年的一个 talk [Simplicity is Complicated](https://talks.golang.org/2015/simplicity-is-complicated.slide#1) 中也指出，Go 成功的一大原因源自其简单易用的特性。

![Simplicity](https://img.alicdn.com/imgextra/i1/581166664/O1CN012w8eQ11z69x0Nk2xz_!!581166664.jpg)

## 参考

- https://golang.org/doc/code.html
- https://blog.golang.org/modules2019
- https://research.swtch.com/vgo-intro
- https://medium.com/@sdboyer/so-you-want-to-write-a-package-manager-4ae9c17d9527
