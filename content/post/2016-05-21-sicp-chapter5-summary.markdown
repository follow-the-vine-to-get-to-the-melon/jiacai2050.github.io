title: SICP 第五章总结
date: 2016-05-21 16:04:15
categories: [研习经典]
tags: [sicp]
---

经过第四章元语言抽象的洗礼，我们已经能够深谙编译器内部的原理，核心就是`eval-apply`循环，只是说基于这个核心可以有各种延伸，像延迟求值、amb 不定选择求值、逻辑求值等等，有了这层的理解，我们应该能够透过各种花哨的[语法糖](https://en.wikipedia.org/wiki/Syntactic_sugar)，看出其本质来，像 Node.js 中的 Promise、 Python 中的 coroutine，都是 [continuation](https://en.wikipedia.org/wiki/Continuation) 的一种应用而已。

但是，我们还无法解释子表达式的求值怎样返回一个值，以便送给使用这个值的表达式，也无法解释为什么有些递归过程能产生迭代型的计算过程，而另一些递归过程却生产递归型的计算。就其原因，是因为我们所实现的求值器是 Scheme 程序，它继承并利用了基础系统的控制结构。要想进一步理解 Scheme 的控制结构，必须转到更低的层面，研究更多细节，而这些，就是第五章的主要内容。

## 寄存器机器的设计

为了探讨底层的控制结构，本章基于传统计算机的一步一步操作，描述一些计算过程，这类计算机称为寄存器机器，它的主要功能就是`顺序的`执行一条条指令，操作一组存储单元。本章不涉及具体机器，还是研究一些 Scheme 过程，并考虑为每个过程设计一个特殊的寄存器机器。

第一步工作像是设计一种硬件体系结构，其中将：

1. 开发一些机制支持重要程序结构，如递归，过程调用等
2. 设计一种描述寄存器机器的语言
3. 做一个 Scheme 程序来解释用这种语言描述的机器

寄存器机器包含`数据通路(寄存器和操作)`和确定操作顺序的`控制器`。书中以 gcd 算法为例介绍：

```
(define (gcd a b)
  (if (= b 0)
    a
    (gcd b (remainer a b))))
```
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB280XDppXXXXXWXXXXXXXXXXXX_!!581166664.png"  alt="GCD 数据通路"/>
<img src="https://img.alicdn.com/imgextra/i3/581166664/TB2S63.pXXXXXXXXpXXXXXXXXXX_!!581166664.png" alt=" GCD 控制器"/>
</center>

为了描述复杂的过程，书中采用如下的语言来描述寄存器机器：
```
(controller
  test-b
    (test (op =) (reg a) (const 0))
    (branch (label gcd-done))
    (assign t (op rem) (reg a) (reg b))
    (assign a (reg b))
    (assign b (reg t))
    (goto (label test-b))
  gcd-done)
```
### 子程序

直接带入更基本操作的结构，可能使控制器变得非常复杂，希望能够作出某种安排，维持机器的简单性，而且避免重复的结构，比如如果机器两次用GCD，最好公用一个 GCD 部件，这是可行的，因为任一时刻，只能进行一个 GCD 操作，只是输入输出的寄存器不一样而已。思路：

> 调用 GCD 代码前把一个寄存器(如 continue)设置为不同的值,在 GCD 代码的出口根据该寄存器跳到正确位置

具体代码与图示可参考：[2015-05-12_subroutes.md](https://github.com/jiacai2050/sicp/blob/master/2016-05/2015-05-12_subroutes.md)

### 采用堆栈实现递归

```
(define (factorial n)
  (if (= n 1)
    1
    (* n (factorial (- n 1)))))
```    
表面看计算阶乘需要嵌套的无穷多部机器,但任何时刻只用一部。要想 用同一机器完成所有计算,需要做好安排,在遇到子问题时中断当前计算,解决子问题后回到中断的原计算。注意:

- 进入子问题时的状态与处理原问题时不同(如 n 变成 n-1)
- 为了将来能继续中断的计算,必须保存当时状态(当时 n 的值)

控制问题:子程序结束后应该返回哪里？

- continue 里保存返回位置,递归使用同一机器时也要用这个寄存 器,给它赋了新值就会丢掉当时保存其中准备返回的位置
- 为了能正确返回,调用前也需要把 continue 的值入栈

阶乘算法的具体解释与图示可参考：[2016-05-16_recursion_stack.md](https://github.com/jiacai2050/sicp/blob/master/2016-05/2016-05-16_recursion_stack.md)

这里比较难理解的是 fib 算法，因为这里涉及到两次递归调用：
```
(define (fib n)
  (if (< n 2)
    n
    (+ (fib (- n 1))
       (fib (- n 2)))))

(controller
  (assign continue (label fib-done))
fib-loop
  (test (op <) (reg n) (const 2))
  (branch (label immediate-answer))
  ;; set up to compute Fib(n-1)
  (save continue)
  (assign (continue (label afterfib-n-1))
  (save n)                                ; save old value of n
  (assign n (op -) (reg n) (const 1)))    ; clobber n to n-1
  (goto (label fib-loop))                 ; perform recursive call
afterfib-n-1                              ; upon return, val contains Fib(n-1)
  (restore n)
  (restore continue)
  ;; set up to compute Fib(n-2)
  (assign n (op -) (reg n) (const 2))
  (save continue)
  (assign continue (label afterfib-n-2))
  (save val)                               ; save Fib(n-1)
  (goto (label fib-loop))
afterfib-n-2                               ; upon return, val contains Fib(n-2)
  (assign n (reg val))                     ; n now contains Fib(n-2)
  (restore val)                            ; val now contains Fib(n-1)
  (restore continue)
  (assign val (op +) (reg val) (reg n))    ; return to caller, answer is in val
  (goto (reg continue))
immediate-answer
  (assign val (reg n))                     ; base case: Fib(n) = n
  (goto (reg continue))
fib-done)

;; afterfib-n-1 中先把 continue 释放，然后又保存起来，中间什么操作也没有
```

[习题5.6](https://github.com/jiacai2050/sicp/blob/master/exercises/05/5.6.scm)、[习题5.11](https://github.com/jiacai2050/sicp/blob/master/exercises/05/5.11.md) 对这一算法进行了分析与修改，建议大家看看。


## 一个寄存器机器模拟器

这是5.2小节的内容，主要是用一种寄存器机器语言（即上面描述 gcd、fib 的语言）描述的机器构造一个模拟器。这一模拟器是一个 Scheme 程序，采用第三章介绍的消息传递的编程风格，将模拟器封装为一个对象，通过给它发送消息来模拟运行。

这一模拟器的代码主要可以分为两部分：[assemble.scm](https://github.com/jiacai2050/sicp/blob/master/exercises/05/lib/assemble.scm)、[machine.scm](https://github.com/jiacai2050/sicp/blob/master/exercises/05/lib/machine.scm)，有需要的可以结合书中解释看看。

这里让我为之惊叹的一点是，本书作者采用之前一贯的风格，用 Scheme 实现了一台寄存器机器，和第四章中各种解释器一样，通过层层数据抽象，让你觉得计算机也没那么深不可测，也是可以通过基本过程构造出来的。

## 其他内容

为了实现 Scheme 解释器,还需要考虑表结构的表示和处理（5.3节内容）：

- 需要实现基本的表操作
- 实现作为运行基础的巧妙的存储管理机制 后面讨论有关的基础技术(可能简单介绍)

有了基本语言和存储管理机制之后,就可以做出一部机器（5.4节内容）,它能

- 实现第四章介绍的元循环解释器
- 而且为解释器的细节提供了清晰的模型

这一章的最后（5.5节内容）讨论和实现了一个编译器
- 把 Scheme 语言程序翻译到这里的寄存器机器语言
- 还支持解释代码和编译代码之间的连接,支持动态编译等

这里由于时间与精力的缘故，最后三小节没有进行细致的阅读，在将来需要时再回来阅读。

## 总结

终于到了这一天，历时一年多，终于还是把这本书看完了，算是了了一个心结，大概在大三的时候就知道了这本书，算算到现在完整的看完，有四年时间了。在最近这一年中，这本书带给我了无数的灵感与启发，这种感觉真的无法描述，只有你亲自体会。

此时此刻印象最深的有两点：

- 对现实世界中时间与空间的模拟，没有最优解，不管是延时求值的流还是封装属性的对象，都有其局限性。也可能是我们人类对世界的认识还不够。摘抄书中P219一段话：

> 从本质上看，在并发控制中，任何时间概念都必然与通信有内在的密切联系。有意思的是，时间与通信之间的这种联系也出现在相对论里，在那里的光速（可能用于同步事件的最快信号）是与时间和空间有关的基本常量。在处理时间和状态时，我们在计算模型领域所遭遇的复杂性，事实上，可能就是物理世界中最基本的复杂性的一种反映。

- 深刻认识了`计算`二字的含义，明白了计算机的局限性（[停机问题](https://github.com/jiacai2050/sicp/blob/master/exercises/04/4.15.md)），并不是所有问题都有解的；

当然，并不是说看完这本书就是“武林高手”了，今后还是要在不断实践中总结、积累，成为一位真正的 hacker。

好了，今天写到这里，作为万里长城的一个终点。😊
