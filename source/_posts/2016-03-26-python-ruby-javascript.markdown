title: python vs. ruby vs. javascript
date: 2016-03-26 17:03:40
categories: 编程语言
tags: [python, ruby, javascript]
---

最近一直在看红宝石（ruby）语言，到现在为止，算是对其设计有一些了解。作为一动态语言，ruby 经常会拿来与 python 对比，确实这两门语言在语法层面、实现层面有很多共同的地方，但是它们也在很多设计理念上存在重要差异，通过对比这些相同点、异同点，更加有助于理解这两门语言。同时，Node.js、React Native 的出现，将 javascript 这门“前端”语言推向了全栈，同样作为一门动态语言，javascript 与 ruby、python 在很多概念上也存在很多相同点、异同点。

这篇文章将尝试介绍这三门语言的一些特点与不同点，让我们开始吧。

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
至于 Ruby 的`一件事情有多种方法做`的理念，后面我在讲解 lambda 时再介绍。

## 语法

如果你之前没接触过 ruby、python 的语法，推荐先去了解下：
- [Ruby Essentials](http://www.techotopia.com/index.php/Ruby_Essentials)，两个小时绝对看完了
- [python 最佳实践](python-best-practice.liujiacai.net)，应该用不了半个小时

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

lambda 表达式表示的是匿名函数，也就是我们通常说的闭包。由于在这三门语言中，函数均是一等成员，所以可以很方便的进行函数式编程
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
`&` 的作用就相当于告诉解释权，我们现在传入的不是正常的参数，而是一个代码块。这个传入的代码块在方法内通过`yield`进行调用。我们可以自己实现个`my_each`
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

 ruby 中 lambda 表达式属于 [Proc 类型](http://ruby-doc.org/core-2.2.0/Proc.html)，
```
> lambda {|x| x}.class
=> Proc
```
更多可以参考：
- [Ruby Explained: Blocks, Procs, and Lambdas, aka "Closures"](http://www.eriktrautman.com/posts/ruby-explained-blocks-procs-and-lambdas-aka-closures)
- [Weird Ruby Part 4: Code Pods (Blocks, Procs, and Lambdas)](https://blog.newrelic.com/2015/04/30/weird-ruby-part-4-code-pods/)

### yield

就像上面说的，ruby 中 `yield` 就是表示代码块的调用，没有其他含义。而在 python 与 javascript `yield` 是用来构造生成器（generators）的，只不过两门语言的语法略有区别，都是用来控制程序的运行流程，相当于用户态的“进程”：
```
$ python
def iter():
    for x in xrange(10):
        yield x

foo = iter()
print next(foo)
print next(foo)
#--------------------------------------------------#

$ node.js

function* iter() {
 for (var i = 0; i < 10; i++)
    yield i
}
var foo = iter()
console.log(foo.next().value)
console.log(foo.next().value)

```
上面两份代码都依次打印出`1`, `2`。

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
上面的代码也依次打印出`1`, `2`。

关于生成器与 Fiber 的关系，可以参考：
- [Overview of Modern Concurrency and Parallelism Concepts](https://nikolaygrozev.wordpress.com/2015/07/14/overview-of-modern-concurrency-and-parallelism-concepts/comment-page-1) （需翻墙，强烈推荐读者看）
- http://merbist.com/2011/02/22/concurrency-in-ruby-explained/

## 包管理

- Python，[PyPI](https://pypi.python.org/pypi)，多版本兼容推荐使用 [virtualenv](https://virtualenv.pypa.io) 管理
- Ruby， [GEMS](https://rubygems.org/)，多版本兼容，推荐使用[rvm](https://rvm.io/) + [bundler](http://bundler.io/) 管理
- Node.js，由于 Node.js 出现较晚，它避免了Python、Ruby 包全局污染的问题，而是选择将第三份模块安装在项目内的`node_modules`文件夹内

## 总结


经过上面简短的介绍，我相信大家对这三门语言有了全面的理解，多了解一门语言，也就是多个解决问题的思路。
个人感觉，Python、Javascript 的语法比较中规中矩，适合大部分程序员学习。Ruby 更适合 geek 去学，因为它的很多奇特语法会让你思考语言的设计细节，而不仅仅是使用这么简单，最近我在看[Ruby元编程](https://book.douban.com/subject/7056800/)，里面的很多内容就很有意思，一些内容在看 SICP 时就已经遇到，这种感觉很棒，我相信对编程语言的了解又加深了一步。谢谢 [Yukihiro Matsumoto](https://en.wikipedia.org/wiki/Yukihiro_Matsumoto) 带给我们 ruby 这么美妙的语言。
