---
title: 实践总结：在 Java 中调用 Go 代码
date: 2020-08-08 09:30:53
categories: [编程语言]
tags: [Go, Java]
---

在 Java 中调用 Go 的大致过程如下
```
go --> cgo --> jna --> java
```
整个过程要解决的问题主要两个：
1. 数据类型在两种语言中如何转化
2. 何时清理无用的数据

下面就围绕上述调用过程来阐述，本文涉及代码完整版可以下面链接找到：
- https://github.com/jiacai2050/blog-snippets/tree/master/cgo-jna-demo

# Go -> Cgo

这是跨语言调用的第一步，主要是借助 cgo，把 Go 代码编译 C 共享库。
[cgo](https://golang.org/cmd/cgo/) 是 Go 语言提供与 C 语言互调的一工具。提供一个名为 `C` 的伪 package，供 Go 访问 C 中的变量与函数，如 `C.size_t` `C.stdout` 等；同时提供 5 个特殊函数，用于两种语言间类型的转化：

```go
// Go string to C string
// The C string is allocated in the C heap using malloc.
// It is the caller's responsibility to arrange for it to be
// freed, such as by calling C.free (be sure to include stdlib.h
// if C.free is needed).
func C.CString(string) *C.char

// Go []byte slice to C array
// The C array is allocated in the C heap using malloc.
// It is the caller's responsibility to arrange for it to be
// freed, such as by calling C.free (be sure to include stdlib.h
// if C.free is needed).
func C.CBytes([]byte) unsafe.Pointer

// C string to Go string
func C.GoString(*C.char) string

// C data with explicit length to Go string
func C.GoStringN(*C.char, C.int) string

// C data with explicit length to Go []byte
func C.GoBytes(unsafe.Pointer, C.int) []byte
```

需要注意一点，cgo 中函数不能直接返回 slice/map 等具有 go pointer （区别与 C pointer，由 go runtime 管理生命周期）的数据类型，否则会报下面的 panic 信息：
```
panic: runtime error: cgo result has Go pointer
```

原因也很简单，go 是有 gc 的，假如允许返回具有 go pointer 的数据，那么 C 代码中得到的数据无法保证合法性，很有可能已经被 gc 了，即悬挂指针问题。解决的方式也很简单，就是采用 go 提供的特殊转化函数，将数据转为 `unsafe.Pointer`，在 C 中用 `void *` 的方式去使用。

可以想象，这些特殊转化函数一定对数据进行了深拷贝，来保证数据的合法性，可参考 [C.CBytes 的定义](https://github.com/golang/go/blob/ba9e10889976025ee1d027db6b1cad383ec56de8/src/cmd/cgo/out.go#L1718)

```go
const cBytesDef = `
func _Cfunc_CBytes(b []byte) unsafe.Pointer {
    p := _cgo_cmalloc(uint64(len(b)))
    pp := (*[1<<30]byte)(p)
    copy(pp[:], b)
    return p
}
`
```
但这也意味着，Go/C 代码中需要负责 free 掉无用的数据（至于哪边 free，要看实际情况）。示例：

```go
func main() {
    cs := C.CString("Hello from stdio")
    C.myprint(cs)
    C.free(unsafe.Pointer(cs))
}
```
将 Go 函数导出供 C 调用，需要用 `//export` 标示相关函数，并且 Go 文件需要在 `package main`下。然后用类似下面的 build 命令，即可得到与 C 互调的动态库，同时会生产一个头文件，里面有 export 函数的相关签名。

```bash
# linux 下可输出到 libawesome.so，这里以 Mac 下的动态库为例
go build -v -o libawesome.dylib -buildmode=c-shared ./main.go
```

```go
//export Hello
func Hello(msg string) *C.char {
    return C.CString("hello " + strings.ToUpper(msg))

}

// 头文件中 Hello 的定义
// ptrdiff_t is the signed integer type of the result of subtracting two pointers.
// n 这里表示字符串的长度
typedef struct { const char *p; ptrdiff_t n; } _GoString_;
extern char* Hello(GoString p0);
```
完整代码可参考 [main.go]( https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/src/main/resources/main.go) 、对应的头文件 [libawesome.h](https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/libawesome.h)。

# Cgo -> JNA

这一步主要是 Java 中如何调用 C 代码，目前主要有两种方式，
- [JNA](https://github.com/java-native-access/jna)，优势是调用方便，只需要编写 Java 代码，JNA 框架负责在 C/Java 中进行数据类型转化
- [JNI](https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/jniTOC.html)，优势是性能好，缺点是调用繁琐

详细区别这里不展开叙述，感兴趣的读者可参考下面文章：
- https://blog.caplin.com/2014/12/01/jnajni/

# JNA -> Java

这一步主要是在 Java 代码中如何调用 JNA 框架提供的库进行跨语言调用，也是本文的重点。
JNA 将 Java 基本类型直接映射为 C 中同等大小的类型，这里[摘抄](https://github.com/java-native-access/jna/blob/master/www/Mappings.md)如下

|Native Type|Size|Java Type|Common Windows Types|
|--- |--- |--- |--- |
|char|8-bit integer|byte|BYTE, TCHAR|
|short|16-bit integer|short|WORD|
|wchar_t|16/32-bit character|char|TCHAR|
|int|32-bit integer|int|DWORD|
|int|boolean value|boolean|BOOL|
|long|32/64-bit integer|NativeLong|LONG|
|long long|64-bit integer|long|__int64|
|float|32-bit FP|float||
|double|64-bit FP|double||
|char*|C string|String|LPCSTR|
|void*|pointer|Pointer|LPVOID, HANDLE, LPXXX|

对于 C 中的 struct/pointer，JNA 中也提供了 [Structure](http://java-native-access.github.io/jna/5.6.0/javadoc/com/sun/jna/Structure.html)/[Pointer](http://java-native-access.github.io/jna/5.6.0/javadoc/com/sun/jna/Pointer.html) 类来对应。JNA 的具体使用过程可参考：
- https://github.com/java-native-access/jna/blob/master/www/GettingStarted.md
- http://java-native-access.github.io/jna/5.6.0/javadoc/overview-summary.html

上述 GettingStarted 中第三种加载动态库的方式（即 resources 下的 `{OS}-{ARCH}/{LIBRARY}` 目录内）可以把动态库一起打包到 jar 中，这对于提供基础类库时比较方便，用户不需要再额外配置。
```
resources/
├── darwin
│   └── libawesome.dylib
├── linux-x86-64
│   └── libawesome.so
```

[vladimirvivien/go-cshared-examples](https://github.com/vladimirvivien/go-cshared-examples) 这个仓库演示了四个函数 Add/Cosine/Sort/Log 的 JNA 调用，但这四个函数的返回类型都是基本类型（int/float64），没有 string/slice 等复杂类型，因此这里通过五个示例讲述复杂类型的返回问题：
1. [BadStringDemo.java](https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/src/main/java/net/liujiacai/cgojna/BadStringDemo.java) 本示例演示了网络上一种常见，但有内存泄露问题的返回 string 的方式
2. [GoodStringDemo.java](https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/src/main/java/net/liujiacai/cgojna/GoodStringDemo.java) 这个示例演示了如何正确的返回 string
3. [AutoClosableStringDemo.java](https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/src/main/java/net/liujiacai/cgojna/AutoClosableStringDemo.java)  本示例在 GoodStringDemo 的基础上，利用 [AutoCloseable](https://docs.oracle.com/javase/8/docs/api/java/lang/AutoCloseable.html) 与 [try-with-resource](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html) 特性来释放内存
4. [ReturnByteSliceDemo.java](https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/src/main/java/net/liujiacai/cgojna/ReturnByteSliceDemo.java) 本示例演示如何返回 slice，以及如何在 Java 中处理 Go 中的多个返回值
5. [ReturnInterfaceDemo.java](https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/src/main/java/net/liujiacai/cgojna/ReturnInterfaceDemo.java) 本示例演示返回具有 Go Pointer 的结构时的报错行为

上述示例均使用 [direct mapping](https://github.com/java-native-access/jna/blob/master/www/DirectMapping.md) 的方式做 JNA，读者可参考 [vladimirvivien/go-cshared-examples](https://github.com/vladimirvivien/go-cshared-examples) 学习 interface mapping 的使用方式。
这里对两种映射方式做了简单的[性能测试]( https://github.com/jiacai2050/blog-snippets/blob/master/cgo-jna-demo/README.org#benchmark)，压测数据如下

| Method | input              | output         | which is better   | rate   |
|------ |------------------ |-------------- |----------------- |------ |
| Add    | two primitive ints | int            | direct-mapping    | 1.38   |
| Hello  | string             | FreeableString | interface-mapping | 1.169  |
| Hello2 | string             | Pointer        | direct-mapping    | 1.0083 |


结论就是
> direct-mapping 对于基本类型（包括 Pointer）性能更好，interface-mapping 在复杂类型上略优。

原因可参考：https://stackoverflow.com/a/38081251

# 总结

C 语言作为连接不同高级语言的胶水语言，不具备垃圾回收功能，所以开发者在做 JNA 时要注意回收无用的内存结构。

# 参考
- https://stackoverflow.com/questions/58759399/does-jna-free-memory-of-go-cstring-return-value
- https://stackoverflow.com/questions/48267403/returning-const-char-from-native-code-and-getting-string-in-java/48270500
- https://github.com/java-native-access/jna/blob/master/www/DirectMapping.md
- https://documentation.help/Golang/cgo.html
- https://docs.yottadb.com/Presentations/DragonsofCGO.pdf
- https://stackoverflow.com/questions/48686763/cgo-result-has-go-pointer
