title: 辨析 Ruby 中的 Method 与 Proc
date: 2017-03-05 15:26:28
categories: [编程语言]
tags: [Ruby]
toc: true
---

> Ruby is simple in appearance, but is very complex inside, just like our human body.  
>> -- Matz  https://www.ruby-lang.org/en/about

Ruby 与 Python、Scala 类似，在一切皆是对象（Seeing Everything as an Object）的基础上，支持函数式编程，这意味着函数是一等成员，可以作为参数传入，也可以作为函数值返回。

但是，Ruby 中的函数并没有其他动态语言中那么简单，它提供了 [Method](http://ruby-doc.org/core-2.4.0/Method.html) 与 [Proc](http://ruby-doc.org/core-2.4.0/Proc.html) 两个类来表示函数的概念，对于这两个类的区别无论是官方文档还是 Stackoverflow 上的问题，解释的都非常模糊。在其他语言函数很习以为常的用法在 Ruby 中却行不通，就其原因还是不清楚这两个类的区别，希望这篇文章能够帮助大家理解好 Ruby 中的“函数”概念，做到深入浅出，与其他函数式语言融会贯通。

## Block-oriented Programming

Ruby 中代码块最常见的形式既不是 Proc 也不是 Method，而是 `block`。比如：
```
# 遍历 Range/Array 等
(0..10).each do |num|
    puts num
end

#  读取文件
File.foreach('README.md').with_index do |line, line_num|
  puts "#{line_num}: #{line}"
end
#  遍历文件
Dir.glob('*.rb') {|ruby_src| puts "found #{ruby_src}"}
```
上面示例演示了`block`的两种字面量（literal）形式，非常方便简洁。但有一点需要注意，`block` 仅仅是 Ruby 提供的一语法糖衣，并不把其赋值给某一变量。如果自定义函数需要调用传入的`block`，需要采用`yield`方式。
```
# 在 Array 类中添加自定义函数
class Array
  def my_each
    0.upto(size) do |i|
      yield self[i]
    end
  end
end

%w(a b c).my_each do |item|
  puts item
end
```

## 面向函数式的 Proc

`block` 的优势是简洁，但是有个缺点就是无法复用，因为并不存在`block`类型。但在其他语言中，函数名可以随意传递，下面举一 Python 的例子：
```
def myinc(x):
	return x + 1

map(myinc, [1,2,3]) # => [2, 3, 4]
map(myinc, [4,5,6])	# => [5, 6, 7]
```
Ruby 中与其对应的是`过程`（Proc），与上面功能等价的 Ruby 代码为：
```
myinc = Proc.new {|num| num + 1}
# 或下面两种方式
# myinc = proc {|num| num + 1}
# myinc = lambda {|num| num + 1}

[1,2,3].map(&myinc)

```
上面代码最关键的是`&myinc`中的`&`，由于 map 函数后面可以跟一个 block，所以需要把 Proc 转为 block。
> 当`&`符号出现在函数参数列表中时，会把其后面的参数转为 Proc，并且把转化后的参数作为 block 传递给调用者。
>> http://stackoverflow.com/a/9429972/2163429

我这里有个更好的理解大家可以参考：

> `&`在C语言中为取地址符，Ruby 中的函数参数后面可以跟一个 block，由于这个 block 不是参数的一部分，所以没有名字，这很理所当然可以把 block 理解为一内存地址，`block_given?` 函数可以检查这个`block`是否存在。`&myinc` 可以理解为取 Proc 的地址传给 map 函数。

```
[1,2,3].map(myinc)
# 这种写法会报下面的错误
# in `map': wrong number of arguments (given 1, expected 0) (ArgumentError)

```

所以，Ruby 中的 Proc 和其他动态语言的函数是等价的，下面再举一例说明
```
def myfilter(arr, validator)
  arr.each do |item|
    if validator.call(item)
      puts item
    end
  end
end

myfilter([1,2,3,4], lambda {|num| num > 3})  # 输出 4

# 此外， 还可以在定义 myfilter 时，利用 & 将最后的 block 转为 Proc

def myfilter(arr, &validator)
  arr.each do |item|
    if validator.call(item)
      puts item
    end
  end
end

myfilter([1,2,3,4]) {|num| num > 3}
# 输出 4
```
### proc vs. lambda

上面介绍过，Proc 有两种字面量形式：
```
myinc = proc {|num| num + 1}   # 与 Proc.new 等价
myinc = lambda {|num| num + 1}
```
这两种形式的 Proc 有以下两点不同：
1. `proc`形式不限制参数个数；而`lambda`形式严格要求一致
    ```
    myadd = proc {|x, y| puts x}

    myadd.call(1)        # ok
    myadd.call(1, 2)     # ok
    myadd.call(1, 2, 3)  # ok


    myadd = lambda {|x, y| puts x}

    myadd.call(1)        # ArgumentError
    myadd.call(1, 2)     # ok
    myadd.call(1, 2, 3)  #ArgumentError
    ```

2. `proc`中的`return`语句对调用方有效；而`lambda`仅仅对其本身起作用
    ```
    def foo(some_proc)
      some_proc.call
      puts "foo over"
    end

    # 1. 正常输出 in lambda、foo over
    foo(lambda do
      puts "in lambda"
      return
    end)
    # 2. 输出 in new 后报  unexpected return (LocalJumpError)
    foo(Proc.new do
      puts "in new"
      return
    end)
    # 3. 输出 in proc 后报  unexpected return (LocalJumpError)
    foo(proc do
      puts "in proc"
      return
    end)
    ```

## 面向对象的 Method

Ruby 中使用`def`定义的“函数”为`Method`类型，专为面向对象特性设计，面向对象更一般的说法是消息传递，通过给一对象发送不同消息，对象作出不同相应，这一点与 [SICP 第三章](/blog/2015/12/26/sicp-chapter3-summary/#用变动的数据做模拟)的内容不谋而合。

```
class Rectangle
  def initialize(width, height)
    @width = width
    @height = height
  end
  def area
    @width * @height
  end
end

rect = Rectangle.new 10, 20
# 传统方式
puts rect.area
# 消息传递方式
puts rect.send :area
```
由于 Ruby 中方法名表示的是调用，所以一般可用与方法同名的 [Symbol](http://ruby-doc.org/core-2.4.0/Symbol.html) 来表示。
```
puts rect.method(:area)

#<Method: Rectangle#area>    
```

可以通过 `Method` 的 `to_proc` 方法可以将 Method 转为功能等价的 Proc。比如：

```
def myinc(num)
  num + 1
end

[1,2,3].map(&method(:myinc).to_proc)
# => [2,3,4]
# 在 Ruby 源文件的顶层定义的函数属于 main 对象（Object 类），所以上面的调用相当于：
# [1,2,3].map(&Object.method(:myinc))
```
通过 `define_method` 可以将 Proc 转为某对象的实例方法
```
class Foo
  define_method :pp { puts "p" }
end
Foo.new.pp
=> p
```


## 总结

- `block` 为 Proc 的语法糖衣，用于单次使用时
- `Proc` 专为函数式编程设计，与其他动态语言的函数等价
- `Method` 专为面向对象设计，消息传递的第一个参数

弄清 Method 与 Proc 的区别后，不得不欣赏 Ruby 语言设计的巧妙，兼具函数式与面向对象的精髓。实在是程序员必备利器。

## 参考

- https://en.wikibooks.org/wiki/Ruby_Programming/Syntax/Method_Calls
