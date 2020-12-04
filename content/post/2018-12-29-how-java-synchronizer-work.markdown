---
categories:
- 编程语言
date: 2018-12-29 22:40:42
tags:
- Java
title: Java 线程同步原理探析
---

现如今，服务器性能日益增长，并发（concurrency）编程已经“深入人心”，但由于冯诺依式计算机“指令存储，顺序执行”的特性，使得编写跨越时间维度的并发程序异常困难，所以现代编程语言都对并发编程提供了一定程度的支持，像 Golang 里面的 [Goroutines](https://tour.golang.org/concurrency/1)、Clojure 里面的 [STM（Software Transactional Memory）](https://clojure.org/reference/refs)、Erlang 里面的 [Actor](https://en.wikipedia.org/wiki/Actor_model)。

Java 对于并发编程的解决方案是多线程（Multi-threaded programming），而且 Java 中的线程 与 native 线程一一对应，多线程也是早期操作系统支持并发的方案之一（其他方案：多进程、IO多路复用）。

本文着重介绍 Java 中线程同步的原理、实现机制，更侧重操作系统层面，部分原理参考 [openjdk 源码](http://hg.openjdk.java.net/jdk/jdk/file/cfceb4df2499)。阅读本文需要对 CyclicBarrier、CountDownLatch 有基本的使用经验。

## JUC

在 Java 1.5 版本中，引入 [JUC](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/package-summary.html) 并发编程辅助包，很大程度上降低了并发编程的门槛，JUC 里面主要包括：
- 线程调度的 Executors
- 缓冲任务的 Queues
- 超时相关的 TimeUnit
- 并发集合（如 ConcurrentHashMap）
- 线程同步类（Synchronizers，如 CountDownLatch ）

个人认为其中最重要也是最核心的是线程同步这一块，因为并发编程的难点就在于如何保证「共享区域（专业术语：临界区，Critical Section）的访问时序问题」。

### AbstractQueuedSynchronizer

JUC 提供的同步类主要有如下几种：

- `Semaphore` is a classic concurrency tool.
- `CountDownLatch` is a very simple yet very common utility for blocking until a given number of signals, events, or conditions hold.
- A `CyclicBarrier` is a resettable multiway synchronization point useful in some styles of parallel programming.
- A `Phaser` provides a more flexible form of barrier that may be used to control phased computation among multiple threads.
- An `Exchanger` allows two threads to exchange objects at a rendezvous(约会) point, and is useful in several pipeline designs.

通过阅读其源码可以发现，其实现都基于 [AbstractQueuedSynchronizer](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/locks/AbstractQueuedSynchronizer.html) 这个抽象类（一般简写 AQS），正如其 javadoc 开头所说：

> Provides a framework for implementing blocking locks and related synchronizers (semaphores, events, etc) that rely on first-in-first-out (FIFO) wait queues. This class is designed to be a useful basis for most kinds of synchronizers that rely on a single atomic int value to represent state.

也就是说，AQS 通过维护内部的 FIFO 队列和具备原子更新的整型 state 这两个属性来实现各种锁机制，包括：是否公平，是否可重入，是否共享，是否可中断（interrupt），并在这基础上，提供了更方便实用的同步类，也就是一开始提及的 Latch、Barrier 等。

这里暂时不去介绍 AQS 实现细节与如何基于 AQS 实现各种同步类（挖个坑），感兴趣的可以移步美团的一篇文章[《不可不说的Java“锁”事》](https://tech.meituan.com/Java_Lock.html) 第六部分“独享锁 VS 共享锁”。

在学习 Java 线程同步这一块时，对我来说困扰最大的是「线程唤醒」，试想一个已经 wait/sleep/block 的线程，是如何响应 interrupt 的呢？当调用 Object.wait() 或 lock.lock() 时，JVM 究竟做了什么事情能够在调用 Object.notify 或 lock.unlock 时重新激活相应线程？

带着上面的问题，我们从源码中寻找答案。


## Java 如何实现堵塞、通知

### wait/notify

```java
    public final native void wait(long timeout) throws InterruptedException;
    public final native void notify();
```
在 JDK 源码中，上述两个方法均用 native 实现（即 cpp 代码），追踪相关代码

```cpp
// java.base/share/native/libjava/Object.c
static JNINativeMethod methods[] = {
    {"hashCode",    "()I",                    (void *)&JVM_IHashCode},
    {"wait",        "(J)V",                   (void *)&JVM_MonitorWait},
    {"notify",      "()V",                    (void *)&JVM_MonitorNotify},
    {"notifyAll",   "()V",                    (void *)&JVM_MonitorNotifyAll},
    {"clone",       "()Ljava/lang/Object;",   (void *)&JVM_Clone},
};
```
通过上面的 cpp 代码，我们大概能猜出 JVM 是使用 monitor 来实现的 wait/notify 机制，至于这里的 monitor 是何种机制，这里暂时跳过，接着看 lock 相关实现

### lock/unlock

LockSupport 是用来实现堵塞语义模型的基础辅助类，主要有两个方法：park 与 unpark。（在英文中，park 除了“公园”含义外，还有“停车”的意思）

```java
// LockSupport.java
    public static void unpark(Thread thread) {
        if (thread != null)
            UNSAFE.unpark(thread);
    }
    public static void park(Object blocker) {
        Thread t = Thread.currentThread();
        setBlocker(t, blocker);
        UNSAFE.park(false, 0L);
        setBlocker(t, null);
    }
// Unsafe.java
    /**
     * Unblocks the given thread blocked on {@code park}, or, if it is
     * not blocked, causes the subsequent call to {@code park} not to
     * block.  Note: this operation is "unsafe" solely because the
     * caller must somehow ensure that the thread has not been
     * destroyed. Nothing special is usually required to ensure this
     * when called from Java (in which there will ordinarily be a live
     * reference to the thread) but this is not nearly-automatically
     * so when calling from native code.
     *
     * @param thread the thread to unpark.
     */
    @HotSpotIntrinsicCandidate
    public native void unpark(Object thread);

    /**
     * Blocks current thread, returning when a balancing
     * {@code unpark} occurs, or a balancing {@code unpark} has
     * already occurred, or the thread is interrupted, or, if not
     * absolute and time is not zero, the given time nanoseconds have
     * elapsed, or if absolute, the given deadline in milliseconds
     * since Epoch has passed, or spuriously (i.e., returning for no
     * "reason"). Note: This operation is in the Unsafe class only
     * because {@code unpark} is, so it would be strange to place it
     * elsewhere.
     */
    @HotSpotIntrinsicCandidate
    public native void park(boolean isAbsolute, long time);

// hotspot/share/prims/unsafe.cpp
UNSAFE_ENTRY(void, Unsafe_Park(JNIEnv *env, jobject unsafe, jboolean isAbsolute, jlong time)) {
  HOTSPOT_THREAD_PARK_BEGIN((uintptr_t) thread->parker(), (int) isAbsolute, time);
  EventThreadPark event;

  JavaThreadParkedState jtps(thread, time != 0);
  thread->parker()->park(isAbsolute != 0, time);
  if (event.should_commit()) {
    post_thread_park_event(&event, thread->current_park_blocker(), time);
  }
  HOTSPOT_THREAD_PARK_END((uintptr_t) thread->parker());
} UNSAFE_END
    
```
通过上述 unsafe.cpp 可以看到每个 thread 都会有一个 Parker 对象，所以我们需要查看 parker 对象的定义

```cpp
// hotspot/share/runtime/park.hpp
class Parker : public os::PlatformParker
...
public:
  // For simplicity of interface with Java, all forms of park (indefinite,
  // relative, and absolute) are multiplexed into one call.
  void park(bool isAbsolute, jlong time);
  void unpark();

// hotspot/os/posix/os_posix.hpp
class PlatformParker : public CHeapObj<mtInternal> {
 protected:
  enum {
    REL_INDEX = 0,
    ABS_INDEX = 1
  };
  int _cur_index;  // which cond is in use: -1, 0, 1
  pthread_mutex_t _mutex[1];
  pthread_cond_t  _cond[2]; // one for relative times and one for absolute
  ...
};
```

看到这里大概就能知道 park 是使用 `pthread_mutex_t` 与 `pthread_cond_t` 实现。好了，到目前为止，就引出了 Java 中与堵塞相关的实现，不难想象，都是依赖底层操作系统的功能。

## OS 支持的同步原语

### Semaphore

并发编程领域的先锋人物 [Edsger Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra)（也是最短路径算法的作者）在 1965 年首次提出了信号量（ Semaphores） 这一概念来解决线程同步的问题。信号量是一种特殊的变量类型，为非负整数，只有两个特殊操作PV：
- P(s) 如果 s!=0，将 s-1；否则将当前线程挂起，直到 s 变为非零
- V(s) 将 s+1，如果有线程堵塞在 P 操作等待 s 变成非零，那么 V 操作会重启这些线程中的任意一个

注：Dijkstra 为荷兰人，名字 P 和 V 来源于荷兰单词 Proberen（测试）和Verhogen（增加），为方便理解，后文会用 Wait 与 Signal 来表示。

```cpp
struct semaphore {
     int val;
     thread_list waiting;  // List of threads waiting for semaphore
}
wait(semaphore Sem):    // Wait until > 0 then decrement
  // 这里用的是 while 而不是 if
  // 这是因为在 wait 过程中，其他线程还可能继续调用 wait
  while (Sem.val <= 0) {
    add this thread to Sem.waiting;
    block(this thread);
  }
  Sem.val = Sem.val - 1;
return;

signal(semaphore Sem):// Increment value and wake up next thread
     Sem.val = Sem.val + 1;
     if (Sem.waiting is nonempty) {
         remove a thread T from Sem.waiting;
         wakeup(T);
     }
```

有两点注意事项：
1. wait 中的「测试和减 1 操作」，signal 中的「加 1 操作」需要保证原子性。一般来说是使用硬件支持的 [read-modify-write 原语](https://en.wikipedia.org/wiki/Read-modify-write)，比如 test-and-set/fetch-and-add/compare-and-swap，除了硬件支持外，还可以用 [busy wait](https://en.wikipedia.org/wiki/Mutual_exclusion#Software_solutions) 的软件方式来模拟。
2. signal 中没有定义重新启动的线程顺序，也即多个线程在等待同一信号量时，无法预测重启哪一个线程

#### 使用场景

信号量为控制并发程序的执行提供了强有力工具，这里列举两个场景：

##### 互斥

信号量提供了了一种很方便的方法来保证对共享变量的互斥访问，基本思想是

> 将每个共享变量（或一组相关的共享变量）与一个信号量 s （初始化为1）联系起来，然后用 wait/signal 操作将相应的临界区包围起来。

二元信号量也被称为互斥锁（mutex，mutual exclusve, 也称为 binary semaphore），wait 操作相当于加锁，signal 相当于解锁。
一个被用作一组可用资源的计数器的信号量称为计数信号量（counting semaphore）


##### 调度共享资源

除了互斥外，信号量的另一个重要作用是调度对共享资源的访问，比较经典的案例是生产者消费者，伪代码如下：

```cpp
emptySem = N
fullSem = 0
// Producer
while(whatever) {
    locally generate item
    wait(emptySem)
    fill empty buffer with item
    signal(fullSem)
}
// Consumer
while(whatever) {
    wait(fullSem)
    get item from full buffer
    signal(emptySem)
    use item
}
```

#### POSIX 实现
POSIX 标准中有定义信号量相关的逻辑，在 [semaphore.h](http://pubs.opengroup.org/onlinepubs/007904875/basedefs/semaphore.h.html) 中，为 sem_t 类型，相关 API：

```cpp
// Intialize: 
sem_init(&theSem, 0, initialVal);
// Wait: 
sem_wait(&theSem);
// Signal: 
sem_post(&theSem);
// Get the current value of the semaphore:       
sem_getvalue(&theSem, &result);
```
信号量主要有两个缺点：
- Lack of structure，在设计大型系统时，很难保证 wait/signal 能以正确的顺序成对出现，顺序与成对缺一不可，否则就会出现死锁！
- Global visiblity，一旦程序出现死锁，整个程序都需要去检查

解决上述两个缺点的新方案是[监控器（monitor）](https://en.wikipedia.org/wiki/Monitor_%28synchronization%29)。

### Monitors

[C. A. R. Hoare](https://en.wikipedia.org/wiki/C._A._R._Hoare)（也是 Quicksort 的作者） 在 1974 年的论文 [Monitors: an operating system structuring concept](https://dl.acm.org/citation.cfm?doid=355620.361161) 首次提出了「监控器」概念，它提供了对信号量互斥和调度能力的更高级别的抽象，使用起来更加方便，一般形式如下：
```
monitor1 . . . monitorM
process1 . . . processN
```
我们可以认为监控器是这么一个对象：
- 所有访问同一监控器的线程通过条件变量（condition variables）间接通信
- 某一个时刻，只能有一个线程访问监控器

#### Condition variables

上面提到监控器通过条件变量（简写 cv）来协调线程间的通信，那么条件变量是什么呢？它其实是一个 FIFO 的队列，用来保存那些因等待某些条件成立而被堵塞的线程，对于一个条件变量 c 来说，会关联一个断言（assertion） P。线程在等待 P 成立的过程中，该线程不会锁住该监控器，这样其他线程就能够进入监控器，修改监控器状态；在 P 成立时，其他线程会通知堵塞的线程，因此条件变量上主要有三个操作：
1. `wait(cv, m)` 等待 cv 成立，m 表示与监控器关联的一 mutex 锁
2. `signal(cv)` 也称为 `notify(cv)` 用来通知 cv 成立，这时会唤醒等待的线程中的一个执行。根据唤醒策略，监控器分为两类：Hoare vs. Mesa，后面会介绍
3. `broadcast(cv)` 也称为 `notifyAll(cv)` 唤醒所有等待 cv 成立的线程

##### POSIX 实现

在 pthreads 中，条件变量的类型是 `pthread_cond_t`，主要有如下几个方法：

```cpp
// initialize
pthread_cond_init() 
pthread_cond_wait(&theCV, &someLock);
pthread_cond_signal(&theCV);
pthread_cond_broadcast(&theCV);
```

#### 使用方式

在 pthreads 中，所有使用条件变量的地方都必须用一个 mutex 锁起来，这是为什么呢？看下面一个例子：
```cpp
pthread_mutex_t myLock;
pthread_cond_t myCV;
int count = 0;

// Thread A
pthread_mutex_lock(&myLock);
while(count < 0) {
    pthread_cond_wait(&myCV, &myLock);
}
pthread_mutex_unlock(&myLock);

// Thread B

pthread_mutex_lock(&myLock);
count ++;
while(count == 10) {
    pthread_cond_signal(&myCV);
}
pthread_mutex_unlock(&myLock);
```
如果没有锁，那么
- 线程 A 可能会在其他线程将 count 赋值为10后继续等待
- 线程 B 无法保证加一操作与测试 count 是否为零 的原子性

这里的关键点是，在进行条件变量的 wait 时，会释放该锁，以保证其他线程能够将之唤醒。不过需要注意的是，在线程 B 通知（signal） myCV 时，线程 A 无法立刻恢复执行，这是因为 myLock 这个锁还被线程 B 持有，只有在线程 B `unlock(&myLock)` 后，线程 A 才可恢复。总结一下：
1. wait 时会释放锁
2. signal 会唤醒等待同一 cv 的线程
3. 被唤醒的线程需要重新获取锁，然后才能从 wait 中返回

#### Hoare vs. Mesa 监控器语义

在上面条件变量中，我们提到 signal 在调用时，会去唤醒等待同一 cv 的线程，根据唤醒策略的不同，监控器也分为两类：

- Hoare 监控器（1974），最早的监控器实现，在调用 signal 后，会立刻运行等待的线程，这时调用 signal 的线程会被堵塞（因为锁被等待线程占有了）
- Mesa 监控器（Xerox PARC, 1980），signal 会把等待的线程重新放回到监控的 ready 队列中，同时调用 signal 的线程继续执行。这种方式是现如今 pthreads/Java/C# 采用的

这两类监控器的关键区别在于等待线程被唤醒时，需要重新检查 P 是否成立。

![监控器工作示意图](https://img.alicdn.com/imgextra/i4/581166664/O1CN01opA7ut1z69s6EhwrR_!!581166664.png)

上图表示蓝色的线程在调用监控器的 get 方式时，数据为空，因此开始等待 emptyFull 条件；紧接着，红色线程调用监控器的 set 方法改变 emptyFull 条件，这时
- 按照 Hoare 思路，蓝色线程会立刻执行，并且红色线程堵塞
- 按照 Mesa 思路，红色线程会继续执行，蓝色线程会重新与绿色线程竞争与监控器关联的锁

#### Java 中的监控器

在 Java 中，每个对象都是一个监控器（因此具备一个 lock 与 cv），调用对象 o 的 synchronized 方法 m 时，会首先去获取 o 的锁，除此之外，还可以调用 o 的 wait/notify/notify 方法进行并发控制

### Big Picture

![操作系统并发相关 API 概括图](https://img.alicdn.com/imgextra/i3/581166664/O1CN01RZViZw1z69s99tJfI_!!581166664.png)
来源：https://www.cs.princeton.edu/courses/archive/fall11/cos318/lectures/L8_SemaphoreMonitor_v2.pdf

## Interruptible

通过介绍操作系统支持的同步原语，我们知道了 park/unpark、wait/notify 其实就是利用信号量（ `pthread_mutex_t`）、条件变量（ `pthread_cond_t`）实现的，其实监控器也可以用信号量来实现。在查看 AQS 中，发现有这么一个属性：
```java
    /**
     * The number of nanoseconds for which it is faster to spin
     * rather than to use timed park. A rough estimate suffices
     * to improve responsiveness with very short timeouts.
     */
    static final long spinForTimeoutThreshold = 1000L;
```
也就是说，在小于 1000 纳秒时，await 条件变量 P 时，会使用一个循环来代替条件变量的堵塞与唤醒，这是由于堵塞与唤醒本身的操作开销可能就远大于 await 的 timeout。相关代码：

```java
// AQS 的 doAcquireNanos 方法节选
for (;;) {
    final Node p = node.predecessor();
    if (p == head && tryAcquire(arg)) {
        setHead(node);
        p.next = null; // help GC
        failed = false;
        return true;
    }
    nanosTimeout = deadline - System.nanoTime();
    if (nanosTimeout <= 0L)
        return false;
    if (shouldParkAfterFailedAcquire(p, node) &&
        nanosTimeout > spinForTimeoutThreshold)
        LockSupport.parkNanos(this, nanosTimeout);
    if (Thread.interrupted())
        throw new InterruptedException();
}
```

在 JUC 提供的高级同步类中，acquire 对应 park，release 对应 unpark，interrupt 其实就是个布尔的 flag 位，在 unpark 被唤醒时，检查该 flag ，如果为 true，则会抛出我们熟悉的 InterruptedException。

`Selector.select()` 响应中断异常的逻辑有些特别，因为对于这类堵塞 IO 操作来说，没有条件变量的堵塞唤醒机制，我们可以再看下 Thread.interrupt 的实现

```java
    public void interrupt() {
        if (this != Thread.currentThread())
            checkAccess();

        synchronized (blockerLock) {
            Interruptible b = blocker;
            if (b != null) {
                interrupt0();           // Just to set the interrupt flag
                b.interrupt(this);
                return;
            }
        }
        interrupt0();
    }
```
OpenJDK 使用了这么一个技巧来实现堵塞 IO 的中断唤醒：在一个线程被堵塞时，会关联一个 Interruptible 对象。
对于 Selector 来说，在开始时，会关联这么一个[Interruptible 对象](http://hg.openjdk.java.net/jdk/jdk/file/cfceb4df2499/src/java.base/share/classes/java/nio/channels/spi/AbstractInterruptibleChannel.java#l154)：

```java
    protected final void begin() {
        if (interruptor == null) {
            interruptor = new Interruptible() {
                    public void interrupt(Thread target) {
                        synchronized (closeLock) {
                            if (closed)
                                return;
                            closed = true;
                            interrupted = target;
                            try {
                                AbstractInterruptibleChannel.this.implCloseChannel();
                            } catch (IOException x) { }
                        }
                    }};
        }
        blockedOn(interruptor);
        Thread me = Thread.currentThread();
        if (me.isInterrupted())
            interruptor.interrupt(me);
    }

```
当调用 interrupt 方式时，会关闭该 channel，这样就会关闭掉这个堵塞线程，可见为了实现这个功能，代价也是比较大的。LockSupport.park 中采用了类似技巧。

## 总结

也许基于多线程的并发编程不是最好的（可能是最复杂的，Clojure 大法好 :-），但却是最悠久的。
即便我们自己不去写往往也需要阅读别人的多线程代码，而且能够写出“正确”（who knows?）的多线程程序往往也是区分 senior 与 junior 程序员的标志，希望这篇文章能帮助大家理解 Java 是如何实现线程控制，有疑问欢迎留言指出，谢谢！

## 参考

- https://carlmastrangelo.com/blog/javas-mysterious-interrupt
- [Java的LockSupport.park()实现分析](https://blog.csdn.net/hengyunabc/article/details/28126139)
- 课件 [COMP3151/9151 Foundations of Concurrency Lecture 6 - Semaphores, Monitors, POSIX Threads, Java](http://www.cse.unsw.edu.au/~cs3151/17s2/lec/PDF/lecture06a.pdf)
- 课件 http://crystal.uta.edu/~ylei/cse6324/data/semaphore.pdf
- 课件 https://cs61.seas.harvard.edu/wiki/images/1/12/Lec19-Semaphores.pdf
- [Mutexes and Semaphores Demystified](https://barrgroup.com/Embedded-Systems/How-To/RTOS-Mutex-Semaphore)
- https://book.douban.com/subject/1888733/
- https://en.wikipedia.org/wiki/Mutual_exclusion
- https://stackoverflow.com/questions/3513045/conditional-variable-vs-semaphore
- https://stackoverflow.com/questions/2332765/lock-mutex-semaphore-whats-the-difference
