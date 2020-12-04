---
categories:
- 编程语言
date: 2016-05-28 20:44:34
tags:
- Python
- JavaScript
title: 编程语言中的变量作用域与闭包
---

如果你写过 javascript，应该听说过[变量提升](https://en.wikipedia.org/wiki/JavaScript_syntax#hoisting)（hoisting），如果你自诩“Life is short, I use Python”，那么多多少少会用过`global`、`nonlocal`这两个关键字。无论新手还是老手，遇到这些时都会觉得很别扭，稍不留神就会出现意想不到的 bug，如果你仔细观察就会发现，它们其实是一个问题：变量作用域的问题。

其次，随着函数式编程的日趋火热，[闭包](https://en.wikipedia.org/wiki/Closure_%28computer_programming%29)逐渐成为了 buzzword，但我相信没几个人（希望你是那少数人）能够准确概括出闭包的精髓，而其实闭包这一概念也是解决变量作用域问题。

这篇文章首先介绍作用域相关的知识，主要是比较 dynamic scope 与 static(或lexical) scope 语言的优劣势；然后分析 Python 中为什么需要`global`和`nonlocal`，Javascript 为什么有`变量提升`，我这里不仅仅是介绍what，更重要的是why，要知道这两门语言的设计者都是深耕CS领域多年的老手，不会轻易犯错的，肯定有“不为人知”的一面，但遗憾的是网上大部分文章就是解释what，很少有涉及到why的，希望我这篇文章能够填充这一空缺；最后介绍闭包这一重要概念。

## 作用域

简单来说，作用域限定了程序中变量的查找范围。

在编程语言中有子过程（subroutine，也称为函数、过程）之前，所有的变量都在一个称为“global”的环境中，现在来看这当然是非常不合理，所以在之后有子过程的大部分静态语言（变量的类型不可变）里面，不同的 block（像if、while、for、函数等），具有不同的环境。例如：
```c
#include <stdio.h>

int main() {
    if(1 == 1) {
        int i = 1;
    } else {
        int i = 2;
    }
    printf("i = %d\n", i);  // error: use of undeclared identifier 'i'
    return 0;
}
```
上面代码片段是一简单的 C 语言程序，在执行 if 代码块时，会新创建一个环境（称为E1，其外围环境为全局环境E0。见下图），然后在 E1 中定义变量`i`，在 if 代码块结束后，E1 这个环境就会被删除，这时 main 函数后面的程序就无法访问 if 代码块的变量了。
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2SPDZpFXXXXaVXXXXXXXXXXXX_!!581166664.png" alt=" if 代码块示意图"/>
</center>

上面这一做法符合我们的直观印象，也是比较合理的设计。但是在一些动态语言（变量的类型可以任意改变）中，并没有变量声明与使用的区别，而是在第一次使用时去声明这个变量，像下面这个 Python 示例：
```python
if 1 == 1:
    i = 1
else:
    i = 2

print i  # 输出 1
```

在 Python 中，执行 if 代码块时不会去创建新的环境，而是在 if 代码块所处的环境中去执行。

根据我目前所了解到的：
- 静态语言（C、Java、C#等）具有块级别（block level，包含if、while、for、switch、函数等）的变量作用域；
- 动态语言（Javascript、Python、Ruby等）只具有函数级别（function level）的变量作用域

### dynamic scope vs. static scope

首先声明一点，这里的dynamic与static是指的变量的作用域，不是指变量的类型，与动态语言与静态语言要区分开。

在上面我们了解到，所有的高级语言都具有函数作用域。我们一般是这样使用函数的，先声明再使用，也就是说函数的声明与使用是分开的，这就涉及到一个问题，函数作用域的外围环境是声明时的还是运行时的呢？不同的外围环境对应不同的语言：

- dynamic scope 的语言，函数作用域的外围环境是`运行时`
- static scope 的语言，函数作用域的外围环境是`声明时`

看下面这个 Python 示例：
```python
    # foo.py
    s = "foo"
    def foo():
        print s

    # bar.py
    from foo import foo
    s = "bar"
    foo()   # 输出 foo
```
上面的示例包括两个文件：`foo.py`、`bar.py`，在`bar.py`中调用`foo.py`的`foo`函数，因为 Python 属于 static scope 的语言，所以这时的环境是这样的：
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2yp6lpFXXXXXAXFXXXXXXXXXX_!!581166664.png" alt=" 在 bar 中调用 foo 函数时的环境示意图"/>
</center>
在调用 foo 时，会创建一新环境E1，E1 虽然是在 bar 的全局环境中创建的，但是其外围指向的是 foo 的全局环境。在执行 foo 函数时，变量的查找顺序是这样的：
1. 首先在 E1 中找到，找不到就会去其外围环境中去查找；找到则直接返回
2. 在E1外围环境中查找，如果找到直接返回，如果找不到则再在外围环境的外围环境中继续查找，止到外围环境为空（foo、bar 模块的全局环境的外围指向均为空）
3. 去语言内置的变量中去查找，找到则直接返回；找不到就会报错。

static scope 是比较符合正常思维的，也是比较正确的实现方式，否则我们在使用第三份类库时，很容易就会发生变量冲突或覆盖的情况。采用 dynamic scope 的语言都是比较古老的，现在还比较常见的是 Shell，想想大家在写 Shell 时是多痛苦就知道 dynamic scope 是多么反人类了。

## JavaScript 中的变量作用域

就像前面说的，Javascript 具有 function level 的 static scope，但是这里有一个常见的问题，具体代码：

```js
var list = document.getElementById("list");

for (var i = 1; i <= 5; i++) {
    var item = document.createElement("li");
    item.appendChild(document.createTextNode("Item " + i));

    item.onclick = function(ev) {
        alert("Item " + i + " is clicked.");
    };
    list.appendChild(item);
}
```
你也许会想当然的认为依次单击时每个Item会依次显示1,2,3...，但其实这里无论你单击那个Item，都只会显示6，你可以去 [JSFiddle](https://jsfiddle.net/jiacai2050/w6agke9d/) 测试下。
究其原因，就是因为每个item click 所对应的回调函数的声明与执行是分开的，而且 Javascript 中只有 function level 的作用域，所以在单击Item时的环境是这样的：
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2YEkppFXXXXXbXXXXXXXXXXXX_!!581166664.png" alt=" 使用 var 定义 i 时，单击 Item 时的环境模型示意图"/>
</center>
在 for 代码块执行完后，`i` 的值为6，又因为Javascript 中只有 function level 的作用域，所以这里的 `i` 被定义在了 E0 中。

为了解决这个问题，ES6 引入了`let`，使用`let`定义的变量具有 block level 的作用域，所以如果把上面的代码片段中的`var`换成`let`，环境会变成下面的形式：
<center>
<img src="https://img.alicdn.com/imgextra/i2/581166664/TB29sDTpFXXXXXpXpXXXXXXXXXX_!!581166664.png" alt=" 使用 let 定义 i 时，单击 Item 时的环境模型示意图"/>
</center>
相信大家通过上面的图示，可以解决心中的疑惑了。最后，给出一个思考，下面的代码片段输出什么值：
```js
var a = "before";
function foo(){
    console.log(a);
}
function bar(fun){
    var a = "after";
    fun();
}
bar(foo);   // 输出 ？
```

### hoisting

先看一个比较典型的例子：
```js
var foo = 1;
function bar() {
    if (!foo) {
        var foo = 10;
    }
    alert(foo);
}
bar();
```
你也许知道，这里弹出的值是10，而不是1，因为javascript会把所有的变量提前（hositing），也就是说，上面的代码等价于：
```js
var foo = 1;
function bar() {
    var foo;
    if (!foo) {
        foo = 10;
    }
    alert(foo);
}
bar();
```
上面这个例子就简单演示了什么是变量提升，下面重点讲述为什么要这么设计？首先看下面一段代码：
```js
function is_even(n) {
  if (n == 0) {
    return true;
  } else {
    return is_odd(n - 1);      
  }

}

is_even(2); // true

function is_odd(n) {
  if (n == 0) {
    return false;
  } else {
    return is_even(n - 1);      
  }
}

```

按照常规思维，在运行`is_even(2);` 时，会去调用还没定义的`is_odd`函数，所以应该会报错，但是由于 Javascript 里面有 hositing，所以是可以运行，但是为什么要这么设计呢？
这要追溯到 Javascript 语言设计者的初衷了，Brendan Eich 在创造这门世界级语言时，一开始打算用 Scheme 的思想来实现，而且当时 Brendan 也是在看 SICP 这本书，[SICP 4.1.6](https://mitpress.mit.edu/sicp/full-text/book/book-Z-H-26.html#%_sec_4.1.6) 在介绍内部定义时，给出了解决变量同一时刻定义的一种解决方式：将所有的变量名提前。这样同一环境中的其他地方就能够使用所有的定义了。需要注意的是，这里只是将变量名提前，赋值的动作不变，显然，Javascript 采用了这一思想（这其实是[forward_declaration](https://en.wikipedia.org/wiki/Forward_declaration) 技术的一种实现手段）。
```lisp
;; SICP 书中的示例代码
(lambda <vars>
  (define u <e1>)
  (define v <e2>)
  <e3>)
;; 转为下面的形式
(lambda <vars>
  (let ((u '*unassigned*)
        (v '*unassigned*))
    (set! u <e1>)
    (set! v <e2>)
    <e3>))  
```

这个问题有人在 Twitter [问过 Brendan 这个问题](https://twitter.com/BrendanEich/status/33403701100154880)，Brendan是这么回答的：

> Function declaration hoisting is for mutual recursion & generally to avoid painful bottom-up ML-like order

对 Javascript 历史感兴趣的同学可以看看 Brendan 本人的自述：

- https://brendaneich.com/2011/06/new-javascript-engine-module-owner/

## Python 中的变量作用域

准确来说，Python 里面有四种作用域：`function`, `module`, `global`和 `class` 作用域。由于 Python 不区分变量的声明，所以在第一次初始化变量时（必须为赋值操作）将变量加入当前环境中。如果在没对变量进行初始化的情况下使用该变量就会报运行时异常，但如果仅仅是访问（并不赋值）的情况下，查找变量的顺序会按照 LEGB 规则 (Local, Enclosing, Global, Built-in)。

```python
s = "hello"
def foo():
    s += "world"
    return s

foo()  # UnboundLocalError: local variable 's' referenced before assignment    
```
由于在函数 foo 中在没有对 s 初始化的情况下使用了该值，所以这里会报异常，解决的办法就是使用 global 关键字：
```
s = "hello"
def foo():
    global s
    s += " world"
    return s

foo()  # return "hello world"
```
但由于 global 关键字只能限定在`global`作用域内查找变量，在有嵌套定义的时候就有问题了，比如：
```python
def foo():
    s = "hello"
    def bar():
        global s     # NameError: global name 's' is not defined
        s += " world"
        return s
    return bar

foo()()    
```
Python 3 中引入了 `nonlocal` 关键字来解决这个问题，：
```python
def foo():
    s = "hello"
    def bar():
        nonlocal s
        s += " world"
        return s
    return bar

foo()()   # return "hello world"
```
在 Python 2 中，我们可以通过引入一可变容器解决（其实就是绕过直接修改 `s` 的值）
```python
def foo():
    s = ["hello"]
    def bar():
        s[0] += " world"
        return s[0]
    return bar

foo()()   # return "hello world"
```

### 类级别作用域

还是先看代码：
```python
class Foo(object):
    username = "Foo"
    def say_hello(self):
        print "Hello %s" % username

foo = Foo()
foo.say_hello()  # NameError: global name 'username' is not defined                
```
`username`是定义在`Foo`类级别的，内部的`say_hello`方法在查找自由变量`username`的作用域会按照上面说的LEGB 规则 (Local, Enclosing, Global, Built-in)，并不会去查找类级别作用域的变量，所以这里会报错。修改的方法也很简单：
```python
def say_hello(self):
    print "Hello %s" % Foo.username
```
可以看到，Python 在试图省略掉变量声明的同时，反而造成了更复杂的情况，相关讨论在 Python mail-list 里面讨论也很火热，有兴趣的读者可以参考：
- [PEP 3104 -- Access to Names in Outer Scopes](http://legacy.python.org/dev/peps/pep-3104/)


## 闭包

还是先看一个例子：

```js
function add(x) {
  return function(y) {
    return x + y;
  }
}
var add3 = add(3);
alert(add3(4));  // return 7
```
这里的`add3`就是一闭包对象，它包括两部分，一个`函数`与声明函数时的`环境`。这就是闭包的核心，没有任何神奇的地方，闭包就是解决自由变量作用域的问题。

## 参考

- [JavaScript Scoping and Hoisting](http://www.adequatelygood.com/JavaScript-Scoping-and-Hoisting.html)
- [Note 4. Two words about “hoisting”](http://dmitrysoshnikov.com/notes/note-4-two-words-about-hoisting/)
- [ES6 In Depth: let and const](https://hacks.mozilla.org/2015/07/es6-in-depth-let-and-const/)
- [The Python Language Reference 4. Execution model](https://docs.python.org/3.5/reference/executionmodel.html#interaction-with-dynamic-features)
