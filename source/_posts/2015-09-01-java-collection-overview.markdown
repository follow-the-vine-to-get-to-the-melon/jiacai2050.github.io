title: Java集合框架综述
date: 2015-09-01 21:18:05
categories: 编程语言
tags: java
---

最近被陆陆续续问了几遍HashMap的实现，回答的不好，打算复习复习JDK中的[集合框架](https://docs.oracle.com/javase/8/docs/technotes/guides/collections/overview.html)，并尝试分析其源码，这么做一方面是这些类非常实用，掌握其实现能更好的优化我们的程序；另一方面是学习借鉴JDK是如何实现了这么一套优雅高效的类库，提升编程能力。

在介绍具体适合类之前，本篇文章对Java中的集合框架做一个大致描述，从一个高的角度俯视这个框架，了解了这个框架的一些理念与约定，会大大帮助后面分析某个具体类，让我们开始吧。

## 集合框架（collections framework）

首先要明确，集合代表了一组对象（和数组一样，但数组长度不能变，而集合能）。Java中的集合框架定义了一套规范，用来表示、操作集合，使具体操作与实现细节解耦。

其实说白了，可以把一个集合看成一个微型数据库，操作不外乎“增删改查”四种操作，我们在学习使用一个具体的集合类时，需要把这四个操作的`时空复杂度`弄清楚了，基本上就可以说掌握这个类了。

## 设计理念

主要理念用一句话概括就是：提供一套“小而美”的API。API需要对程序员友好，增加新功能时能让程序员们快速上手。
为了保证核心接口足够小，最顶层的接口（也就是Collection与Map接口）并不会区分该集合是否可变（mutability）,是否可更改（modifiability）,是否可改变大小（resizability）这些细微的差别。相反，一些操作是可选的，在实现时抛出`UnsupportedOperationException`即可表示集合不支持该操作。集合的实现者必须在文档中声明那些操作是不支持的。

为了保证最顶层的核心接口足够小，它们只能包含下面情况下的方法：

1. 基本操作，像之前说的“增删改查”
2. There is a compelling performance reason why an important implementation would want to override it.

此外，所有的集合类都必须能提供友好的交互操作，这包括没有继承`Collection`类的数组对象。因此，框架提供一套方法，让集合类与数组可以相互转化，并且可以把`Map`看作成集合。

## 两大基类Collection与Map

在集合框架的类继承体系中，最顶层有两个接口：
- `Collection`表示一组纯数据
- `Map`表示一组key-value对

一般继承自`Collection`或`Map`的集合类，会提供两个“标准”的构造函数：
- 没有参数的构造函数，创建一个空的集合类
- 有一个类型与基类（`Collection`或`Map`）相同的构造函数，创建一个与给定参数具有相同元素的新集合类

因为接口中不能包含构造函数，所以上面这两个构造函数的约定并不是强制性的，但是在目前的集合框架中，所有继承自`Collection`或`Map`的子类都遵循这一约定。


### Collection

![java-collection-hierarchy](https://img.alicdn.com/imgextra/i4/581166664/TB21HYoeVXXXXaLXXXXXXXXXXXX_!!581166664.jpeg)

如上图所示，[Collection](http://docs.oracle.com/javase/7/docs/api/java/util/Collection.html)类主要有三个接口：
- `Set`表示不允许有重复元素的集合（A collection that contains no duplicate elements）
- `List`表示允许有重复元素的集合（An ordered collection (also known as a sequence)）
- `Queue` JDK1.5新增，与上面两个集合类主要是的区分在于`Queue`主要用于存储数据，而不是处理数据。（A collection designed for holding elements prior to processing.）

### Map

![MapClassHierarchy](https://img.alicdn.com/imgextra/i4/581166664/TB2JzW7eVXXXXbRXpXXXXXXXXXX_!!581166664.jpg)

[Map](http://docs.oracle.com/javase/7/docs/api/java/util/Map.html)并不是一个真正意义上的集合（are not true collections），但是这个接口提供了三种“集合视角”（collection views ），使得可以像操作集合一样操作它们，具体如下：
- 把map的内容看作key的集合（map's contents to be viewed as a set of keys）
- 把map的内容看作value的集合（map's contents to be viewed as a collection of values）
- 把map的内容看作key-value映射的集合（map's contents to be viewed as a set of key-value mappings）

## 总结

今天先开个头，后面会陆陆续续来一系列干货，Stay Tuned。

需要说明一点，今后所有源码分析都将基于[Oracle JDK 1.7.0_71](http://www.oracle.com/technetwork/java/javase/7u71-relnotes-2296187.html)，请知悉。

    $ java -version
    java version "1.7.0_71"
    Java(TM) SE Runtime Environment (build 1.7.0_71-b14)
    Java HotSpot(TM) 64-Bit Server VM (build 24.71-b01, mixed mode)


## 参考

- http://docs.oracle.com/javase/7/docs/technotes/guides/collections/overview.html
- https://en.wikipedia.org/wiki/Java_collections_framework 