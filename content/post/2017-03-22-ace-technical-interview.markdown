title: “玩转” 技术面试——链表的函数表示法
date: 2017-03-22 11:31:11
categories: 他山之石
tags: [Clojure]
---

## 简介

[《Acing the technical interview》](https://aphyr.com/posts/340-acing-the-technical-interview)，老外写的白板面试的调侃文，声色并茂，兼具叙述文的生动与技术文的抽象。文中用函数来模拟链表的表示法我在[《编程语言的基石——Lambda calculus》](/blog/2014/10/12/lambda-calculus-introduction/)里面有深入讲解，感兴趣的读者可以参考。本文最后，给出了 Python、Ruby 语言中链表的函数表示。

文中个别语句我翻译的不是很好或者没有翻译，希望感兴趣的读者予以补充。


## 正文

如果你打算找一份程序员（software witch）的工作，那么你极有可能需要通过白板面试。白板面试已经成了我们程序员的家常便饭：在电脑桌面上排列出一组好看的 `xterm`，不由自主地在周边的文件夹里运行`ls`，以防环境在昨晚有什么变动——这就像在厨房的抽屉里找东西，而这个厨房储藏了各种奇怪的法兰（flanges，使管子与管子及和阀门相互连接的零件）、螺丝刀以及各种不知名的家用电器上掉下来的零件形成的各种奇怪的塑料碎片，现在谁也不知道这些家用电器的用途，或许从来就没知道过，但即使如此，我们还必须小心翼翼的对待它们。我现在给你分析一个非常常见的面试问题：反转链表（reverse linked list）。


首先，我们需要一个链表。清空你工作空间里面不必要的`xterm`窗口，然后递归地在具有保护性的括号（译者注：Lisp 里面用括号分割代码块）里面撒些盐（译者注：这句话非常形象，想想我们做菜时放盐的场景，表示要开始了，忽略某些人后放盐）。从零开始反转一个链表。

```
(defn cons [h t] #(if % h t))
```

“这不是一个链表，这只是一个`if`语句”，面试官说。
“但其他部分是链表，还有什么问题嘛？”你回答到，同时不屑地翻了一个白眼。
```
user=> (def x (cons 1 (cons 2 nil)))
#'user/x
user=> (x true)
1
user=> ((x false) true)
2
```
“`x`到底是什么？”面试官尽量让自己看起来友善些。
答案在 REPL 里，但是不要被它一时误导了，它们可不是你的朋友。这与你在接待厅的誓言是相违背的（译者注：宣誓时一般都要求虔诚对待别人）。
```
user=> x
#object[user$cons$cell__4431 0x3b89cc1c "user$cons$cell__4431@3b89cc1c"]
```
“了解一个事物最好的方式就是对它命名”，你建议到。好的名字非常有意义（True names have power）。由 Ursula K. Le Guin 发明的 [K 语言](https://en.wikipedia.org/wiki/K_%28programming_language%29)是最古老、最精练的魔幻型语言之一。让一个新语言映射成你自己的词汇需要忘掉自己之前的认知，原有知识会让你的记忆疼痛（译者注：作者是想表达 Lisp 里面惯用法与常见的语言差距比较大，不能简单类比）。

“呃... 那好，那你会怎么从这个链表里面取出一个元素呢？”

在你脑海中有非常漂亮解决方式，就像你赤裸的双脚下铺开了红地毯。奥斯卡的明星昨晚在这里出席过，但你还是等待着不同的明星来亲吻你。这就像你住在[瑟略島](https://en.wikipedia.org/wiki/S%C3%B8r%C3%B8ya)（挪威第八大岛） 的山上时，月亮就是你的爱人。（译者注：这里作者应该是想表达 s-expression 很优美）。除了一些边界条件的检查，你在第一时间写出了正确的获取一个元素的代码：
```
(defn nth [l n]
  (when l (if (= 0 n)
            (l true)
            (recur (l false) (dec n)))))
```

“你能不能给我写一个正常的链表，像 Python 里面的那样？”

你摩拳擦掌起来，双脚站在地板上，从头开始写出了一个具有良好缩进格式的`print`函数。现在你的手掌长满老茧，眼睑里流露出晶莹的、碳黑的雪花（译者注：这是可能是说作者写这种函数很多次了，不屑于写了）。每一个函数都是有代价的，当然，除非它们是无副作用的纯函数。
```
(defn prn-list [l]
  (print "(")
  (loop [l l]
    (if (nil? l)
      (print ")\n")
      (do (print (l true))
          (when (l false)
            (print " "))
          (recur (l false))))))
```
没有时间去想有意义的变量名、示例、帮助文档（译者注：docstring，Clojure里面函数的注释）。在白板面试过程中，时间就是一切。 Pretend you are a Haskell programmer, as your grandmother was, before her continuation passed。（译者注：不清楚这句话作者想表达神马意思，懂 Haskell 同学解释下？）
```
user=> (prn-list (cons 1 (cons 2 (cons 3 nil))))
(1 2 3)
```
这时面试官终于安心地笑了，最起码上面的输出看起来终于正常了。“那么，开始反转吧，你需要....”

你突然攥住面试官的双手，这时他的大脑像紧张忙乱的闹钟发条似的发生了扭曲，飞掠而过心脏里面的绦虫，拍挞拍挞的心发生了偏斜，并且用古老的语言默背一首讽刺诗。
```
(defn reverse [l]
  (loop [r nil, l l]
    (if l
      (recur (cons (l true) r) (l false))
      r)))

user=> (prn-list (reverse (cons 1 (cons 2 (cons 3 nil)))))
(3 2 1)
```

当你放开面试官的手，他结结巴巴的说了些有礼貌的东西，拉上了兜帽上衣的拉锁来掩盖自己冷汗。下面这里会有其他会议，但是你不需要参加，你快点走吧（Send an eagle in your place ？是这么翻译嘛）。

他们肯定会决绝你，而且会嗤之以鼻，说你不符合他们的公司文化。Alight upon your cloud-pine, and exit through the window. （神马意思？）这地方不适合你。


## 其他实现

### Python

```
from __future__ import print_function


def cons(h, t):
    return lambda x: h if x else t


def printer(l):
    if l is None:
        print("nil")
    else:
        while l:
            e = l(True)
            print(e, end=' ')
            l = l(False)
        else:
            print("")


def reverse(l):
    reversed_l = None
    while l:
        e = l(True)
        reversed_l = cons(e, reversed_l)
        l = l(False)

    return reversed_l


l = cons(3, cons(2, cons(1, None)))

printer(l)
# 3 2 1

printer((reverse(l)))
# 1 2 3
```

### Ruby

```
def cons(h, t)
  lambda { |e| e ? h : t }
end

def printer(l)
  while l
    e = l.call true
    print e, ' '
    l = l.call false
  end
  puts ''
end

def reverse(l)
  reversed_l = nil
  while l
    e = l.call true
    reversed_l = cons e, reversed_l
    l = l.call false
  end
  return reversed_l
end

l = cons(3, cons(2, cons(1, nil)))
printer l
# 3 2 1
printer reverse l
# 1 2 3
```
