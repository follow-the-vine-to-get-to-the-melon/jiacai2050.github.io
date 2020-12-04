---
categories:
- 编程语言
date: 2020-03-14 22:52:26
tags:
- Go
title: Go struct/interface 最佳实践
---

使用 Go 已经一年，深深沉浸在其简洁的设计中，就像其官网描述的：

> Go is expressive, concise, clean, and efficient. It's a fast, statically typed, compiled language that feels like a dynamically typed, interpreted language.

Rob Pike 在 [Simplicity is Complicated](https://talks.golang.org/2015/simplicity-is-complicated.slide) 中也提到 Go 的简洁是其流行的重要原因。简洁并不意味着简单，Go 有着诸多设计确保了把复杂性隐藏在背后。本文就结合笔者自身经验，来讨论 Go 中 struct/interface 的设计理念与最佳实践，帮助读者写出健壮、高效的 Go 程序。


## 值类型的 struct

Go 的设计目标是取代 C/C++，所以 Go 里面的 struct 和 C 的类似，与 int/float 一样属于**值类型**，值类型最重要的特点是在进行赋值时，新变量会得到一份拷贝后的值，这和 Java 中以引用赋值的 Object 有着本质区别。

![Go_struct_vs_Java_object](https://img.alicdn.com/imgextra/i4/581166664/O1CN01Dgr4Ek1z69yFADCwq_!!581166664.png)

这意味着，如果要改变 struct 的内部状态，需要将其定义为指针类型`*struct`。

```go
    type student struct {
        name string
    }

    foo := student{name: "foo"}
    bar := foo
    bar.name = "bar"
    fmt.Println(foo.name)  // 输出 foo

    bar2 := &foo
    bar2.name = "bar"
    fmt.Println(foo.name)  // 输出 bar
```
与之类似的，使用`for range` 遍历 `[]struct` `map[xx]struct` 时，得到的也是一份拷贝。

```go
    m := map[int]student{
        1: {name: "1"},
    }
    m[1].name = "2" // 编译错误： cannot assign to struct field m[1].name in map
```
可以看到，无法直接对 map 中的 struct 进行赋值，这是由于`m[1]`得到的是原有 struct 的拷贝，即使编译器允许这里的赋值，map 中的 struct 值也不会改变，所以编译器直接不允许这种情况。其次，
这里的赋值操作是个 `read-modify-write` 操作，无法保证原子性，更多讨论可参考 [#3117](https://github.com/golang/go/issues/3117)。解决方式有两种：

```go
// 1. 使用临时变量
m := map[int]student{1: {name: "1"}}
tmp := m[1]
tmp.name = "2"
m[1] = tmp

// 2. 使用指针类型
m := map[int]*student{1: {name: "1"}}
m[1].name = "2"
```

笔者多次遇到这个“坑”，那是不是说把所有的 struct 都定义为指针就好了呢？这里需要了解下 Go 的逃逸分析才能回答这个问题。

### 逃逸分析

逃逸分析的主要作用是决定对象分配在内存中的位置，Go 会尽量分配在 stack 上，这样的好处显而易见：回收简单，减轻 GC 压力。可以通过 `go build -gcflags -m xx.go` 查看

```go
func returnByValue(name string) student {
    return student{name}
}

func returnByPointer(name string) *student {
    return &student{name}
}

./snippet.go:6:18: &student literal escapes to heap
```
可以看到，`returnByPointer` 方法的返回值会逃逸，最终分配在 heap 上，关于变量分配在 stack / heap 上的性能差距，可参考：[bench_test.go](https://github.com/jiacai2050/blog-snippets/blob/master/go-struct-interface/bench_test.go)

测试结果：
```bash
go test -run ^NOTHING -bench Struct *.go
goos: darwin
goarch: amd64
BenchmarkPointerVSStruct/return_pointer-8               33634951                34.3 ns/op            16 B/op          1 allocs/op
BenchmarkPointerVSStruct/return__value-8                530202802                2.23 ns/op            0 B/op          0 allocs/op
BenchmarkPointerVSStruct/value_receiver-8               433067940                2.77 ns/op            0 B/op          0 allocs/op
BenchmarkPointerVSStruct/pointer_receiver-8             431380804                2.72 ns/op            0 B/op          0 allocs/op
PASS
ok      command-line-arguments  5.889s
```

可以看到，方法返回 pointer 时，会有一次 heap 分配，占 16 个字节，这正好是 name 字段（string 类型）的大小，8 个字节表示指向数据的指针，8 个字节表示长度（笔者为 64 位系统），类似下面的结构

```go
type StringHeader struct {
    Data uintptr
    Len  int
}
```

方法返回 value 时，则没有 heap 分配，说明所有变量都分配在 stack 上。
对于 receiver 为 pointer 或 value 性能差别不大，这是因为 s 在两种情况下均无逃逸，并且拷贝 struct value 本身与拷贝指针（8 字节）的代价差不多；如果增加 struct 的大小，拷贝指针的代价就会小于 value 本身了。
这个测试也说明变量分配在内存中的位置，与是否为指针无关。

### value vs pointer

结合上面的实验，可以按照下述流程确定选用 value/pointer：
1. 如果 struct 需要改变状态（比如包含 waitgroup/sync.Poll/sync.Mutex 等），则需要 pointer
2. 作为函数返回值，`unsafe.Sizeof(struct)` 大于一定阈值时，拷贝 value 的时间大于在 heap 上分配的时间，考虑用 pointer
3. 作为函数参数，可以把指针看成 8 字节的 value，如果 struct 大小远大于 8 字节，考虑用 pointer
3. 除此之外，struct 即可

为了确定出 2 中的阈值，可以在 struct 中添加一数组元素，之后再来跑上述测试即可，在笔者机器中，这个阈值大概为 72K。
```go
type student struct {
    name string
    dummy  [9000]int64  // 添加一数组元素
}

BenchmarkPointerVSStruct/return_pointer-8                 150147              8147 ns/op           73728 B/op          1 allocs/op
BenchmarkPointerVSStruct/return__value-8                  138591              8146 ns/op               0 B/op          0 allocs/op
```

很少有 struct 会达到这个量级，这是由于 Go 中常用的 slice/map/string 均为复合类型（可认为由 header+data 两部分组成），类似上面的 StringHeader，header 部分是固定的，header 里面有指向数据的指针。

| 简单类型        | 复合类型  |
|--------------- |--------- |
| bool            | slice     |
| numeric         | map       |
| (unsafe)pointer | channel   |
| struct          | function  |
| array           | interface |
|                 | string    |

```go
    fmt.Println(map[string]uint64{
        "ptr":       uint64(unsafe.Sizeof(&struct{}{})),
        "map":       uint64(unsafe.Sizeof(map[bool]bool{})),
        "slice":     uint64(unsafe.Sizeof([]struct{}{})),
        "chan":      uint64(unsafe.Sizeof(make(chan struct{}))),
        "func":      uint64(unsafe.Sizeof(func() {})),
        "interface": uint64(unsafe.Sizeof(interface{}(0))),
    })

    // 输出
    map[chan:8 func:8 interface:16 map:8 ptr:8 slice:24]
```
可以看到，
- chan/func/map/ptr 均为 8 个字节，即一个指向具体数据的指针
- interface 为 16，两个指针，一个指向具体类型，一个指向具体数据。细节可参考 Russ Cox 的 [Go Data Structures: Interfaces ](https://research.swtch.com/interfaces)
- slice 为 24，包括一个指向底层 array 的指针，两个整型，分布表示 cap、len

上文中提到无法直接修改 map 中的 struct，那么下面的程序是否合法？为什么？

```go
    m := map[int][]int{1: {1, 2, 3}}
    m[1][0] = 11
    fmt.Println(m)
```

### 内存对齐

struct 中的字段会按照机器字长进行对齐，所以在性能要求比较高的地方，可以尽量把相同类型的字段放一起。

```go
    fmt.Println(
        unsafe.Sizeof(struct {
            a bool
            b string
            c bool
        }{}),
        unsafe.Sizeof(struct {
            a bool
            c bool
            b string
        }{}),
    )
```
上述代码会依次输出 `32 24`，下面的图示清晰的展示了两个顺序的 struct 在内存中的布局：（[图片来源](https://stackoverflow.com/a/38034334/2163429)）
![field_align](https://img.alicdn.com/imgextra/i2/581166664/O1CN018aBsFK1z69yFIcVSO_!!581166664.png)

最后，读者可以思考下面代码的运行结果：

```go
    fmt.Println(
        unsafe.Sizeof(interface{}(0)),
        unsafe.Sizeof(struct{}{}),
    )
```

## 基于组合的 interface

如果说 struct 是对状态的封装，那么 interface 就是对行为的封装，是 Go 中构造抽象的基础。由于 Go 中没有 oop 的概念，主要是通过组合，而非继承来实现不同组件的整合，比如 io 包下的 Reader/Writer。
但就组合来说，并没有什么优势，Java 中也可以实现，但 Go 中的隐式“继承” 让组合变得十分灵活。

### Embedded struct
下面通过一示例进行说明：

```go
type RecordWriter struct {
    code int
    http.ResponseWriter
}

func (rw *RecordWriter) WriteHeader(statusCode int) {
    rw.code = statusCode
    rw.ResponseWriter.WriteHeader(statusCode)
}

func URLStat(w http.ResponseWriter, r *http.Request, next http.HandlerFunc) {
    // if w.WriteHeader isn't called inside handlerFunc, 200 is the default code.
    rw := &RecordWriter{ResponseWriter: w, code: 200}
    next(rw, r)
    metrics.HTTPReqs.WithLabelValues(r.URL.Path, r.Method, strconv.FormatInt(int64(rw.code), 10)).Inc()
}
```

上述代码片段为 [negroni](https://github.com/urfave/negroni) 中的一个 middleware，用来记录 http code。自定义 Writer 通过嵌入 ResponseWriter，实现了 ResponseWriter 接口，然后通过重写 WriteHeader 的方式来实现业务需求，由于需要改变状态，所以采用指针类型 `*RecordWriter` 来作为 receiver，整个实现非常简洁扼要。

### New func type
第二个示例是关于如何通过自定义 type，来达到简化 err 处理的目的。在 net/http 中，handlerFunc 没有返回值，这就导致在每个异常处理的后面加上一个空的 return 来中止逻辑处理，这样不仅繁琐，还容易遗漏，

```go
func viewRecord(w http.ResponseWriter, r *http.Request) {
    c := appengine.NewContext(r)
    key := datastore.NewKey(c, "Record", r.FormValue("id"), 0, nil)
    record := new(Record)
    if err := datastore.Get(c, key, record); err != nil {
        http.Error(w, err.Error(), 500)
        return
    }
    if err := viewTemplate.Execute(w, record); err != nil {
        http.Error(w, err.Error(), 500)
    }
}

```

这时便可通过自定义新类型来解决这个问题：

```go
type appError struct {
    Error   error
    Message string
    Code    int
}
type appHandler func(http.ResponseWriter, *http.Request) appError

func (fn appHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if e := fn(w, r); e != nil { // e is *appError, not os.Error.
        c := appengine.NewContext(r)
        c.Errorf("%v", e.Error)
        http.Error(w, e.Message, e.Code)
    }
}

func viewRecord(w http.ResponseWriter, r *http.Request) appError {
    c := appengine.NewContext(r)
    key := datastore.NewKey(c, "Record", r.FormValue("id"), 0, nil)
    record := new(Record)
    if err := datastore.Get(c, key, record); err != nil {
        return appError{err, "Record not found", 404}
    }
    if err := viewTemplate.Execute(w, record); err != nil {
        return appError{err, "Can't display record", 500}
    }
    return appError{}
}

mux.HandleFunc("/view", appHandler(viewRecord))
```
可以看到，上述示例通过定义 appHandler 新函数类型，并隐式“继承” [http.Handler](https://golang.org/pkg/net/http/#Handler) 接口来达到了统一集中处理 err 的需求。
该实现漂亮的地方为函数增加新类型，且函数签名与 ServeHTTP 一致，这样就可以直接复用参数。对于初学者来说，可能没想到也可以给 func 类型来定义方法，但是在 Go 中，可以给任何类型增加方法。

之前在网上看到一些框架，采用 [panic](https://github.com/gogf/gf/blob/506552c3a93a9094c96699bdf62c533b5b4f42c6/net/ghttp/ghttp_request.go#L84) 的方式来简化 err 处理，感觉这属于对 panic 的滥用，先不说对性能是否有损耗，更主要的是破坏了 `if err != nil` 的处理方式。希望读者在后续处理繁琐的逻辑时，多去考虑如何抽象新类型来解决。

## 总结


Go 的精妙设计保证了其简洁的特性，而且这些特性可能和传统的 oop 不同，这对于从这些语言转过来的读者来说会采用旧思维去思考问题，这无可厚非，但作为优秀的 Go 程序员，更多的需要从 Go 自身特点来考虑问题，这样就不至于产生“为什么 XX 特性在 Go 中没有”的疑惑，要知道 Go 的作者可是 Rob Pike, Ken Thompson :-)
如果读者阅读/实现过基于 interface 的精巧设计，欢迎留言分享。

## 参考
- https://go101.org/article/value-part.html
- https://github.com/tyranron/golang-sizeof.tips/blob/master/internal/parser/types.go
- https://blog.golang.org/error-handling-and-go
- https://medium.com/a-journey-with-go/go-should-i-use-a-pointer-instead-of-a-copy-of-my-struct-44b43b104963
