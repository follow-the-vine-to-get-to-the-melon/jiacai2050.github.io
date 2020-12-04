---
title: javascript中的数据类型
date: 2015-02-24 21:09:45
categories: [编程语言]
tags: [JavaScript]
---

学一门编程语言，无非两方面：一是语法，二是数据类型。类C语言的语法不外乎if、while、for、函数、算术运算等，面向对象的语言再加上object。
语法只是语言设计者预先做的一套规则，不同语言语法不尽相同，但都有一些共通点，对于熟悉一两门编程语言的人，学其他的编程语言时，语法往往不是问题（当然，如果你一直学的是类C语言，那么首次接触lisp时肯定也要花些时间），学习的重点往往是数据类型及其相关操作上，不是有句老话：“数据结构＋算法＝程序”！其次，有些语言的语法本身就存在设计问题（javascript更甚），我们没必要深究这些点，当然，如果你自诩geek，可以把玩把玩。

本文将对javascript中的数据类型做一个详尽的介绍。

## 弱类型 vs 强类型

鉴于javascript的[设计理念](/blog/2015/02/01/javascript-oop/#设计理念)，javascript被设计成一种弱类型的语言。
说到这里，难免要说一下，弱类型与强类型的区别。
一些人会误以为这两者的差别就是“强类型的语言在声明一个变量时需要指明它的类型，而弱类型的则不用”。其实这种观点是错误的。比如下面这个Java代码片段：
```
String s = "hello";
int l = s.getBytes().length;
```
编译器是怎么知道`.length`是合法的表达式呢？这是因为编译器知道`s`的数据类型为`String`，当调用`String`的`getBytes`方法时，返回值的数据类型为`byte[]`，所以`.length`是合法的表达式。
这两者真正的区别是：  
> 在强类型的语言，每个表达式的类型都能够在编译时确定，并且只允许适用于该类型的操作；
> 弱类型的语言允许对任意类型施加任何操作，只是这个操作有可能在运行时报错。

## 数据类型

根据[ECMAScript 5.1](http://www.ecma-international.org/ecma-262/5.1/#sec-8)的规范，javascript中共有六种数据类型，分别为：`Undefined`, `Null`, `Boolean`, `Number`, `String`、`Object`。前五种属于基本类型，最后一种属于对象类型。

### 基本数据类型
- `Undefined`类型只有一个值，为`undefined`，意味着“空值(no value)”，适用于所有数据类型。
- `Null`类型只有一个值，为`null`，意味着“空对象(no object)”，只适用于对象类型。
- `Boolean`类型有两个值，为`true`与`false`
- `Number`类型的值是遵循IEEE 754标准的64位浮点数的集合，类似于Java的double。没有整型数据结构。此外还包含三个特殊的值：`NaN`、`Infinity`、`-Infinity`
- `String`类型的值是有穷个Unicode字符的集合。必须用`'`或`"`括起来。

#### 基本类型的string与对象类型的string区别
在javascript是区分基本类型的string与对象类型的string（Number、Boolean与之类似）。
- 使用字面量方式创建的字符串，为基本类型的string
- 使用`String()`创建的字符串，为基本类型的string
- 使用`new String()`的方式创建的字符串，为对象类型的string
```
str1 = "javascript"
str2 = String("javascript")
str3 = new String("javascript")

> typeof str1
"string"
> typeof str2
"string"
> typeof str3
"object"
```
javascript会在合适的时候自动把基本类型的string转为对象类型的string，也就是说我们可以对基本类型string使用`String.prototype`中的方法。这两者也可以进行显式转化。
```
// 基本类型----->对象类型
str1 = "javascript"
str1 = new String(str1)
> typeof str1
"object"
// 对象类型----->基本类型
str1 = new String("javascript")
str1 = str1.valueOf()
> typeof str1
"string"
```
这两者用在`eval`函数中时，结果有所区别：
```
var s1 = '2 + 2';
var s2 = new String('2 + 2');
> eval(s1)
4
> eval(s2)
[String: '2 + 2']   //这里还是返回的string对象
```


#### null与undefined

`null`与`undefined`都表示“没有值(non-value)”的概念，如果严格区分：
- `null`表示空
- `undefined`表示不存在。没有初始化的变量、函数中缺失的参数、函数没有显式return值时都为此值

在其他语言中，一般只用一个null来表示空值，javascript中为什么多了个undefined呢？这是历史原因造成的：
> javascript采用了Java的语法，把类型分为了基本类型与对象类型，Java中用null来表示空对象，javascript想当然的继承了过来；在C语言中，null在转为数字时为0，javascript也采取同样的方式：
```
> Number(null)
0
> 5 + null
5
```
> 在javascript1.0时，还没有异常处理(exception handling)，对于一些异常情况（没有初始化的变量、调用函数时缺失的参数等），需要标明为一种特殊的值，`null`本来是个很好的选择，但是Brendan Eich同时想避免下面两件事：
- 这个特殊值不应该有引用的特性，因为那是对象特有的
- 这个特殊值不应该能转为0，因为这样不容易发现程序中的错误

> 基于这两个原因，Brendan Eich选择了`undefined`，它可以被强转为`NaN`。
```
> Number(undefined)
NaN
> 5 + undefined
NaN
```

两者在于JSON对象打交道时，结果也迥然不同：
```
> JSON.parse(null)
null
> JSON.parse(undefined)
//Firfox SyntaxError: JSON.parse: unexpected character at line 1 column 1 of the JSON data
//Chrome SyntaxError: Unexpected token u

> JSON.stringify(null)
"null"
> JSON.stringify(undefined)
undefined
```

### 对象类型

javascript作为一门[脚本语言](http://en.wikipedia.org/wiki/Scripting_language)，本身功能十分精简，很多功能（文件读写、网络等）都是由宿主环境提供。宿主环境与javascript语言的桥梁是对象，宿主环境通过提供一系列符合javascript语法的对象，提供各种各样的功能。

在[javascript面向对象编程](/blog/2015/02/01/javascript-oop)这篇文章（如果你不知道prototype是什么，强烈建议看看这篇文章）里，我多次强调了`对象在javascript中就是一系列的键值对`，就像Java中的HashMap一样，不过，javascript中对象的属性可以有一些描述符(property descriptor)，这在HashMap中是没有的。

#### 属性描述符

属性描述符分为两类：

- 数据描述符(data descriptor)，包含一系列boolean值，用以说明该属性是否允许修改、删除。
- 访问描述符(accessor descriptor)，包含get与set函数。

这两种描述符都是对象，它们都拥有下面两个boolean属性：

- configurable 用以指定该描述符是否允许修改、删除。默认为false。
- enumerable 用以指定在遍历对象（使用[for...in循环](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...in)或[Object.keys方法](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/keys)）的属性时，是否访问该属性。默认为false。

除了上面这两个共有属性外，数据描述符还有下面两个属性：
- value 用以指定该属性的值，默认为undefined
- writable 用以指定该属性的值是否允许改变该属性的值，默认为false

访问描述符还有下面两个属性：
- get 用以指定访问该属性时的访问器(getter，本质是个函数)，该访问器的返回值为该属性的值。默认为undefined
- set 用以指定访问该属性时的赋值器(setter，本质是个函数)，该赋值器的接受一个参数。默认为undefined

我们可以使用[Object.defineProperty](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty)来设置对象的属性描述符。例如：
```
// using __proto__
Object.defineProperty(obj, 'key', {
  __proto__: null, // no inherited properties
  value: 'static'  // not enumerable
                   // not configurable
                   // not writable
                   // as defaults
});
```
通过上面这个例子可以看出，描述符具有继承的特点，我们这里显式的把描述符对象的`__proto__`设为`null`，就避免了从`Object.prototype`中继承相应属性。当然我们也可以显式地设置描述符的所有属性：
```
// being explicit
Object.defineProperty(obj, 'key', {
  enumerable: false,
  configurable: false,
  writable: false,
  value: 'static'
});
```
这样的效果和第一段代码的效果是一样的。

下面再举一个访问描述符的例子：
```
// Example of an object property added with defineProperty with an accessor property descriptor
var bValue = 38;
Object.defineProperty(obj, 'key', {
  get: function() { return bValue; },
  set: function(newValue) { bValue = newValue; },
  enumerable: true,
  configurable: true
});
```
需要注意的是，不能混淆了访问描述器与数据描述器。下面这样写是错误的：
```
// You cannot try to mix both:
Object.defineProperty(obj, 'conflict', {
  value: 0x9f91102,
  get: function() { return 0xdeadbeef; }
});
// throws a TypeError: property descriptors must not specify a value
// or be writable when a getter or setter has been specified

```

##typeof

如果想在运行时获知某变量的类型，可以使用typeof操作符。typeof的返回值如下表：
<center>
<img src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB2WufjbVXXXXX1XpXXXXXXXXXX_!!581166664.png" alt="typeof-values"/>
</center>

其中有一处需要注意，那就是`typeof null == "object"`，按照[ECMAScript 5.1](http://www.ecma-international.org/ecma-262/5.1/#sec-4.3.2)标准，`Null`类型应该是个基本类型，为什么这里返回`object`呢？原因是这样的：
> 在javascript 1.0中，javascript中的值是用一个类型标志（type tag）和一个实际值这样的结构表示的，对象的类型标志为0，null在C语言中表示NULL指针（0x00），所以null的类型标志就为0了。

##参考

- [《Speaking JavaScript》 Chapter 8. Values](http://speakingjs.com/es5/ch08.html#undefined_null)
- [A Survey of the JavaScript Programming Language](http://javascript.crockford.com/survey.html)
- [Object.defineProperty](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty)
- [Standard built-in objects String](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)
- [typeof](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/typeof)
- [The history of “typeof null”](http://www.2ality.com/2013/10/typeof-null.html) （需翻墙）
