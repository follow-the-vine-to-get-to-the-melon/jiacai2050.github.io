---
title: 由浅入深学习 Lisp 宏之实战篇
date: 2017-10-01 10:13:05
tags: [Clojure]
categories: [编程语言]
---

本文是宏系列的第二篇文章，侧重于实战，对于新手建议先阅读宏系列的[理论篇](/blog/2017/08/31/master-macro-theory/)，之后再来看本文。当然如果你有一定基础，也可以直接阅读本文。
其次，希望读者能把本文的 Clojure 代码手动敲到 REPL 里面去运行、调试，直到完全理解。

## Code as data

在[理论篇](/blog/2017/08/31/master-macro-theory/)中，介绍了宏（macro）的本质：`在编译时期运行的函数`。宏相对于普通函数，具有如下特点：

1. 宏的参数不会求值（eval），是 symbol 字面量
2. 宏的返回值是 code（在运行期执行），不是一般的数据。

这两条特性蕴含着一非常重要的思想： [code as data](https://en.wikipedia.org/wiki/Homoiconicity) ，也被称为同像性（homoiconicity，来自希腊语单词 homo，意为与符号含义表示相同）。同像性使得在 Lisp 中去操作语法树（AST）显得十分自然，而这在非 Lisp 语言只能由编译器（Compiler）去操作。这里举一典型的例子：

```clj
(defmacro when [test & body]
  (list 'if test (cons 'do body)))
```

`'`代表 quote，作用是阻止后面的表达式求值，如果不使用`'`的话，在进行`(list 'if test ...)`求值时会报错，因为对 special form 单独进行求值是非法的，这里需要的仅仅是 `if` 字面量，list 函数执行后的结果（是一个 list）作为 code 插入到调用 when 的地方去执行。

```clj
(when (even? (rand-int 100))
  (println "good luck!")
  (println "lisp rocks!"))

;; when 展开后的形式 

(if (even? (rand-int 100))
  (do (println "good luck!") (println "lisp rocks!")))
```

### syntax-quote & unquote

对于一些简单的宏，可以采用像 when 那样的方式，使用 list 函数来形成要返回的 code，但对于复杂的宏，使用 list 函数来表示，会显得十分麻烦，看下 when-let 的实现：

```clj
(defmacro when-let [bindings & body]
  (let [form (bindings 0) tst (bindings 1)]
    `(let [temp# ~tst]
       (when temp#
         (let [~form temp#]
           ~@body)))))
```

这里返回的 list 使用 *`*（backtick）进行了修饰，这称为 syntax-quote，它与 quote `'` 类似，只不过在阻止表达式求值的同时，支持以下两个额外功能：

1. 表达式里的所有 symbol 会在当前 namespace 中进行 resolve，返回 fully-qualified symbol
2. 允许通过 `~`(unquote) 或 `~@`(slicing-unquote) 阻止部分表达式的 quote，以达到对它们求值的效果

可以通过下面一个例子来了解它们之间的区别：

```clj
(let [x '(* 2 3) y x]
  (println `y)
  (println ``y)
  (println ``~y)
  (println ``~~y)
  (println (eval ``~~y))
  (println `[~@y]))

;; 依次输出

user/y
(quote user/y)
user/y
(* 2 3)
6
[* 2 3]
```

这里尤其要注意理解嵌套 syntax-quote 的情况，为了得到正确的值，需要 unquote 相应的次数（上例中的第四个println），这在 macro-writing macro 中十分有用，后面会介绍的。
最后需要注意一点，在整个 Clojure 程序生命周期中，`(syntax-)quote`, `(slicing-)unquote` 是 [Reader](https://clojure.org/reference/reader) 来解析的，详见 [编译器工作流程](/blog/2017/02/05/clojure-compiler-analyze/#编译器工作流程)。可以通过`read-string`来验证：

```clj
user> (read-string "`y")
(quote user/y)
user> (read-string "``y")
(clojure.core/seq (clojure.core/concat (clojure.core/list (quote quote)) 
                                       (clojure.core/list (quote user/y))))
user> (read-string "``~y")
(quote user/y)
user> (read-string "``~~y")
y
```

## Macro Rules of Thumb 

在正式实战前，这里摘抄 JoyOfClojure 一书中关于写宏的一般准则：

1. 如果函数能完成相应功能，不要写宏。在需要构造语法抽象（比如`when`）或新的binding 时再去用宏
2. 写一个宏使用的 demo，并手动展开
3. 使用`macroexpand`, `macroexpand-1` 与 `clojure.walk/macroexpand-all` 去验证宏是如何工作的
4. 在 REPL 中测试
5. 如果一个宏比较复杂，尽可能拆分成多个函数

希望读者在写/读宏遇到困难时，思考是否对应了上述准则。

## In Action

前面介绍过，宏的一大应用场景是流程控制，比如上面介绍的 when、when-let，以及各种 do 的衍生品 dotimes、doseq，所以实战也从这里入手，构造一系列 do-primes，通过对它不断的完善修改，介绍写宏的技巧与注意事项。

```clj
(do-primes [n start end]
  body)
```

上面是 do-primes 的使用方式，它会遍历 `[start, end)` 范围内的素数，对于具体素数 n，执行 body 里面的内容。

### 使用 gensym 保证宏 Hygiene

```clj
(defn prime? [n]
  (let [guard (int (Math/ceil (Math/sqrt n)))]
    (loop [i 2]
      (if (zero? (mod n i))
        false
        (if (= i guard)
          true
          (recur (inc i)))))))

(defn next-prime [n]
  (if (prime? n)
    n
    (recur (inc n))))

(defmacro do-primes [[variable start end] & body]
  `(loop [~variable ~start]
     (when (< ~variable ~end)
       (when (prime? ~variable)
         ~@body)
       (recur (next-prime (inc ~variable))))))
```
上面的实现比较直接，首先定义了两个辅助函数，然后通过返回由 loop 构成的 code 来达到遍历的效果。简单测试下：

```clj
(do-primes [n 2 13]
  (println n))

;; 展开为

(loop [n 2]
  (when (< n 13)
    (when (prime? n) (println n))
    (recur (next-prime (inc n)))))

;; 最终输出 3 5 7 11      
```
达到预期。但上述实现有些问题：end 在循环中进行比较时多次进行了求值，如果传入的 end 不是固定的数字，而是一个函数，而我们又无法确定这个函数有无副作用，这就可能产生问题。
也许你会说，这个解决也很简单，在进行 loop 之前，用一个 let 先把 end 的值先算出来就可以了。这个确实能解决多次执行的问题，但是又引入另一个隐患：**end 先于 start 执行**。这会不会产生不良后果，我们同样无法预知，我们能做到的就是**尽量不用暴露宏的实现细节**，具体表现就是**保证宏参数的求值顺序**。所以有了下面的修改：

```clj
(defmacro do-primes2 [[variable start end] & body]
  `(let [start# ~start
         end# ~end]
     (loop [~variable start#]
       (when (< ~variable end#)
         (when (prime? ~variable)
           ~@body)
         (recur (next-prime (inc ~variable)))))))

(do-primes2 [n 2 (+ 10 (rand-int 30))]
  (println n))
;; 展开为
(let [start__17380__auto__ 2 end__17381__auto__ (+ 10 (rand-int 30))]
  (loop [n start__17380__auto__]
    (when (< n end__17381__auto__)
      (when (prime? n) (println n))
      (recur (next-prime (inc n))))))  

```
在 syntax-quote 里面，使用了 `name#` 的形式来定义 locals，这是 gensym 机制，用来生成全局唯一的 symbol，保证宏的“卫生”（[hygiene](http://clojure-doc.org/articles/language/macros.html#macro-hygiene-and-gensym)）。如果这里不使用 gensym，在 Common Lisp 里面可能会污染全局里面的同名变量，在 Clojure 里面，为了避免污染全局环境，name 部分会 resolve 成当前命名空间里面的变量，例如

```clj
(defmacro do-primes2-danger [[variable start end] & body]
  `(let [inner-start ~start
         inner-end ~end]
     (loop [~variable inner-start]
       (when (< ~variable inner-end)
         (when (prime? ~variable)
           ~@body)
         (recur (next-prime (inc ~variable)))))))

(do-primes2-danger [n 2 (+ 10 (rand-int 30))]
                        (println n))
;; 展开为
(let [user/inner-start 2
      user/inner-end (+ 10 (rand-int 30))]
  (loop [n user/inner-start] 
    (when (< n user/inner-end) 
      (when (prime? n) 
        (println n))
      (recur (next-prime (inc n))))))                        
```
通过宏展开的代码可以看到，这明显不是我们想要的，运行上述代码会直接报错
```
java.lang.RuntimeException：Can't let qualified name: user/inner-start
```
所以在定义内部 locals 时，一定要用 gensym 机制。如果能确保使用的名字不会造成污染，也可以使用 `~'name` 的形式来避免 resolve 这一过程。`~'name` 其实就是 `~(quote name)` 的简写，它在 syntax-quote 里面求值的结果就是 symbol 字面量 `name`：

```clj
(defmacro do-primes2-safe [[variable start end] & body]
  `(let [~'inner-start ~start
         ~'inner-end ~end]
     (loop [~variable ~'inner-start]
       (when (< ~variable ~'inner-end)
         (when (prime? ~variable)
           ~@body)
         (recur (next-prime (inc ~variable)))))))

(do-primes2-safe [n 2 (+ 10 (rand-int 30))]
                 (println n))
;; 展开为
(let [inner-start 2 inner-end (+ 10 (rand-int 30))]
  (loop [n inner-start]
    (when (< n inner-end)
      (when (prime? n) (println n))
      (recur (next-prime (inc n))))))
```


### Macro-writing macro

通过上面的例子，我们知道，gensym 是一种非常实用的技巧，所以我们完全有可能再进行一次抽象，构造 only-once 宏，来保证传入的参数按照顺序只求值一次：

```clj
(defmacro only-once [names & body]
  (let [gensyms (repeatedly (count names) gensym)]
    `(let [~@(interleave gensyms (repeat '(gensym)))]
       `(let [~~@(mapcat #(list %1 %2) gensyms names)]
          ~(let [~@(mapcat #(list %1 %2) names gensyms)]
             ~@body)))))

(defmacro do-primes3 [[variable start end] & body]
  (only-once [start end]
             `(loop [~variable ~start]
                (when (< ~variable ~end)
                  (when (prime? ~variable)
                    ~@body)
                  (recur (next-prime (inc ~variable)))))))

(do-primes3 [n 2 (+ 10 (rand-int 30))]
  (println n))

;; 展开为
(let [G__18605 2 G__18606 (+ 10 (rand-int 30))]
  (loop [n G__18605]
    (when (< n G__18606)
      (when (prime? n) (println n))
      (recur (next-prime (inc n))))))
```
only-once 的核心思想是用 gensym 来替换掉传入的 symbol（即 names），为了达到这种效果，它首先定义出一组与参数数目相同的 gensyms（分别记为#s1 #s2），然后在第二层 let 为这些 gensyms 做 binding，value 也是用 gensym 生成的（分别记为#s3 #s4），这一层的 let 的返回值将内嵌到 do-primes3 内：

```clj
(let [#s1 #s3 #s2 #s4]
  `(let [#s3 ~start #s3 ~end]
    (let [start #s1 end #s2]
      ~@body)))
```

第三层 let 的结果作为 code 内嵌到调用 do-primes3 处，即最终的展开式：

```clj
(let [#s3 2 #s4 (+ 10 (rand-int 30))]
  (loop [n #s3]
    (when (< n #s4)
      (when (prime? n) (println n))
      (recur (next-prime (inc n))))))
```

根据上述分析过程，可以看到第四层嵌套的 let 先于第三层嵌套的 let 执行，第四层 let 做 binding 时，是把 #s1 对应的 #s3 赋值给 start，#s2 对应的 #s4 赋值给 end，这样就成功的实现了 symbol 的替换。

only-once 属于 macro-writing macro 的范畴，就是说它使用的对象本身还是个宏，所以有一定的难度，主要是分清不同表达式的求值环境，这一点对于理解这一类宏非常关键。不过这一类宏大家应该很少能见到，更多的时候是使用辅助函数来分解复杂宏。比如我们这里就使用了两个辅助函数 prime? next-prime 来简化宏的写法。下面一个例子会阐述这一点。

### 使用辅助函数定义简化宏

`def-watched` 可以定义一个受监控的 var，在 root binding 改变时打印前后的值

```clj
(defmacro def-watched [name & value]
  `(do
     (def ~name ~@value)
     (add-watch (var ~name)
                :re-bind
                (fn [~'key ~'r old# new#]
                  (println '~name old# " -> " new#)))))

(def-watched foo 1)                  
(def foo 2)
;; 这时打印 foo 1  ->  2
```

为了简化 def-watched，可能会想把里面的函数提取出来：

```clj
(defn gen-watch-fn [name]
  (fn [k r o n]
    (println name ":" o " -> " n)))

(defmacro def-watched2 [name & value]
  `(do
     (def ~name ~@value)
     (add-watch (var ~name)
                :re-bind (gen-watch-fn '~name))))

(def-watched2 bar 1)                  
;; 展开为
(do (def bar 1) (add-watch #'bar :re-bind (gen-watch-fn 'bar)))
```
这时的效果和上面是一样的，请注意这里是把 gen-watch-fn 实现为了函数，如果用宏的话，会有什么效果呢？
```clj
;; 将 gen-watch-fn 改为 defmacro，其他均不变 
;; (def-watched2 bar 1) 展开后变成了
(do
  (def bar 1)
  (add-watch
    #'bar
    :re-bind
    #function[user/gen-watch-fn/fn--17288]))
```
这直接会报 No matching ctor found for class #function[user/gen-watch-fn/fn--17288]，由于 gen-watch-fn 是宏，它返回的是 code，而不是一般的 data，这也就是问题发生的缘由。

回想本文一开始介绍的宏的两个特性：参数是否需要求值，返回值是 code 还是 data，这是决定是否用宏的关键。

## 总结

本文一开始就明确指出 Lisp 中 code as data 的特性，这一点表面看似比较好理解，但是放到具体环境中时，就十分容易搞错，所以还是要多写宏，实战岀真知。
实战部分介绍了一些注意事项以及管用技巧，引入了相比来说难以理解的 macro-writing marco，完全理解它有一定难度，但也不是无法入手，理清 quote unquote 的作用机制，并且在 REPL 中不断调试，肯定能有所收获。
虽说不推荐使用宏解决问题，但是在有些时候，一个简单的宏不仅仅能省掉好几十行代码，而且能使逻辑更清晰，这时候也就不要“吝啬”了。

最后，希望通过宏系列这两篇文章的介绍，大家能对宏有更深的理解。如果有问题，欢迎留言讨论！
Happy Lisp！

## 参考

- [Quoting Without Confusion](https://8thlight.com/blog/colin-jones/2012/05/22/quoting-without-confusion.html)
- https://clojure.org/reference/reader#syntax-quote
- http://www.gigamonkeys.com/book/macros-defining-your-own.html
- https://hubpages.com/technology/Clojure-macro-writing-macros
- https://xivilization.net/~marek/blog/2013/09/17/clojure-and-hygienic-macros/
