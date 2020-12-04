---
categories:
- 理解计算机
date: 2019-01-09 20:14:54
tags:
- GC
- Java
title: Java 垃圾回收权威指北
---

毫无疑问，GC（垃圾回收） 已经是现代编程语言标配，为了研究这个方向之前曾经写过四篇[《深入浅出垃圾回收》](/blog/2018/06/15/garbage-collection-intro/)博文来介绍其理论，之后也看了不少网络上关于 JDK GC 原理、优化的文章，质量参差不齐，其中理解有误的文字以讹传讹，遍布各地，更是把初学者弄的晕头转向。
不仅仅是个人开发者的文章，一些[大厂的官博](https://engineering.linkedin.com/garbage-collection/garbage-collection-optimization-high-throughput-and-low-latency-java-applications)也有错误。
本文在实验+阅读 openjdk 源码的基础上，整理出一份相对来说比较靠谱的资料，供大家参考。

## 预备知识
### 术语

为方便理解 GC 算法时，需要先介绍一些常见的名词

- mutator，应用程序的线程
- collector，用于进行垃圾回收的线程
- concurrent（并发），指 collector 与 mutator 可以并发执行
- parallel（并行），指 collector 是多线程的，可以利用多核 CPU 工作
- young/old(也称Tenured) 代，根据大多数对象“朝生夕死”的特点，现代 GC 都是分代

一个 gc 算法可以同时具有 concurrent/parallel 的特性，或者只具有一个。

### JDK 版本

- HotSpot 1.8.0_172
- [openjdk8u](https://openjdk.java.net/projects/jdk8u/)（changeset: 2298:1c0d5a15ab4c）

为了方便查看当前版本 JVM 支持的选项，建议配置下面这个 alias

```sh
alias jflags='java -XX:+UnlockDiagnosticVMOptions -XX:+PrintFlagsFinal -version'
```
然后就可以用 `jflags | grep XXX` 的方式来定位选项与其默认值了。

### 打印 GC 信息

```sh
-verbose:gc
-Xloggc:/data/logs/gc-%t.log
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+PrintGCCause
-XX:+PrintTenuringDistribution
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=10
-XX:GCLogFileSize=50M
-XX:+PrintPromotionFailure
```

## JDK 中支持的 GC

Java 8 中默认集成了哪些 GC 实现呢？ jflags 可以告诉我们

```sh
$ jflags |  grep "Use.*GC"
     bool UseAdaptiveGCBoundary                     = false                               {product}
     bool UseAdaptiveSizeDecayMajorGCCost           = true                                {product}
     bool UseAdaptiveSizePolicyWithSystemGC         = false                               {product}
     bool UseAutoGCSelectPolicy                     = false                               {product}
     bool UseConcMarkSweepGC                        = false                               {product}
     bool UseDynamicNumberOfGCThreads               = false                               {product}
     bool UseG1GC                                   = false                               {product}
     bool UseGCLogFileRotation                      = false                               {product}
     bool UseGCOverheadLimit                        = true                                {product}
     bool UseGCTaskAffinity                         = false                               {product}
     bool UseMaximumCompactionOnSystemGC            = true                                {product}
     bool UseParNewGC                               = false                               {product}
     bool UseParallelGC                             = false                               {product}
     bool UseParallelOldGC                          = false                               {product}
     bool UseSerialGC                               = false                               {product}
java version "1.8.0_172"
Java(TM) SE Runtime Environment (build 1.8.0_172-b11)
Java HotSpot(TM) 64-Bit Server VM (build 25.172-b11, mixed mode)
```
肉眼筛选下，就知道有如下几个相关配置：
- UseSerialGC
- UseParNewGC，
- UseParallelGC
- UseParallelOldGC
- UseConcMarkSweepGC
- UseG1GC

每个配置项都会对应两个 collector ，表示对 young/old 的不同收集方式。而且由于 JVM 不断的演化，不同 collector 的组合方式其实很复杂。而且在 Java 7u4 后，UseParallelGC 与 UseParallelOldGC 其实是等价的，openjdk 中有如下代码：

```cpp
  // hotspot/src/share/vm/runtime/arguments.cpp#set_gc_specific_flags
  // Set per-collector flags
  if (UseParallelGC || UseParallelOldGC) {
    set_parallel_gc_flags();
  } else if (UseConcMarkSweepGC) { // Should be done before ParNew check below
    set_cms_and_parnew_gc_flags();
  } else if (UseParNewGC) {  // Skipped if CMS is set above
    set_parnew_gc_flags();
  } else if (UseG1GC) {
    set_g1_gc_flags();
  }

```

我们可以用[下面的代码](https://stackoverflow.com/a/19837515/2163429)测试使用不同配置时，young/old 代默认所使用的 collector：

```java
package gc;
// 省略 import 语句
public class WhichGC {
    public static void main(String[] args) {
        try {
            List<GarbageCollectorMXBean> gcMxBeans = ManagementFactory.getGarbageCollectorMXBeans();
            for (GarbageCollectorMXBean gcMxBean : gcMxBeans) {
                System.out.println(gcMxBean.getName());
            }
        } catch (Exception exp) {
            System.err.println(exp);
        }
    }
}
```
```sh
$ java gc.WhichGC  # 两个输出分别表示 young/old 代的 collector
PS Scavenge
PS MarkSweep

$ java -XX:+UseSerialGC gc.WhichGC
Copy
MarkSweepCompact

$ java -XX:+UseParNewGC gc.WhichGC # 注意提示
Java HotSpot(TM) 64-Bit Server VM warning: Using the ParNew young collector with the Serial old collector is deprecated and will likely be removed in a future release
ParNew
MarkSweepCompact

$ java -XX:+UseParallelGC gc.WhichGC
PS Scavenge
PS MarkSweep # 虽然名为 MarkSweep，但其实现是 mark-sweep-compact

$ java -XX:+UseParallelOldGC gc.WhichGC # 与上面输出一致，不加 flag 时这样同样的输出
PS Scavenge
PS MarkSweep

$ java -XX:+UseConcMarkSweepGC gc.WhichGC # ParNew 中 Par 表示 parallel，表明采用并行方式收集 young 代
ParNew
ConcurrentMarkSweep  # 注意这里没有 compact 过程，也就是说 CMS 的 old 可能会产生碎片

$ java -XX:+UseG1GC gc.WhichGC
G1 Young Generation
G1 Old Generation
```

PS 开头的系列 collector 是 Java5u6 开始引入的。按照 [R 大的说法](https://hllvm-group.iteye.com/group/topic/27629)，这之前的 collector 都是在一个框架内开发的，所以 young/old 代的 collector 可以任意搭配，但 PS 系列与后来的 G1 不是在这个框架内的，所以只能单独使用。

使用 UseSerialGC 时 young 代的 collector 是 Copy，这是单线程的，PS Scavenge 与 ParNew 分别对其并行化，至于这两个并行 young 代 collector 的区别呢？这里再引用 [R 大的回复](https://hllvm-group.iteye.com/group/topic/37095#post-242695)：

1. PS以前是广度优先顺序来遍历对象图的，JDK6的时候改为默认用深度优先顺序遍历，并留有一个UseDepthFirstScavengeOrder参数来选择是用深度还是广度优先。在JDK6u18之后这个参数被去掉，PS变为只用深度优先遍历。ParNew则是一直都只用广度优先顺序来遍历 
2. PS完整实现了adaptive size policy，而ParNew及“分代式GC框架”内的其它GC都没有实现完（倒不是不能实现，就是麻烦+没人力资源去做）。所以千万千万别在用ParNew+CMS的组合下用UseAdaptiveSizePolicy，请只在使用UseParallelGC或UseParallelOldGC的时候用它。 
3. 由于在“分代式GC框架”内，ParNew可以跟CMS搭配使用，而ParallelScavenge不能。当时ParNew GC被从Exact VM移植到HotSpot VM的最大原因就是为了跟CMS搭配使用。 
4. 在PS成为主要的throughput GC之后，它还实现了针对NUMA的优化；而ParNew一直没有得到NUMA优化的实现。 

如果你对上面所说的 mark/sweep/compact 这些名词不了解，建议参考下面这篇文章：

- https://plumbr.io/handbook/garbage-collection-algorithms-implementations

其实原理很简单，和我们整理抽屉差不多，找出没用的垃圾，丢出去，然后把剩下的堆一边去。但是别忘了

> The evil always comes from details!

怎么定义「没用」？丢垃圾时还允不允许同时向抽屉里放新东西？如果允许放，怎么区别出来，以防止被误丢？抽屉小时，一个人整理还算快，如果抽屉很大，多个人怎么协作？

## 核心流程指北

### ParallelGC

SerialGC 采用的收集方式十分简单，没有并行、并发，一般用在资源有限的设备中。由于其简单，对其也没什么好说的，毕竟也没怎么用过 :-)
[ParallelGC](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/parallel.html) 相比之下，使用多线程来回收，这就有些意思了，比如
- 多个GC线程如何实现同步，需要注意一点，ParallelGC 运行时会 STW，因此不存在与 mutator 同步问题
- 回收时，并行度如何选择（也就是 GC 对应用本身的 overhead）

凭借仅有的 cpp 知识，大略扫一下 `parNewGeneration.cpp` 这个文件，大概是这样实现多个 GC 线程同步的：

> 每个 GC 线程对应一个 queue（叫 ObjToScanQueue），然后还支持不同 GC 线程间 steal，保证充分利用 cpu

```cpp
  // ParNewGeneration 构造方法
  for (uint i1 = 0; i1 < ParallelGCThreads; i1++) {
    ObjToScanQueue *q = new ObjToScanQueue();
    guarantee(q != NULL, "work_queue Allocation failure.");
    _task_queues->register_queue(i1, q);
  }
  // do_void 方法
  while (true) {

    ......
    // We have no local work, attempt to steal from other threads.

    // attempt to steal work from promoted.
    if (task_queues()->steal(par_scan_state()->thread_num(),
                             par_scan_state()->hash_seed(),
                             obj_to_scan)) {
      bool res = work_q->push(obj_to_scan);
      assert(res, "Empty queue should have room for a push.");

      //   if successful, goto Start.
      continue;

      // try global overflow list.
    } else if (par_gen()->take_from_overflow_list(par_scan_state())) {
      continue;
    }
    .......
  }
  

```

下面还是重点说一下我们开发者能控制的选项，

- `-XX:MaxGCPauseMillis=<N>` 应用停顿（STW）的的最大时间
- `-XX:GCTimeRatio=<N>`  GC 时间占整个应用的占比，默认 99。需要注意的是，它是这么用的 `1/(1+N)`，即默认 GC 占应用时间 1%。这么说来这个选项的意思貌似正好反了！
其实不仅仅是这个，类似的还有 `NewRatio` `SurvivorRatio`，喜欢八卦的可以看看[《我可能在跑一个假GC》](http://yoroto.io/wo-ke-neng-zai-pao-yi-ge-jia-gc/)

当然，上面两个指标是软限制，GC 会采用后面提到的自适应策略（Ergonomics）来调整 young/old 代大小来满足。

#### Ergonomics

每次 gc 后，会记录一些统计信息，比如 pause time，然后根据这些信息来决定
1. 目标是否满足
2. 是否需要调整代大小

可以通过 `-XX:AdaptiveSizePolicyOutputInterval=N` 来打印出每次的调整，N 表示每隔 N 次 GC 打印。
默认情况下，一个代增长或缩小是按照固定百分比，这样有助于达到指定大小。默认增加以 20% 的速率，缩小以 5%。也可以自己设定
```sh
-XX:YoungGenerationSizeIncrement=<Y>
-XX:TenuredGenerationSizeIncrement=<T>
-XX:AdaptiveSizeDecrementScaleFactor=<D>
# 如果增长的增量是 X，那么减少的减量则为 X/D
```
当然，一般情况下是不需要自己设置这三个值的，除非你有明确理由。

#### 使用场景

ParallelGC 另一个名字就表明了它的用途：吞吐量 collector。主要用在对延迟要求低，更看重吞吐量的应用上。
我们公司的数据导入导出、跑报表的定时任务，用的就是这个 GC。（能提供数据导入导出的都是良心公司呀！）
一般利用自适应策略就能满足需求。线上的日志大概这样子：

```sh
2018-12-27T22:14:19.006+0800: 5433.841: [GC (Allocation Failure) [PSYoungGen: 606785K->3041K(656896K)] 746943K->143356K(2055168K), 0.0157837 secs] [Times: user=0.03 sys=0.01, real=0.02 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.02         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
2018-12-27T22:21:36.581+0800: 5871.417: [GC (Allocation Failure) [PSYoungGen: 615905K->3089K(654848K)] 756220K->143504K(2053120K), 0.0157796 secs] [Times: user=0.02 sys=0.00, real=0.01 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.01         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
2018-12-27T22:28:51.669+0800: 6306.505: [GC (Allocation Failure) [PSYoungGen: 615953K->3089K(660992K)] 756368K->143664K(2059264K), 0.0178418 secs] [Times: user=0.03 sys=0.01, real=0.02 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.01         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
2018-12-27T22:36:17.738+0800: 6752.573: [GC (Allocation Failure) [PSYoungGen: 624145K->2896K(658944K)] 764720K->143576K(2057216K), 0.0144179 secs] [Times: user=0.02 sys=0.01, real=0.01 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.01         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
2018-12-27T22:43:40.208+0800: 7195.043: [GC (Allocation Failure) [PSYoungGen: 623952K->2976K(665088K)] 764632K->143720K(2063360K), 0.0135656 secs] [Times: user=0.03 sys=0.01, real=0.02 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.01         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
2018-12-27T22:48:59.110+0800: 7513.945: [GC (Allocation Failure) [PSYoungGen: 632224K->5393K(663040K)] 772968K->146241K(2061312K), 0.0230613 secs] [Times: user=0.05 sys=0.01, real=0.02 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.01         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
2018-12-27T22:54:05.871+0800: 7820.706: [GC (Allocation Failure) [PSYoungGen: 634641K->4785K(669696K)] 775489K->147601K(2067968K), 0.0173448 secs] [Times: user=0.04 sys=0.01, real=0.02 secs]
    UseAdaptiveSizePolicy actions to meet  *** reduced footprint ***
                       GC overhead (%)
    Young generation:        0.01         (attempted to shrink)
    Tenured generation:      0.00         (attempted to shrink)
    Tenuring threshold:    (attempted to decrease to balance GC costs) = 1
```

### CMS

CMS 相比于 ParallelGC，支持并发式的回收，虽然个别环节还是需要 STW，但相比之前已经小了很多；另一点不同是 old 代在 sweep 后，没有 compact 过程，而是通过 freelist 来将空闲地址串起来。CMS 具体流程还是参考下面的文章：

- https://plumbr.io/handbook/garbage-collection-algorithms-implementations/concurrent-mark-and-sweep

上述文章会针对 gc 日志里面的每行含义做解释，务必弄清楚每一个数字含义，这是今后调试优化的基础。网站找了个[比较详细的图](http://fengfu.io/2016/06/21/JVM-%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E5%99%A8CMS%E4%B9%8B%E5%90%84%E9%98%B6%E6%AE%B5%E6%95%B4%E7%90%86/)供大家参考：

![CMS 工作流程示意图](https://img.alicdn.com/imgextra/i4/581166664/O1CN01eiAx891z69sKEdsdy_!!581166664.jpg)

之前在有赞的同事阿杜写过一篇[《不可错过的CMS学习笔记》](https://www.jianshu.com/p/78017c8b8e0f) 推荐大家看看，主要是文章的思路比较欣赏，带着问题去探索。这里重申下 CMS 的特点：

- CMS 作用于 old 区，与 mutator 并发执行（因为是多线程的，所以也是并行的）；默认与 young 代 ParNew 算法一起工作

下面重点介绍以下三点：
- 误传最广的 CMF
- 影响最为严重的内存碎片问题
- 最被忽视的 Abortable Preclean

#### Concurrent mode failure

在每次 young gc 开始前，collector 都需要确保 old 代有足够的空间来容纳新晋级的对象（通过之前GC的统计估计），如果判断不足，或者当前判断足够，但是真正晋级对象时空间不够了（即发生 Promotion failure），那么就会发生 Concurrent mode failure（后面简写 CMF），CMF 发生时，不一定会进行 Full GC，而是这样的：

> 如果这时 CMS 会正在运行，则会被中断，然后根据 UseCMSCompactAtFullCollection、CMSFullGCsBeforeCompaction 和当前收集状态去决定后面的行为

有两种选择：
1. 使用跟Serial Old GC一样的LISP2算法的mark-compact来做 Full GC，或
2. 用CMS自己的mark-sweep来做不并发的（串行的）old generation GC （这种串行的模式在 openjdk 中称为 foreground collector，与此对应，并发模型的 CMS 称为 background collector）

UseCMSCompactAtFullCollection默认为true，CMSFullGCsBeforeCompaction默认是0，这样的组合保证CMS默认不使用foreground collector，而是用Serial Old GC的方式来进行 Full GC，而且在 JDK9 中，彻底去掉了这两个参数以及 foreground GC 模式，具体见：[JDK-8010202: Remove CMS foreground collection](https://bugs.openjdk.java.net/browse/JDK-8010202)，所以这两个参数就不需要再去用了。

这里还需要注意，上述两个备选策略的异同，它们所采用的算法与作用范围均不同：

1. Serial Old GC的算法是mark-compact（也可以叫做mark-sweep-compact，但要注意它不是“mark-sweep”）。具体算法名是LISP2。它收集的范围是整个GC堆，包括Java heap的young generation和old generation，以及non-Java heap的permanent generation。因而其名 Full GC
2. CMS的foreground collector的算法就是普通的mark-sweep。它收集的范围只是CMS的old generation，而不包括其它generation。因而它在HotSpot VM里不叫做Full GC

这里大家可能会有疑问，既然能够用多线程方式去进行 Full GC（比如 ParallelGC），那么 CMS 在降级时却采用了 Serial 的方式呢？从 [JDK-8130200](https://bugs.openjdk.java.net/browse/JDK-8130200) 里可以略知端倪，大概是这样的：

> Google 的开发人员实现了多线程版本的 Full GC，然后在 2015 年给 openjdk 提了个 PR，但是这个 PR 一直没人理，根据[邮件列表](http://mail.openjdk.java.net/pipermail/hotspot-gc-dev/2015-June/thread.html#13649)来看，主要是 CMS 没有 leader maintainer 了，其他 maintainer 又怕这个改动太大，带来今后巨大的维护成本，就一直没合这个 PR，再后来 G1 出来了，这个 PR 就更不受人待见了

解决 CMF 的方式，一般是尽早执行 CMS，可以通过下面两个参数设置：

```sh
-XX:CMSInitiatingOccupancyFraction=60
-XX:+UseCMSInitiatingOccupancyOnly
```
上述两个参数缺一不可，第一个表示 old 区占用量超过 60% 时开始执行 CMS，第二个参数禁用掉 JVM 的自适应策略，如果不设置这个 JVM 可能会忽略第一个参数。

此外，除了 CMF 能触发 Full GC 外，`System.gc()` 的方式也能触发，不过 CMS 有个选项，可以将这个单线程的 Full GC 转化为 CMS 并发收集过程，一般建议打开：`-XX:+ExplicitGCInvokesConcurrent`。

上述关于 CMF 解释主要参考
- [R 大的这个帖子](https://hllvm-group.iteye.com/group/topic/42365)
- http://blog.ragozin.info/2011/10/java-cg-hotspots-cms-and-heap.html
- 自己的消化吸收，如果有误肯定是我的（请留言指出），与 [R 大](https://www.zhihu.com/question/48973999)无关
  
#### 内存碎片
Promotion failure 一般是由于 heap 内存碎片过多导致检测空间足够，但是真正晋级时却没有足够连续的空间，监控 old 代碎片可以用下面的选项

```sh
-XX:+PrintGCDetails
-XX:+PrintPromotionFailure
-XX:PrintFLSStatistics=1
```

这时的 gc 日志大致是这样的

```sh
592.079: [ParNew (0: promotion failure size = 2698)  (promotion failed): 135865K->134943K(138240K), 0.1433555 secs]
Statistics for BinaryTreeDictionary:
------------------------------------
Total Free Space: 40115394
Max   Chunk Size: 38808526
Number of Blocks: 1360
Av.  Block  Size: 29496
Tree      Height: 22
```
重点是 Max Chunk Size 这个参数，如果这个值一直在减少，那么说明碎片问题再加剧。解决碎片问题可以按照下面步骤：
1. 尽可能提供较大的 old 空间，但是最好不要超过 32G，[超过了就没法用压缩指针了](https://www.elastic.co/guide/en/elasticsearch/guide/current/heap-sizing.html#compressed_oops)。
2. 尽早执行 CMS，即修改  initiating occupancy 参数
3. 减少 PLAB，我具体还没试过，可参考 [Java GC, HotSpot's CMS promotion buffers
](http://blog.ragozin.info/2011/11/java-gc-hotspots-cms-promotion-buffers.html) 这篇文章
4. 应用尽量不要去分配巨型对象


#### Abortable Preclean

![ParallelGC vs CMS 工作流程](https://img.alicdn.com/imgextra/i3/581166664/O1CN01iVE4uz1z69sCiXptB_!!581166664.png)
根据上图重新回顾下 CMS 工作流程。Openjdk 内部通过 `_collectorState` 这个变量实现不同状态的转变（采用状态机设计模式），在 `collect_in_background` 方法内有个大 switch 进行转化，对应的 case 顺序即为状态机转化顺序。

```cpp
  // concurrentMarkSweepGeneration.cpp#collect_in_background
  while (_collectorState != Idling) {
     ....
    switch (_collectorState) {
      case InitialMarking:
        {
          ReleaseForegroundGC x(this);
          stats().record_cms_begin();
          VM_CMS_Initial_Mark initial_mark_op(this);
          VMThread::execute(&initial_mark_op);
        }
        // The collector state may be any legal state at this point
        // since the background collector may have yielded to the
        // foreground collector.
        break;
      case Marking:
        // initial marking in checkpointRootsInitialWork has been completed
        if (markFromRoots(true)) { // we were successful
          assert(_collectorState == Precleaning, "Collector state should "
            "have changed");
        } else {
          assert(_foregroundGCIsActive, "Internal state inconsistency");
        }
        break;
      case Precleaning:
        if (UseAdaptiveSizePolicy) {
          size_policy()->concurrent_precleaning_begin();
        }
        // marking from roots in markFromRoots has been completed
        preclean();
        if (UseAdaptiveSizePolicy) {
          size_policy()->concurrent_precleaning_end();
        }
        assert(_collectorState == AbortablePreclean ||
               _collectorState == FinalMarking,
               "Collector state should have changed");
        break;
      case AbortablePreclean:
        if (UseAdaptiveSizePolicy) {
        size_policy()->concurrent_phases_resume();
        }
        abortable_preclean();
        if (UseAdaptiveSizePolicy) {
          size_policy()->concurrent_precleaning_end();
        }
        assert(_collectorState == FinalMarking, "Collector state should "
          "have changed");
        break;
      case FinalMarking:
        {
          ReleaseForegroundGC x(this);

          VM_CMS_Final_Remark final_remark_op(this);
          VMThread::execute(&final_remark_op);
        }
        assert(_foregroundGCShouldWait, "block post-condition");
        break;
      case Sweeping:
        if (UseAdaptiveSizePolicy) {
          size_policy()->concurrent_sweeping_begin();
        }
        // final marking in checkpointRootsFinal has been completed
        sweep(true);
        assert(_collectorState == Resizing, "Collector state change "
          "to Resizing must be done under the free_list_lock");
        _full_gcs_since_conc_gc = 0;

        // Stop the timers for adaptive size policy for the concurrent phases
        if (UseAdaptiveSizePolicy) {
          size_policy()->concurrent_sweeping_end();
          size_policy()->concurrent_phases_end(gch->gc_cause(),
                                             gch->prev_gen(_cmsGen)->capacity(),
                                             _cmsGen->free());
        }

      case Resizing: {
        ....
        break;
      }
      case Resetting:
        ......
        break;
      case Idling:
      default:
        ShouldNotReachHere();
        break;
    }
    .......
  }

```
可以看到里面有 Precleaning 与 AbortablePreclean 两个状态，他们底层都是调用 `preclean_work` 进行具体工作，区别只是 
- precleaning 阶段只执行一次，而 AbortablePreclean 是个迭代执行的过程，直到某个条件不成立。先看看 AbortablePreclean 阶段受哪些条件限制，再来介绍 preclean_work 里面做的具体事情。

```cpp
  // concurrentMarkSweepGeneration.cpp#abortable_preclean()
  
  if (get_eden_used() > CMSScheduleRemarkEdenSizeThreshold) {
    size_t loops = 0, workdone = 0, cumworkdone = 0, waited = 0;
    while (!(should_abort_preclean() ||
             ConcurrentMarkSweepThread::should_terminate())) {
      workdone = preclean_work(CMSPrecleanRefLists2, CMSPrecleanSurvivors2);
      cumworkdone += workdone;
      loops++;
      // Voluntarily terminate abortable preclean phase if we have
      // been at it for too long.
      if ((CMSMaxAbortablePrecleanLoops != 0) &&
          loops >= CMSMaxAbortablePrecleanLoops) {
        if (PrintGCDetails) {
          gclog_or_tty->print(" CMS: abort preclean due to loops ");
        }
        break;
      }
      if (pa.wallclock_millis() > CMSMaxAbortablePrecleanTime) {
        if (PrintGCDetails) {
          gclog_or_tty->print(" CMS: abort preclean due to time ");
        }
        break;
      }
      // If we are doing little work each iteration, we should
      // take a short break.
      if (workdone < CMSAbortablePrecleanMinWorkPerIteration) {
        // Sleep for some time, waiting for work to accumulate
        stopTimer();
        cmsThread()->wait_on_cms_lock(CMSAbortablePrecleanWaitMillis);
        startTimer();
        waited++;
      }
    }
    if (PrintCMSStatistics > 0) {
      gclog_or_tty->print(" [%d iterations, %d waits, %d cards)] ",
                          loops, waited, cumworkdone);
    }
  }
```
条件包括下面几个：
1. 首先要 eden 大于 CMSScheduleRemarkEdenSizeThreshold（默认 2M）时才继续
2. 下面的 while 里面条件主要是为了与 foregroundGC 做同步用的，这里可以先忽略
3. while 后面的第一个 if 表示这个阶段执行的次数小于 CMSMaxAbortablePrecleanLoops 时才继续，由于这个值默认为 0，所以默认不会进入这个分支
4. 紧接着的那个 if 表示这个阶段的运行时间不能大于 CMSMaxAbortablePrecleanTime，默认是 5s

好了，上面就是 abortable preclean 迭代执行的条件，任意一个不满足即会转到下一个状态。
下面介绍 `preclean_work` 里做的事情，主要包含两个：
1. 根据 card marking 状态，重新 mark 在 concurrent mark 阶段，mutator 又有访问的对象
![preclean 执行前 card mark 以及对象 live mark 状态](https://img.alicdn.com/imgextra/i1/581166664/O1CN012DBLER1z69sHf5zR6_!!581166664.png)
![preclean 执行后 card mark 以及对象 live mark 状态](https://img.alicdn.com/imgextra/i3/581166664/O1CN01Rdi6pg1z69sIciHq8_!!581166664.png)
2. 对 eden 进行抽样（sample），把 eden 划分成大小相近的 chunk ，且每个 chunk 的起始地址都是对象的起始地址。

把 eden 划分成不同 chunk 主要是为了方便后面的 remark 阶段并发执行。试想一下，如果 remark 阶段以多线程的方式重新 mark 被 mutator 访问的对象，势必要将 eden 划分为不同区域，然后不同区域由不同的线程去 mark，这里的区域就是 chunk。这个抽样过程主要是保证不同 chunk 大小一致，这样不同线程的工作量就均匀了。根据[这个功能作者测试](http://hiroshiyamauchi.blogspot.com/2013/08/parallel-initial-mark-and-more-parallel.html)，这个抽样使得 remark 阶段的 STW 由 500ms 减到 100ms

不过这个抽样阶段，也可能发生在 ParNew 过程中，是由 CMSEdenChunksRecordAlways 这个选项控制的，而且默认是 true，表示 preclean 阶段不对 eden 进行抽样，而是在 ParNew 运行时抽样，相关代码：

```cpp
// concurrentMarkSweepGeneration.cpp 
// preclean_work 会调用 sample_eden，但是这里的 !CMSEdenChunksRecordAlways 默认为 false
// 所以这里不会进行抽样
void CMSCollector::sample_eden() {
  if (_eden_chunk_array != NULL && !CMSEdenChunksRecordAlways) {
    ...... do sample
  }

}
// defNewGeneration.cpp#allocate() 
  HeapWord* result = eden()->par_allocate(word_size);
  if (result != NULL) {
    if (CMSEdenChunksRecordAlways && _next_gen != NULL) {
      // 这里会调用 concurrentMarkSweepGeneration 里的 sample_eden_chunk
      _next_gen->sample_eden_chunk();
    }
    return result;
  }
// concurrentMarkSweepGeneration.cpp 
void CMSCollector::sample_eden_chunk() {
  // 默认会在这里进行抽样
  if (CMSEdenChunksRecordAlways && _eden_chunk_array != NULL) {
     ..... do sample
  }
}
```

## 调优

说到优化，让很多人望而却步，一方便有人不断在说“不要过早优化”，另一方面在真正有问题时，不知道如何入手。这里介绍我自己的一些经验供大家参考。

既然提到 GC 优化，首先要明确衡量 GC 的几个指标，LinkedIn 在这方面值得借鉴，在 [Tuning Java Garbage Collection for Web Services
](https://engineering.linkedin.com/26/tuning-java-garbage-collection-web-services) 提出了从 gc 日志中可以获知的 5 个指标：

1. Allocation Rate: the size of the young generation divided by the time between young generation collections
2. Promotion Rate: the change in usage of the old gen over time (excluding collections)
3. Survivor Death Ratio: when looking at a log, the size of survivors in age N divided by the size of survivors in age N-1 in the previous collection
4. Old Gen collection times: the total time between a CMS-initial-mark and the next CMS-concurrent-reset. You'll want both your 'normal' and the maximum observed
5. Young Gen collection times: both normal and maximum. These are just the "total collection time" entries in the logs Old Gen Buffer: 
```sh
the promotion rate*the maximum Old Gen collection time*(1 + a little bit)
```

直接从纯文本的 gc 日志中得出这 5 项指标比较困难，还好有个比较好用的开源工具 [gcplot](https://github.com/dmart28/gcplot)，借助 docker，一行命令即可启动

```sh
docker run -d -p 8080:80 gcplot/gcplot
```

如果发现 gcplot 里面的指标不符合你的预期，那就可以根据所使用 GC 算法的特点进行优化了。

### 实战

利用 gcplot，我对公司内部 API 服务（使用 CMS）进行了一次优化，效果较为明显：

优化前的配置：Xmx/Xms 均为 4G，CMSInitiatingOccupancyFraction=60，下面是使用 gcplot 得到的一些数据

| Percentiles | STW Pause (ms) |
|----------- |-------------- |
| 50%         | 22.203         |
| 90%         | 32.872         |
| 95%         | 40.255         |
| 99%         | 76.724         |
| 99.9%       | 317.584        |

- STW Pause per Minute: 3.396 secs
- STW Events per Minute: 133

| Promoted Total           | 17.313 GB |
|----------- |-------------- |
| Promotion Rate (MB/Sec)  | 5.99      |
| Allocated Total          | 5.053 TB  |
| Allocation Rate (MB/Sec) | 1273.73   |

优化后的配置：Xmx/Xms 均为 4G, NewRatio 为 1， CMSInitiatingOccupancyFraction=80。
这么修改主要是增加 young 区空间，因为对于 Web 服务来说，除了一些 cache 外，没什么常驻内存的对象；通过把 OccupancyFraction 调大，延迟 CMS 发生频率，还是基于前面的推论，大多数对象不会晋级到 old 代，所以发生碎片的概率也不会怎么大。下面是优化后的相关参数，也证明了上面的猜想

| percentiles | STW pause(ms) |
|----------- |------------- |
| 50%         | 19.75         |
| 90%         | 30.334        |
| 95%         | 35.441        |
 99%         | 53.5          |
| 99.9%       | 120.008       |

- STW Pause per Minute: 826.607 ms
- STW Events per Minute: 38

| Promoted Total           | 6.182 GB  |
|----------- |------------- |
| Promotion Rate (MB/Sec)  | 0.29      |
| Allocated Total          | 28.254 TB |
| Allocation Rate (MB/Sec) | 1121.29   |

### 参考资料

虽然本文一开始指出 LinkedIn 文章中存在理解误差，但是那篇文章的思路还是值得解决，下面再次给出链接
- https://engineering.linkedin.com/garbage-collection/garbage-collection-optimization-high-throughput-and-low-latency-java-applications
- 段子手王四哥对上面文章的指正：[难道他们说的都是真的？](http://yoroto.io/nan-dao-ta-men-shuo-de-du-shi-zhen-de/)
- 江南白衣的 [关键业务系统的JVM参数推荐](http://calvin1978.blogcn.com/articles/jvmoption-7.html)，说到这里就不得不提 [vjtools](https://github.com/vipshop/vjtools/) 了，我目前主要用了 vjtop。

## 总结

上面基本把 ParallelGC 与 CMS 核心点过了一遍，然后顺带介绍了下优化，主要还是熟悉 GC 日志中的每个指标含义，理解透后再去决定是否需要优化。关于 G1 本文没有过多介绍，主要是用的确实不多，后面会尝试把服务升级到 G1 后再来写写它。

本文一开始就说网络上关于 GC 的误解很多，本文可能也是这样的，虽然我已经尽可能保证“正确”，但还是需要大家带着辩证的眼光来看。元芳,你怎么看？

## 扩展阅读

- https://www.infoq.com/articles/G1-One-Garbage-Collector-To-Rule-Them-All
- https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/cms.html
- https://blogs.oracle.com/jonthecollector/did-you-know
- https://dzone.com/articles/how-tame-java-gc-pauses
- https://mechanical-sympathy.blogspot.com/2013/07/java-garbage-collection-distilled.html
- https://www.oracle.com/technetwork/java/javase/memorymanagement-whitepaper-150215.pdf

