title: 我的第一个玩具语言 JCScheme 问世了
date: 2015-10-03 17:13:49
categories: 没事找事
tags: sicp
---

记得在上大学那会，就想着能够实现个自己的编程语言。由于之前技能不足，一直没敢去尝试。现赶上国庆七天假期，SICP 看的也正起劲，终于鼓起勇气，把这个坑给填上了。甚是开心。
实现 JCScheme 这个语言前后大概用了一天时间，功能虽然简单，但是“麻雀虽小，五脏俱全”，编程语言中最基本的类型、作用域、函数都涵盖了，以后在扩展时也很方便。
如果你和之前的我一样，想实现一门语言但又苦于无从下手，那么你应该花半个小时看看本文，相信你肯定会有所收获。
本文没有复杂难懂的编译原理知识，没有学过编译原理的人不要害怕。
JCScheme 完整代码托管到[Github](https://github.com/jiacai2050/JCScheme)，并且以后会持续更新，感兴趣的可以去 star。


## 预备知识

### 前缀表达式
由于 JCScheme 极其简单，所以你不需要什么背景知识即可看懂本文，不过你最好了解点 Scheme 语言，如果不了解也没关系，你只需要知道 JCScheme 中的语句使用[前缀表达式（也称为波兰表示法）](https://zh.wikipedia.org/zh/%E6%B3%A2%E5%85%B0%E8%A1%A8%E7%A4%BA%E6%B3%95)，如果你之前没了解过，需要适应下。
```
# 这是我们常用的中缀表达式
(5 − 6) * 7
# 这就是前缀表达式
* (− 5 6) 7
```
前缀表达式最明显的一个好处是其操作符的参数可以有不定个，像`(+ 1 2 3 4)`。

### 编程语言分类
现在编程语言大致可以分为两种：
1. 编译型，该类型语言源代码经由编译器（compiler）转化为机器语言，再由机器运行机器码。像C/C++ 即属于这个范畴。更详细的可以参考[深入理解计算机之hello world背后的故事](http://segmentfault.com/a/1190000003814221)
2. 解释型，该类型语言不转化为最终的机器语言，而是由解释器（interpreter）逐行解释执行，像 Python、JavaScript 属于这个范畴， JCScheme 也是这种类型。

由于我这里采用 Java 来实现 JCScheme 的解释器，所以 JCScheme 源代码的执行逻辑是这样的：
<center>
    <img src="https://img.alicdn.com/imgextra/i2/581166664/TB2548UfVXXXXXiXXXXXXXXXXXX_!!581166664.png" alt="JCScheme 源程序执行逻辑"/>
</center>

可以看到，JCScheme 解释器的主要工作就是将按照自定义语法规则书写的源程序，转化为 Java 代码，之后的事情就由 JVM 来处理了。

所以我们实现自己的语言要做的就是两件事：
1. 制定语法
2. 编写解释器，解析自定义的语法

## JCScheme 语法
```
rlwrap java -jar target/JCScheme-*.jar
>> (* 2 3 4 5)
120
>> (def a 4)
null
>> (def b 5)
null
>> (if (> a b) a b)
5
>> (def max (lambda (a b) (if (> a b) a b)))
null
>> (def c (max a b))
null
>> c
5
```

从上面可以看出，JCScheme 有以下基本特性：
1. 支持整数（Java int实现）与布尔（Java bool实现）、函数三种类型
2. 提供`def`进行变量定义、`if`进行逻辑判断、`lambda`进行函数声明
3. 支持整数的`+`、`-`、`*`、`/`四种基本算术操作，`>`、`<`、`=`三种比较操作。参数可以为多个
4. 更多的特性可以参考[ChangeLog](https://github.com/jiacai2050/JCScheme#ChangeLog)

现在 JCScheme 中只有一个全局环境（Java Map实现），后面定义的同名变量会覆盖之前的。

## 基本概念与实现
实现一个解释器时，一般步骤如下：
> 词法分析 --> 语法分析 ---> 语义分析 ---> 求值

### 词法分析

词法分析（lexical analysis）就是将源程序中的字符分割为一个个单词（token，构成源代码最小的单位）。
由于 JCScheme 中使用前缀表示，所以词法解析很简单，两行代码：
```
src = src.replaceAll("\\(", "( ").replaceAll("\\)", " )");
String[] tokens = src.split("\\s+");
```

### 语法分析

语法分析（Syntactic analysis，也叫Parsing）也就是把词法分析得到的token序列转化为[语法树（AST）](https://en.wikipedia.org/wiki/Abstract_syntax_tree)，语法树是程序的中间表示形式，与具体语言无关。JCScheme 采用 Lisp 中经典的[S表达式（S-expression）](https://en.wikipedia.org/wiki/S-expression)来表示语法树。

<center>
<img src="https://img.alicdn.com/imgextra/i1/581166664/TB2MKQ2fFXXXXX1XpXXXXXXXXXX_!!581166664.png" alt="(* 2 (+ 3 4)) 的语法树"/>
</center>

AST 本质是一种树，大家可以先想想数据结构中一般都是怎么设计树的存储结构。（其实只要设计的数据结构能够保证获取到当前节点的父节点与子节点就可以了）。下面看看我的实现：
```
public class SExpression {
    private String value;
    private SExpression parent;
    private List<SExpression> children;

    public SExpression(String value, SExpression parent) {
        this.value = value;
        this.parent = parent;
        this.children = new ArrayList<>();
    }

    public boolean addChild(SExpression child) {
        return this.children.add(child);
    }
    // 3个 getter 函数省略
    // 进行求值的 eval 函数省略，这是重点，后面会单独介绍
    @Override
    public String toString() {
        if (0 == children.size()) {
            return value;
        } else {
            StringBuffer displayBuffer = new StringBuffer(value + " ");
            for (SExpression child : children) {
                displayBuffer.append(child.toString() + " ");
            }
            return displayBuffer.toString();
        }
    }
}
```
解析token序列生产AST的函数是
```
    public static final String START_TOKEN = "(";
    public static final String END_TOKEN = ")";

    public static SExpression parse(String[] tokens) {
        SExpression root = new SExpression("", null);
        SExpression parent = root;
        for (String token : tokens) {
            SExpression newNode = new SExpression(token, parent);
            parent.addChild(newNode);
            switch (token) {
            case Constants.START_TOKEN:
                parent = newNode;
                break;
            case Constants.END_TOKEN:
                parent = parent.getParent();
                break;
            }
        }
        return root;
    }
```
可以看到，每个 AST 根节点是token为空，父节点为 null 的一节点。
这里解析的方法是：
1. 每一个token为AST上的一节点，父节点为 parent（初始为root）
2. 遇到`(` token时，开始创建该节点的子树（通过让这个节点成为 parent 实现）
3. 遇到`)` token时，进行回溯（通过把 parent 赋值为 parent.getParent() 实现）

下面看下`(+ 1 2 (* 3 4))`生成怎样的 `SExpression`：
<center>
    <img src="https://img.alicdn.com/imgextra/i4/581166664/TB2l9NefVXXXXbeXXXXXXXXXXXX_!!581166664.png" alt="(+ 1 2 (* 3 4)) AST 示意图"/>
</center>
上图最主要的一点就是
> 与左括号相匹配的右括号位于左括号的最后一个孩子节点上（从左到右）。

### 语义分析

语义分析（Semantic analysis，也叫context sensitive analysis）根据上一步生成的AST，收集源代码的信息，这包括类型校验、变量在使用前是否声明等一系列操作。

因为 JCScheme 中类型比较简单，而且去做语义分析，需要做很多异常处理，有些繁琐，我这里为了简单都忽略了。所以如果你输入的语法有误（比如括号不匹配），那么解释器就会报错，在后面的迭代中会逐步改善这块。

## 求值（eval与apply）

做完了词法分析、语法分析，我们已经得到了与具体语言无关的 AST，那么如果求值呢，SICP 书中给出了`eval-apply cycle`，如下图
<center>
    <img src="https://img.alicdn.com/imgextra/i2/581166664/TB2KjMVfFXXXXbOXpXXXXXXXXXX_!!581166664.png" alt="ICP-eval-apply"/>
</center>
在[StackOverflow](http://stackoverflow.com/a/6269132/2163429)上找到一比较好理解的解释：
-  the one that eval is doing, is dealing with the syntactic translation of code to its meaning -- but it's doing almost nothing except dispatching over the expression type
-  apply is to call function with values.
- A major enlightenment moment here is to realize that there is a major difference between this eval and apply -- the former inherently deals with syntax, but the latter deals with values.

如果你也在读 SICP，可以参考下面的`eval`、与`apply`的具体实现，对 Scheme 不了解的可以直接略过。
```
(define (eval exp env)
  (cond ((self-evaluating? exp) exp)
        ((variable? exp) (lookup-variable-value exp env))
        ((quoted? exp) (text-of-quotation exp))
        ((assignment? exp) (eval-assignment exp env))
        ((definition? exp) (eval-definition exp env))
        ((if? exp) (eval-if exp env))
        ((lambda? exp)
         (make-procedure (lambda-parameters exp)
                         (lambda-body exp)
                         env))
        ((begin? exp) 
         (eval-sequence (begin-actions exp) env))
        ((cond? exp) (eval (cond->if exp) env))
        ((application? exp)
         (apply (eval (operator exp) env)
                (list-of-values (operands exp) env)))
        (else
         (error "Unknown expression type -- EVAL" exp))))

(define (apply procedure arguments)
  (cond ((primitive-procedure? procedure)
         (apply-primitive-procedure procedure arguments))
        ((compound-procedure? procedure)
         (eval-sequence
           (procedure-body procedure)
           (extend-environment
             (procedure-parameters procedure)
             arguments
             (procedure-environment procedure))))
        (else
         (error
          "Unknown procedure type -- APPLY" procedure))))

```
简单来说，`eval`的主要作用就是理解 AST 的含义，根据其含义进行相应处理，比如赋值语句有其独特的处理方式，if 语句有其独特的处理方式等等。
为了能够让`apply`进行函数调用求值，需要把 AST 解释为 JCScheme 中内置的类型，而这就是 JCScheme 中`eval`的主要作用。

### 类型定义

定义一个基类
```
public abstract class SObject {

}
```
然后是整数类型与布尔类型
```
public class SNumber extends SObject{

    private int value;

    public int getValue() {
        return value;
    }
    public SNumber(int value) {
        this.value = value;
    }
    @Override
    public String toString() {
        return String.valueOf(value);
    }
    
}
public class SBool extends SObject{
    private boolean value;

    public boolean getValue() {
        return value;
    }

    public SBool(boolean value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}
```
这两个类比较简单，并且注意到没有为其成员变量提供`setter`函数，这说明这些类型是不可变的。
最后一个比较重要的是函数类型
```
public class SFunction extends SObject{

    List<String> param;
    SExpression body;

    public SFunction(List<String> param, SExpression body) {
        this.param = param;
        this.body = body;
    }

    public SObject apply(SObject... args) {
        for(int i = 0; i< args.length; i ++) {
            SScope.env.put(param.get(i), args[i]);
        }
        SObject ret = body.eval();
        for(int i = 0; i< args.length; i ++) {
            SScope.env.remove(param.get(i));
        }
        return ret;
    }
    @Override
    public String toString() {
        StringBuffer buffer = new StringBuffer("Function : args [");
        for(String p : param) {
            buffer.append(p + ", ");
        }
        buffer.append("]\n");
        buffer.append("Body :\n");
        buffer.append(body.toString());
        return buffer.toString();
    }
    
}
```
可以看到，`SFunction`内部有两个成员变量，用来表示其`参数列表`与`函数体`。其中的`apply`表示函数调用，可以看到无非就是把形式参数与实际参数进行捆绑（现在放到全局环境中，按理说这时应该生成一新环境，后面再改进），之后调用`SExpression`的`eval`方法，得到用内置类型表示的结果。

可以看到，这里的重点又回到`eval`方法上去了。 JCScheme 的主要复杂点也就算在`SExpression`的`eval`方法上，因为它涉及到把`SExpression`转为内置类型，所以按理说也应该是复杂的。

`eval`的工作原理最直接的方式就是看源码[JCScheme/SExpression.java](https://github.com/jiacai2050/JCScheme/blob/master/src/main/java/net/liujiacai/jcscheme/SExpression.java)，这个方法后面会不断完善。


## 不足

经过上面这些工作，运行是没问题了（希望没有bug😊），函数定义也有了。但是下面这些点都没有涉及
1. 函数的递归调用
2.  <del>匿名函数的直接调用，如`((lambda (a b) (+ a b)) 1 2)`，现在这样的方式是不支持的， 需要先定义个变量，然后在调用</del>，已经支持。
3. 函数的部分调用，也就是`currying`
......

后面会逐步添坑，大家可以查看 JCScheme 的 [ChangeLog](https://github.com/jiacai2050/JCScheme#ChangeLog) 获取最新进展。

## 总结

“纸上得来终觉浅，绝知此事要躬行”，最开始时，觉得像 Scheme 语法这么简单的语言实现起来应该不难，做了后才发现眼高手低。比如，我第一次设计`SExpression`时没有`parent`这个属性导致了无法正确实现`parse`函数。
不过感触最深应该是这点：动手。在之前学习编程语言，被各种语法类库虐的死去活来，虽然想尝试去实现个自己的语言，但是一直觉得自己能力不够，没敢去尝试，经过这次 JCScheme 的开发，真是有种“不入虎穴,焉得虎子”的感觉。

当然，JCScheme 语言只是刚开始，还比较简陋，高手请不要见笑，后面随着学习的深入我会逐步完善。

##  参考

- 王垠的[谈谈Parser](http://www.yinwang.org/blog-cn/2015/09/19/parser/)
- [90分钟实现一门编程语言——极简解释器教程](http://zh.lucida.me/blog/how-to-implement-an-interpreter-in-csharp/)