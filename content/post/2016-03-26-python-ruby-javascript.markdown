title: python, ruby, javascript 浅析
date: 2016-03-26 17:03:40
categories: [编程语言]
tags: [Python, Ruby, JavaScript]
---

最近一直在看红宝石（ruby）语言，到现在为止，算是对其设计有一些了解。作为一动态语言，ruby 经常会拿来与 python 对比，确实这两门语言在语法层面、实现层面有很多共同的地方，但是它们也在很多设计理念上存在重要差异，通过对比这些相同点、异同点，更加有助于理解这两门语言。同时，Node.js、React Native 的出现，将 javascript 这门“前端”语言推向了全栈，同样作为一门动态语言，javascript 与 ruby、python 在很多概念上也存在很多相同点、异同点。

本篇文章着重从编程语言设计的角度进行阐述，希望对编程语言爱好者理解这三门语言有所帮助，做到融会贯通。

<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2kVcxcByN.eBjSZFgXXXmGXXa_!!581166664.png" alt=" js_python_ruby"/>
</center>

## 讨论范围

Python、Ruby、Javascript(ECMAScript) 准确说是一种语言规范，规范可以有多种实现，这体现在不同的解释器上。
- Python 的解释器主要有 CPython、IronPython、Jython、PyPy
- Ruby 的解释器主要有 Ruby MRI(CRuby)、JRuby、MacRuby、IronRuby
- Javascript 的解释器主要有 Chakra, SpiderMonkey, V8

本文主要讨论的是 CPython、CRuby，它们是其语言作者亲自设计的，也是应用场景最广的。
Javascript 在语言设计之初根本没考虑到其应用范围会如此之广，所以相比其他语言，它语言内置的功能要弱很多，[ES6](http://es6-features.org/) 的出现就是为了解决这个问题，本文所涉及的 javascript 运行在基于 V8 引擎的 Node.js 中，且具备 ES6 语法。

## 语言定义

首先看一下 wikipedia 上对这三门语言的定义：
- Python is a widely used `high-level`, `general-purpose`, `interpreted`, `dynamic` programming language
- Ruby is a `dynamic`, `reflective`, `object-oriented`, `general-purpose` programming language.
- JavaScript is a `high-level`, `dynamic`, `untyped`, and `interpreted` programming language.

其实上面标红的关键字对于这三门语言来说都适用，只是每个语言的强调点不一样而已。

通常会称这三门语言为`动态语言`，支持`函数式`、`面向对象`两种编程范式，这两点其实是最重要的。

## 设计理念

`既轻量又强大`是大多数动态语言相通的设计理念，关于 javascript 设计理念更多的介绍可以参考我的[这篇文章介绍](http://liujiacai.net/blog/2015/02/01/javascript-oop/#设计理念)。至于 Python 与 Ruby 设计理念的区别，一句话即可概括：
- Python: 一件事情只有一种方法做
- Ruby: 一件事情有多种方法做

比如，Python 中 Tuple, Array, String 没有相应获取大小的方法，而是提供了统一的`len`来解决这个问题
```
>>> len([1,2])
2
>>> len("hello world")
11
>>> len((1,2))
2
```
至于 Ruby 的`一件事情有多种方法做`的理念，后面我在讲解 lambda 与字符串拼接时再介绍。

## 语法

如果你之前没接触过 ruby、python 的语法，推荐先去了解下：
- 官方文档 [Ruby in Twenty Minutes](https://www.ruby-lang.org/en/documentation/quickstart/)
- [Ruby Essentials](http://www.techotopia.com/index.php/Ruby_Essentials)，两个小时绝对看完了
- [python 最佳实践](http://python-best-practice.liujiacai.net)，应该用不了半个小时

javascript 实在是太简单了，就不用特别看了。

综合来说，python、javascript 还是比较中规中矩的，即使 ES6 里面加了[很多花哨的语法糖衣](https://github.com/lukehoban/es6features)，但是也比较直观，但是 ruby 这个语言就比较变态了，各种符号，像`class Son < Father`表示类的基础，`"hello" << " world"`表示字符串的拼接，`@var`表示对象的成员变量，`@@var`表示类的成员变量，`$var`表示全局变量。

而且在 ruby 中，方法调用时的括号可有可无，即使有参数也可以省略：
```
> def add(a, b)
>     a + b
> end
>
> add 1, 2
=> 3
```
如果你对 Scheme 熟悉，上面的代码还能像下面这么写，是不是很亲切
```
> (def add a, b
>     a + b
> end)

> (add 1, 2)
=> 3
```
这也就是充分说明，括号在 ruby 中只是起到了“分割”的作用，并没有什么语法含义。

### 面向对象

面向对象主要的核心是用`对象`来达到数据封装的目的。
- javascript 基于原型链实现面向对象，更详细的介绍可以参考[《javascript中的面向对象编程》](http://liujiacai.net/blog/2015/02/01/javascript-oop/)
- python、ruby 基于类来实现面向对象，和 java 类似，但是更纯粹些。

```
$ python
>>> def func(): return 1
>>> type(func)
<type 'function'>
>>> func2 = lambda x: x
>>> type(func2)
<type 'function'>
>>> type(1)
<type 'int'>
>>> dir(1)
['__abs__', '__add__', .....]
#--------------------------------------------------#
$ irb
> def add(a, b)
>    a + b
> end
> method(:add)
=> #<Method: Object#add>
# 上面 ruby 的例子中，使用了 Symbol 来表示 add 方法，这是由于 ruby 中直接写 add 表示函数调用
> 1.methods
=> [:%, :&, :*, :+, :-, :/, .....]
```

可以看到，在 python、ruby 中，像`1`这样的数字字面量也是对象。


### lambda 表达式

lambda 表达式表示的是匿名函数。由于在这三门语言中，函数均是一等成员，所以可以很方便的进行函数式编程
```
$ node
> [1,2,3].map((x) => x + 1)
[ 2, 3, 4 ]
#--------------------------------------------------#
$ python
>>> map(lambda x: x+1, [1,2,3])
[2, 3, 4]
#--------------------------------------------------#
$ irb
> [1,2,3].map &(lambda {|x| x+1})
 => [2, 3, 4]
```

Python 的 lambda 表达式是这三者中最弱的一个，只能包含一个表达式，javascript 与 ruby 的则没有这种限制。

细心的读者会发现上面 ruby 版本的 lambda 前有个`&`，这是必须的，否则会报下面的错误
```
ArgumentError: wrong number of arguments (given 1, expected 0)
```

这是因为在 ruby 中，方法除了接受参数外，还可以接受一个代码块(block)，代码块在 ruby 中有两种写法：
- 一行的话用`{}`
- 多行的话用`do ... end`    
```
> [1,2,3].each { |num| print "#{num}! " }
1! 2! 3!
=>[1,2,3]
> [1,2,3].each do |num|
>    print "#{num}!"
> end
1! 2! 3!
 =>[1,2,3]         # Identical to the first case.
```
`&` 的作用是告诉解释器，现在传入的不是正常的参数，而是一个代码块。这个传入的代码块在方法内通过`yield`进行调用。这里可以做个演示：
```
class Array
  def my_each
    i = 0
    while i < self.size
        yield(self[i])  
        i+=1      
    end
    self
  end
end

> [1,2,3].my_each { |num| print "#{num}!" }
1! 2! 3!
=> [1,2,3]
```

Ruby 中 lambda 表达式属于 [Proc 类型](http://ruby-doc.org/core-2.2.0/Proc.html)，
```
> lambda {|x| x}.class
=> Proc
```

这里可以看到，只是对于闭包的支持，Ruby 就提供了多种方案。更多可以参考：

- [Ruby Explained: Blocks, Procs, and Lambdas, aka "Closures"](http://www.eriktrautman.com/posts/ruby-explained-blocks-procs-and-lambdas-aka-closures)
- [Weird Ruby Part 4: Code Pods (Blocks, Procs, and Lambdas)](https://blog.newrelic.com/2015/04/30/weird-ruby-part-4-code-pods/)

### yield

就像上面说的，ruby 中 `yield` 就是表示代码块的调用，没有其他含义。而在 python 与 javascript `yield` 是用来构造[生成器（generator）](https://wiki.python.org/moin/Generators)的，都是用来控制程序运行流程，相当于用户态的“线程”：
```
$ python
def iter():
    for x in xrange(10):
        yield x

foo = iter()
print next(foo)
print next(foo)
#--------------------------------------------------#

$ node
function* iter() {
 for (var i = 0; i < 10; i++)
    yield i
}
var foo = iter()
console.log(foo.next().value)
console.log(foo.next().value)

```
上面两份代码都依次打印出`0`, `1`。

关于生成器的更多资料，可以参考：
- [Generators in Node.js: Common Misconceptions and Three Good Use Cases](https://strongloop.com/strongblog/how-to-generators-node-js-yield-use-cases/)
- [More details on Python generators and coroutines](http://www.dabeaz.com/coroutines/Coroutines.pdf)（强烈推荐 Python 读者看）

在 ruby 中，与生成器对应的概念是 [Fiber](http://ruby-doc.org/core-2.2.0/Fiber.html)，例如：
```
iter = Fiber.new do
  (0..10).each do |x|
    Fiber.yield x
  end
end

puts iter.resume
puts iter.resume
```
上面的代码也依次打印出`0`, `1`。

关于生成器与 Fiber 的关系，可以参考：
- [Overview of Modern Concurrency and Parallelism Concepts](https://nikolaygrozev.wordpress.com/2015/07/14/overview-of-modern-concurrency-and-parallelism-concepts/comment-page-1) （需翻墙，强烈推荐读者看）
- http://merbist.com/2011/02/22/concurrency-in-ruby-explained/

其实，生成器、Fiber 以及相关概念背后的理论基础是 [continuation](https://en.wikipedia.org/wiki/Continuation)，continuation 的应用场景非常广泛，各种编程语言中的[异常处理](https://en.wikipedia.org/wiki/Exception_handling)也是基于它来实现的。鉴于这个话题比较大，这里不再展开叙述，感兴趣的读者可以参考[这篇文章](http://matt.might.net/articles/programming-with-continuations--exceptions-backtracking-search-threads-generators-coroutines/)，后面我也会单独再写一篇文章进行介绍。
这里仅仅给出 continuation 的一个简单示例以飨读者：
```
; Scheme 语言中没有 return 语句，利用 continuation 可以模拟 return
(define (f return)
  (return 2)
  3)

(display (f (lambda (x) x))) ; displays 3
(display (call-with-current-continuation f)) ; displays 2
```
关于这里例子详细的解释可以参考[WIKI Call-with-current-continuation](https://en.wikipedia.org/wiki/Call-with-current-continuation#Examples)。



### 字符串

#### immutable vs mutable
[字符串](/blog/2015/11/20/strings/)作为对字符的一种抽象，实现时有两种选择：可变的与不可变的。这两种实现的优缺点如下：
- 可变的字符串，这意味着对字符串进行修改、追加等操作时可在原有字符串基础上直接操作，比较节省空间。但是可变的特点会导致如下几个问题：
    - 相等性（equality）。如果一个对象是可变的，我们应该如何判断两个对象是相等的呢？这里还有个容易混淆的概念：同一性（identity），同一性是指两个变量指向同一个对象，相等性指两个变量指向不同的两个对象，但这两个对象的值是一样的。
        ![string_identity_equal](https://img.alicdn.com/imgextra/i3/581166664/TB29NApmFXXXXbvXpXXXXXXXXXX_!!581166664.png)

    - 并发性（concurrence）。在多线程的环境中，需要对可变对象进行各种复杂的锁机制来保障其正确性。

- 不可变字符串没有上面的两个问题，但是不可变字符串在进行修改时由于会新生成一个对象，所以会比较消耗空间，所以这采用不可变字符串实现的语言一般都会提供一个具备 buffer 的字符串构造对象来生成字符串，像 Java 中的 [StringBuffer](https://docs.oracle.com/javase/7/docs/api/java/lang/StringBuffer.html)，Python 中的 [StringIO](https://docs.python.org/2/library/stringio.html)。

Ruby 中字符串是`可变`的，但是 Ruby 中提供了不可变字符串的替代品 Symbol，而且 Ruby 2.3 也提供了`--enable-frozen-string-literal` 选项用以声明字符串是不可变的。具体可参考：

- https://wyeworks.com/blog/2015/12/1/-strings-in-ruby-2-dot-3

```
$ irb
> "a".equal? "a"   # equals?--- identity comparison
 => false
> "a".eql? "a"     # eql?   --- hash equality
 => true
> "a" == "a"       # ==     --- generic "equality"
 => true
> str = "hello"
 => "hello"
> str.__id__
 => 70099860517540
> "hello".__id__
 => 70099856137920
> str << " world"
 => "hello world"
> str.__id__
 => 70099860517540     # 与之前的 id 一样，说明 str 所指向的对象没变

> str = "hello"
 => "hello"
> str.__id__
 => 70099860630880
> str += " world"
 => "hello world"
> str.__id__
 => 70099856250160    # 与之前的 id 不一样，说明 += 在进行字符串拼接时，会生成一新对象
 ```
Python、Javascript 中字符串都是`不可变`的。

```
$ python
>>> str = "hello world"
>>> str2 = str.replace("o", "oo")
>>> str
'hello world'
>>> str2
'helloo woorld'

$ node
> str = "hello world"
'hello world'
> str2 = str.replace("o", "oo")
'helloo world'
> str
'hello world'
> str2
'helloo world'
```

#### 拼接

大多数语言都可以直接通过`+`进行字符串的拼接，但是这样做既不优雅，效率也低，所以一些语言会有些替代方案。
Ruby 与 Python 中对这块的支持比较强大，ES6 中借鉴了以上两门语言的语法，引入了 [template_string](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals)，这在极大程度上方便了字符串的拼接。
```
$ node
> var a = 5;
> var b = 10;
> console.log(`Fifteen is ${a + b} and\nnot ${2 * a + b}.`);
// "Fifteen is 15 and
// not 20."
#--------------------------------------------------#
$ python
> long_string = """
> my name is {username},
> my age is {age}
> """.format(username="zhangsan", age=10)
#--------------------------------------------------#
$ irb
> long_string = """
> my name is %{username},
> my age is %{age}
> """ % {username: "zhangsan", age:10}
```


就是上面不可变字符串缺点中说的，对字符串进行追加时效率比较低，那么在 Python 与 Javascript 中进行大量字符串拼接时该采用什么方式呢？下面给出我的两组测试：

##### Python

```
import time
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # StringIO is in package io in python 3

try:
    xrange
except NameError:
    xrange = range  # xrange is gone in python 3


def method1(loop_count):
    start = time.time()
    out_str = ''
    for num in xrange(loop_count):
        out_str += repr(num)

    print("+= : %f seconds" % (time.time() - start))
    return out_str


def method2(loop_count):
    start = time.time()
    str_list = []
    for num in xrange(loop_count):
        str_list.append(repr(num))
    out_str = ''.join(str_list)
    print("list + join : %f seconds" % (time.time() - start))
    return out_str


def method3(loop_count):
    start = time.time()
    out_str = ''.join([repr(num) for num in xrange(loop_count)])
    print("list comprehension + join : %f seconds" % (time.time() - start))
    return out_str

def method4(loop_count):
    start = time.time()
    file_str = StringIO()
    for num in xrange(loop_count):
        file_str.write(repr(num))

    out_str = file_str.getvalue()
    print("StringIO : %f seconds" % (time.time() - start))
    return out_str

loop_count = 1000000
method1(loop_count)
method2(loop_count)
method3(loop_count)
method4(loop_count)
```

下面给出统计结果

| python版本|+=| list + join| list comprehension + join| stringIO |
| ---------|---------|---------|---------|--------- |
| 2.7.6|0.181868| 0.219901| 0.194387| 1.085162 |
| 3.5.0|0.330583| 0.271803| 0.229952| 0.313573 |

从上面的比较可以看出，`list comprehension + join` 的方式时最快，而且写法也比较优雅的。

##### Javascript
```
function method1(loop_count) {
    var out_str = "";
    var start = Date.now()
    for (i=0;i<loop_count;i++) {
        out_str += i;
    }
    console.log(`+= cost : ${Date.now() - start} ms`);
    return out_str;
}
function method2(loop_count) {
    var arr = []
    var start = Date.now()
    for (i=0;i<loop_count;i++) {
        arr.push(i);
    }
    var out_str = arr.join("");
    console.log(`arr + join cost : ${Date.now() - start} ms`);
    return out_str;
}
function method3(loop_count) {
    var out_str = "";
    var start = Date.now()
    for (i=0;i<loop_count;i++) {
        out_str.concat(i);
    }
    console.log(`str.concat cost: ${Date.now() - start} ms`);
    return out_str;
}

var loop_count = 1000000;
method1(loop_count)
method2(loop_count)
method3(loop_count)

```

| |+=| arr + join| str.concat |
| ---------|---------|---------|--------- |
| 耗时（单位：ms）|199| 230| 126 |

上面的测试结果使用 Node v5.9.1 测试出来的，从结果来看，`str.concat` 是速度最快的。


### 查看值类型
动态语言最主要的特点就是`变量无类型`，利用[反射机制](https://en.wikipedia.org/wiki/Reflection_%28computer_programming%29)可以查看`运行时变量的值的类型`。
```
$ node
> str = "hello world"
> typeof str     
'string'
#------------------------------#
$ irb
> str = "hello world"
> str.class
String
#------------------------------#
$ python
> str = "hello world"
> type(str)
<type 'str'>
```

## 包管理

- Python，[PyPI](https://pypi.python.org/pypi)，多版本兼容推荐使用 [virtualenv](https://virtualenv.pypa.io) 管理
- Ruby， [GEMS](https://rubygems.org/)，多版本兼容，推荐使用 [rvm](https://rvm.io/) + [bundler](http://bundler.io/) 管理
- Node.js，由于 Node.js 出现较晚，它避免了Python、Ruby 包全局污染的问题，而是选择将第三份模块安装在项目内的`node_modules`文件夹内

## 总结


经过上面简短的介绍，我相信大家对这三门语言有了全面的理解，多了解一门语言，也就是多个解决问题的思路。

个人感觉，Python、Javascript 的语法比较中规中矩，适合大部分程序员学习。Ruby 更适合 geek 去学，因为它的很多奇特语法会让你思考语言的设计细节，而不仅仅是使用这么简单。

最近我在看[Ruby元编程](https://book.douban.com/subject/7056800/)，里面的很多内容就很有意思，一些内容在看 SICP 时就已经遇到，这种似曾相识的感觉很棒，我相信对编程语言的了解又加深了一步。谢谢 [Yukihiro Matsumoto](https://en.wikipedia.org/wiki/Yukihiro_Matsumoto)大叔，带给我们 ruby 这么美妙的语言。

## 参考

- http://stackoverflow.com/questions/7299010/why-is-string-concatenation-faster-than-array-join
- https://waymoot.org/home/python_string/
- https://wyeworks.com/blog/2015/12/1/immutable-strings-in-ruby-2-dot-3
- http://stackoverflow.com/questions/7156955/whats-the-difference-between-equal-eql-and
- http://stackoverflow.com/questions/214714/mutable-vs-immutable-objects
- https://kentreis.wordpress.com/2007/02/08/identity-and-equality-in-ruby-and-smalltalk/
