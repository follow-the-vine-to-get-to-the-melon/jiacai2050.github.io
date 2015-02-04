title: javascript中的面向对象(object-oriented)编程
date: 2015-02-01 12:53:18
categories: 编程语言
tags: [javascript, mozilla]
---

最近工作一直在用nodejs做开发，有了nodejs，前端、后端、脚本全都可以用javascript搞定，很是方便。但是javascript的很多语法，比如对象，就和我们常用的面向对象的编程语言Java不同，看某个javascript开源项目，也经常会看到使用this关键字，而这个this关键字在javascript中因上下文不同而意义不同，这些零零碎碎的东西加起来就很容易让人不知所措，所以，有必要对javascript这门语言进行一下深入了解。

我这篇文章主要想说说如何在javascript中进行面向对象的编程，同时会讲一些javascript这门语言在设计之初的理念。下面让我们开始吧。

## javascript设计理念

javascript1.0 最初是由网景公司的[Brendan Eich](http://en.wikipedia.org/wiki/Brendan_Eich)在1995年5月花了[十天搞出来的](http://www.computer.org/csdl/mags/co/2012/02/mco2012020007.pdf)，Eich的目标是设计出一种即轻量又强大的语言，所以Eich充分借鉴了其他编程语言的特性，比如Java的语法(syntax)、Scheme的函数(function)、Self的原型继承(prototypal inheritance)、Perl的正则表达式等。
其中值得一提的是，为什么继承借鉴了Self语言的原型机制而不是Java的类机制？首先我们要知道：
- Self的原型机制是靠运行时的语义
- Java的类机制是靠编译时的类语法

Javascript1.0的功能相对简单，为了在今后不断丰富javascript本身功能的同时保持旧代码的兼容性，javascript通过改变运行时的支持来增加新功能，而不是通过修改javascript的语法，这就保证了旧代码的兼容性。这也就是javascript选择基于运行时的原型机制的原因。
wikipedia这样描述到：JavaScript is classified as a [prototype-based](http://en.wikipedia.org/wiki/Prototype-based_programming) scripting language with [dynamic typing](http://en.wikipedia.org/wiki/Dynamic_language) and [first-class functions](http://en.wikipedia.org/wiki/First-class_functions)。这些特性使得javascript是一种[多范式](http://en.wikipedia.org/wiki/Multi-paradigm)的[解释性](http://en.wikipedia.org/wiki/Interpreter_%28computing%29)编程语言，支持[面向对象](http://en.wikipedia.org/wiki/Object-oriented_programming),[命令式(imperative)](http://en.wikipedia.org/wiki/Imperative_programming), [函数式(functional)](http://en.wikipedia.org/wiki/Functional_programming)编程风格。

##Object对象
在javascript中，除了数字、字符串、布尔值（true/false）、undefined这几个简单类型外，其他的都是对象。
数字、字符串、布尔值这些都是不可变量，是可变的键值对的集合(mutable keyed conllections)，数组`Array`、正则表达式`Regexp`、函数`Function`都是对象，当然`Object`也是对象。
对象在javascript中说白了就是一系列的键值对。键可以是任何字符串，包括空串；值可以是除了undefined以外的任何值。在javascript中是没有类的概念(class-free)的，但是它有一个原型链(prototype linkage)。javascript对象通过这个链来实现继承关系。在语法表现上就是每个对象都有一个prototype属性。
javascript中提供了一种简单的方法用来创建对象：`对象字面量(object literal)`。类似于下面的方式：
```
var empty_object = {};//创建了一个空对象
//创建了一个有两个属性的对象
var stooge = {
    "first-name": "Jerome",
    "last-name": "Howard"
};
```
当然，javascript中也有一些[预定义对象](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects)，像是`Function`、`Date`、`Number`、`String`、`Array`等。其中比较重要的是`Function`与`Array`，下面讲一下这两个非常有用的对象。
###函数对象Function
函数是javascript中的精髓。对函数的理解程度决定了对javascript的理解程度。

首先，函数在javascript中无非也是个对象，可以作为value赋值给某个变量，唯一不同的是函数能够被执行。使用对象字面量方式创建的对象prototype指向`Object.prototype`(Object.prototype的prototype指向null)，函数对象的prototype指向`Function.prototype`(Function.prototype这个 对象的prototype属性指向Object.prototype)。每个函数对象还有两个隐藏的属性：
1. 函数的上下文(function’s context)
2. 实现函数的代码(the code that implements the function’s behavior)

和对象字面量一样，我们可以使用`函数字面量(function literal)`来创建函数。类似于下面的方式：
```
//创建一个函数，并赋值给add变量
var add = function (a, b) { 
    return a + b;
};
```
一个函数字面量有四个部分：
1. function关键字，必选项。
2. 函数名，可选项。上面的示例中就省略了函数名
3. 由圆括号括起来的一系列参数，必选项。
4. 由花括号括起来的一系列语句，必选项。该函数执行时将会执行这些语句。

####函数调用与this
一个函数在被调用时，除了声明的参数外，还会隐式传递两个额外的参数：`this`与`arguments`。
this在OOP中很重要，this的值随着调用方式的不同而不同。javascript中共有四种调用方式：
1. method invocation pattern。当函数作为某对象一个属性调用时，this指向这个对象。this赋值过程发生在函数调用时（也就是运行时），这叫做late binding
2. function invocation pattern。当函数不作为属性调用时，this指向全局对象，这是个设计上的错误，正确的话，内部函数的this应该指向外部函数。可以通过在函数中定义一个变量来解决这个问题。
    
        var add = function(a, b) {return a+b;}
        var obj = {
            value: 3,
            double: function() {
                var self = this;//把this赋值给了self
                this.value = add(self.value, self.value);
            }
        }
        obj.double(); //obj.value现在为6

3. construct invocation pattern。javascript是一门原型继承语言，这也就意味着对象可以直接从其他对象中继承属性，没有类的概念。这和java中的继承不一样。但是javascript提供了一种类似与java创建对象的语法。当一个函数用new来调用时，this指向新创建的对象。这时的函数通常称为构造函数。
4. apply invocation pattern。使用函数对象的[apply方法](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/apply)来执行时，this指向apply的第一个参数。

除了this外，函数在调用是额外传入的另一个参数是`arguments`。它包含函数调用处的所有参数，甚至包含函数定义时没有的参数。
```
var sum = function () { 
    var i, sum = 0;
    for (i = 0; i < arguments.length; i += 1) {
        sum += arguments[i];
    }
    return sum;
};
sum(4, 8, 15, 16, 23, 42); // 108
```
需要注意的是，这里的arguments不是一个数组，它只是一个有length属性的类数组对象(Array-like)，它并不拥有数组的其他方法。

###数组对象Array
数组是一种在内存中线性分配的数据结构，通过下标计算出元素偏移量，从而取出元素。数组应该是一个快速存取的数据结构，但是在javascript中，数组不具备这种特性。
数组在javascript中一个具有传统数组特性的对象，这种对象能够把数组下标转为字符串，然后把这个字符串作为对象的key，最后对取出对应该key的value（这又一次说明了对象在javascript中就是一系列键值对）。

虽然javascript中的数组没有传统语言中的数组那么快，但是由于javascript是弱类型的语言，所以javascript中的数组可以存放任何值；关于Array更多的知识点，大家可以去[MDN Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)查看。
javascript也为数组提供了很方便的`字面量(Array Literal)`定义方式：
```
var arr = [1,2,3]
```
通过数组字面量创建的数组对象的prototype指向Array.prototype。

##继承Inheritance

在Java中，对象是某个类的实例，一个类可以从另一个类中继承。但是在基于原型链的javascript中，对象可以直接从另一个对象创建。

在上面讲解javascript内置对象时，我们知道了在创建一个对象时，该对象会自动赋予一个prototype属性，使用各种类型的`字面量(Literal)`时，javascript解释器自动为prototype进行了赋值。当我们在javascript执行使用new操作符创建对象时，javascript解释器在构造函数时，同时会执行类似于下面的语句
```
     this.prototype = {constructor: this};
```
新创建的对象都会有一个protoytpe属性，这个属性有一个constructor属性，并且这个属性指向这个新对象。
如果new不是一个操作符，而是一个函数的话，它的实现类似于下面的代码：
```
Function.prototype.new =  function () {
    // Create a new object that inherits from the constructor's prototype.
    var that = Object.create(this.prototype);
    // Invoke the constructor, binding –this- to the new object.
    var other = this.apply(that, arguments);
    // If its return value isn't an object, substitute the new object.
    return (typeof other === 'object' && other) || that;
};
```

之前也说了，基于原型的继承机制是根据运行时的语义决定的，这就给我们提供了很大的便利。比如，我们想为所有的Array添加一个map函数，那么我们可以这么做：
```
Array.prototype.map = function(f) {
    var newArr = [];
    for(i=0; i<this.length; i++) {
        newArr.push(f(this[i]));
    }
    return newArr;
}
```
因为所有的数组对象的prototype都指向Array.prototype对象，所谓我们为这个对象增加方法，那么所有的数组对象就都拥有了这个方法。
javascript解释器会顺着原型链查看某个方法或属性。如果想查看某对象的是否有某个属性，可以使用`Object.prototype.hasOwnProperty`方法。

##总结

通过上面多次强调，希望大家对`对象在javascript中就是一系列的键值对`这个概念有个深刻的认识。
其次我想说一下，我们现在广泛使用的javascript都是遵循了[ECMAScript 5.1](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Language_Resources)标准的，最新的6.0版本正在制定中，这个版本变化很大，增加了很多新的语法与函数，大家可以去[Mozilla Developer Network](https://developer.mozilla.org/en-US/docs/Web/JavaScript)上查看。

这篇文章大部分内部参考自[《Javascript: The Good Parts》](http://book.douban.com/subject/2994925/)，加上我自己的理解，强烈建议大家去看这个书。
<center>
![Javascript: The Good Parts](http://img3.douban.com/lpic/s2931482.jpg)
</center>

