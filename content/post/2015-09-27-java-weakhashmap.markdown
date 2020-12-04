---
categories:
- 编程语言
date: 2015-09-27 14:10:24
tags:
- Java
title: Java WeakHashMap 源码解析
---

前面把基于特定数据结构的Map介绍完了，它们分别利用了相应数据结构的特点来实现特殊的目的，像HashMap利用哈希表的快速插入、查找实现`O(1)`的增删改查，TreeMap则利用了红黑树来保证key的有序性的同时，使得增删改查的时间复杂度为`O(log(n))`。

今天要介绍的[WeakHashMap](http://docs.oracle.com/javase/7/docs/api/java/util/WeakHashMap.html)并没有基于某种特殊的数据结构，它的主要目的是为了优化JVM，使JVM中的垃圾回收器（garbage collector，后面简写为 GC）更智能的回收“无用”的对象。

> 本文源码分析基于[Oracle JDK 1.7.0_71](http://www.oracle.com/technetwork/java/javase/7u71-relnotes-2296187.html)，请知悉。

```
$ java -version
java version "1.7.0_71"
Java(TM) SE Runtime Environment (build 1.7.0_71-b14)
Java HotSpot(TM) 64-Bit Server VM (build 24.71-b01, mixed mode)
```

## 引用类型

`WeakHashMap`与其他 Map 最主要的不同之处在于其 key 是弱引用类型，其他 Map 的 key 均为强引用类型，说到这里，必须强调下：Java 中，引用有四种类型，分别为：强（strong）引用、软（soft）引用、弱（weak）引用、虚（phantom，本意为幽灵👻）引用。我相信对于 Java 初学者来说，不一定听过这几种引用类似，下面先介绍下这几种类型。

### 强引用

这是最常用的引用类型，在执行下面的语句时，变量 `o` 即为一个强引用。

```java
Object o = new Object();
```

> 强引用指向的对象无论在何时，都不会被GC 清理掉。

一般来说，对于常驻类应用（比如server），随着时间的增加，所占用的内存往往会持续上升，如果程序中全部使用强引用，那么很容易造成内存泄漏，最终导致`Out Of Memory (OOM)`，所以 Java 中提供了除强引用之外的其他三种引用，它们全部位于`java.lang.ref`包中，下面一一介绍。

### java.lang.ref.Reference

`java.lang.ref.Reference` 为 软（soft）引用、弱（weak）引用、虚（phantom）引用的父类。

<center>
    <img src="https://img.alicdn.com/imgextra/i4/581166664/TB2FuyqfFXXXXcjXpXXXXXXXXXX_!!581166664.png" alt="Reference类继承关系"/>
</center>

下面分析下`Reference`的源码（其他三种引用都是其子类，区分不是很大）。

#### 构造函数

```java
    //referent 为引用指向的对象
    Reference(T referent) {
        this(referent, null);
    }
    //ReferenceQueue对象，可以简单理解为一个队列
    //GC 在检测到appropriate reachability changes之后，
    //会把引用对象本身添加到这个queue中，便于清理引用对象本身
    Reference(T referent, ReferenceQueue<? super T> queue) {
        this.referent = referent;
        this.queue = (queue == null) ? ReferenceQueue.NULL : queue;
    }
```

如果我们在创建一个引用对象时，指定了`ReferenceQueue`，那么当引用对象指向的对象达到合适的状态（根据引用类型不同而不同）时，GC 会把引用对象本身添加到这个队列中，方便我们处理它，因为
> 引用对象指向的对象 GC 会自动清理，但是引用对象本身也是对象（是对象就占用一定资源），所以需要我们自己清理。

举个例子：

```java
Object o = new Object();
SoftReference<Object> sr = new SoftReference<>(o , queue);
```

`sr` 为软引用，指向 `o` 这个对象，`o` 会在一定时机被 GC 自动清理，但是 `sr` 对象本身的清理工作依赖于 `queue`，当 `sr` 出现在`queue`中时，说明其指向的对象已经无效，可以放心清理了。

从上面的分析大家应该对`Reference`类有了基本的认识，但是上面也提到了，不同的引用，添加到`ReferenceQueue`的时机是不一样。下面介绍具体引用时再进行说明。
这里有个问题，如果创建引用对象是没有指定`ReferenceQueue`，引用对象会怎么样呢？这里需要了解`Reference`类内部的四种状态。

#### 四种状态

每一时刻，`Reference`对象都处于下面四种状态中。这四种状态用`Reference`的成员变量`queue`与`next`（类似于单链表中的next）来标示。

```
ReferenceQueue<? super T> queue;
Reference next;
```

- Active。新创建的引用对象都是这个状态，在 GC 检测到引用对象已经到达合适的reachability时，GC 会根据引用对象是否在创建时制定`ReferenceQueue`参数进行状态转移，如果指定了，那么转移到`Pending`，如果没指定，转移到`Inactive`。在这个状态中

    ```
    //如果构造参数中没指定queue，那么queue为ReferenceQueue.NULL，否则为构造参数中传递过来的queue
    queue = ReferenceQueue || ReferenceQueue.NULL
    next = null
    ```

- Pending。pending-Reference列表中的引用都是这个状态，它们等着被内部线程`ReferenceHandler`处理（会调用`ReferenceQueue.enqueue`方法）。没有注册的实例不会进入这个状态。在这个状态中

    ```
    //构造参数参数中传递过来的queue
    queue = ReferenceQueue
    next = 该queue中的下一个引用，如果是该队列中的最后一个，那么为this
    ```

- Enqueued。调用`ReferenceQueue.enqueued`方法后的引用处于这个状态中。没有注册的实例不会进入这个状态。在这个状态中

    ```
    queue = ReferenceQueue.ENQUEUED
    next = 该queue中的下一个引用，如果是该队列中的最后一个，那么为this
    ```

- Inactive。最终状态，处于这个状态的引用对象，状态不会在改变。在这个状态中

    ```
    queue = ReferenceQueue.NULL
    next = this
    ```

有了这些约束，GC 只需要检测`next`字段就可以知道是否需要对该引用对象采取特殊处理
- 如果`next`为`null`，那么说明该引用为`Active`状态
- 如果`next`不为`null`，那么 GC 应该按其正常逻辑处理该引用。

我自己根据`Reference.ReferenceHandler.run`与`ReferenceQueue.enqueue`这两个方法，画出了这四种状态的转移图，供大家参考：
<center>
<img src="https://img.alicdn.com/imgextra/i2/581166664/TB2CCSNfFXXXXceXXXXXXXXXXXX_!!581166664.png" alt="Reference状态转移图"/>
</center>

要理解这个状态 GC 到底做了什么事，需要看 JVM 的代码，我这里时间、能力都不够，就不献丑了，后面有机会再来填坑。
对于一般程序员来说，这四种状态完全可以不用管。最后简单两句话总结上面的四种状态：
1. 如果构造函数中指定了`ReferenceQueue`，那么事后程序员可以通过该队列清理引用
2. 如果构造函数中没有指定了`ReferenceQueue`，那么 GC 会自动清理引用

#### get

调用`Reference.get`方法可以得到该引用指向的对象，但是由于指向的对象随时可能被 GC 清理，所以即使在同一个线程中，不同时刻的调用可能返回不一样的值。

### 软引用（soft reference）

软引用“保存”对象的能力稍逊于强引用，但是高于弱引用，一般用来实现memory-sensitive caches。
> 软引用指向的对象会在程序即将触发`OOM`时被GC 清理掉，之后，引用对象会被放到`ReferenceQueue`中。

### 弱引用（weak reference）

软引用“保存”对象的能力稍逊于弱引用，但是高于虚引用，一般用来实现canonicalizing mapping，也就是本文要讲的`WeakHashMap`😊。
> 当弱引用指向的对象只能通过弱引用（没有强引用或弱引用）访问时，GC会清理掉该对象，之后，引用对象会被放到`ReferenceQueue`中。

### 虚引用（phantom reference）

虚引用是“保存”对象能力最弱的引用，一般用来实现scheduling pre-mortem cleanup actions in a more flexible way than is possible with the Java finalization mechanism

> 调用虚引用的`get`方法，总会返回`null`，与软引用和弱引用不同的是，虚引用被`enqueued`时，GC 并不会自动清理虚引用指向的对象，只有当指向该对象的所有虚引用全部被清理（enqueued后）后或其本身不可达时，该对象才会被清理。

## WeakHashMap.Entry

上面介绍了很多引用的知识点，其实`WeakHashMap`本身没什么好说的，只要是把引用的作用与使用场景搞清楚了，再来分析基于这些引用的对象就会很简单了。
`WeakHashMap`与`HashMap`的签名与构造函数一样，这里就不介绍了，这里重点介绍下`Entry`这个内部对象，因为其保存具体key-value对，所以把它弄清楚了，其他的就问题不大了。

```java
   /**
     * The entries in this hash table extend WeakReference, using its main ref
     * field as the key.
     */
    private static class Entry<K,V> extends WeakReference<Object> implements Map.Entry<K,V> {
        V value;
        int hash;
        Entry<K,V> next;

        /**
         * Creates new entry.
         */
        Entry(Object key, V value,
              ReferenceQueue<Object> queue,
              int hash, Entry<K,V> next) {
            //这里把key传给了父类WeakReference，说明key为弱引用（没有显式的 this.key = key）
            //所有如果key只有通过弱引用访问时，key会被 GC 清理掉
            //同时该key所代表的Entry会进入queue中，等待被处理
            //还可以看到value为强引用（有显式的 this.value = value ），但这并不影响
            //后面可以看到WeakHashMap.expungeStaleEntries方法是如何清理value的
            super(key, queue);
            this.value = value;
            this.hash  = hash;
            this.next  = next;
        }

        @SuppressWarnings("unchecked")
        //在获取key时需要unmaskNull，因为对于null的key，是用WeakHashMap的内部成员属性来表示的
        public K getKey() {
            return (K) WeakHashMap.unmaskNull(get());
        }

        public V getValue() {
            return value;
        }

        public V setValue(V newValue) {
            V oldValue = value;
            value = newValue;
            return oldValue;
        }
        public boolean equals(Object o) {
            if (!(o instanceof Map.Entry))
                return false;
            Map.Entry<?,?> e = (Map.Entry<?,?>)o;
            K k1 = getKey();
            Object k2 = e.getKey();
            if (k1 == k2 || (k1 != null && k1.equals(k2))) {
                V v1 = getValue();
                Object v2 = e.getValue();
                if (v1 == v2 || (v1 != null && v1.equals(v2)))
                    return true;
            }
            return false;
        }

        public int hashCode() {
            K k = getKey();
            V v = getValue();
            return ((k==null ? 0 : k.hashCode()) ^
                    (v==null ? 0 : v.hashCode()));
        }

        public String toString() {
            return getKey() + "=" + getValue();
        }
    }

```

## WeakHashMap.expungeStaleEntries

```java
    /**
     * Reference queue for cleared WeakEntries
     */
    // 所有Entry在构造时都传入该queue
    private final ReferenceQueue<Object> queue = new ReferenceQueue<>();

    /**
     * Expunges stale entries from the table.
     */
    private void expungeStaleEntries() {
        for (Object x; (x = queue.poll()) != null; ) {
            synchronized (queue) {
                // e 为要清理的对象
                @SuppressWarnings("unchecked")
                    Entry<K,V> e = (Entry<K,V>) x;
                int i = indexFor(e.hash, table.length);

                Entry<K,V> prev = table[i];
                Entry<K,V> p = prev;
                // while 循环遍历冲突链
                while (p != null) {
                    Entry<K,V> next = p.next;
                    if (p == e) {
                        if (prev == e)
                            table[i] = next;
                        else
                            prev.next = next;
                        // Must not null out e.next;
                        // stale entries may be in use by a HashIterator
                        // 可以看到这里把value赋值为null，来帮助 GC 回收强引用的value
                        e.value = null; // Help GC
                        size--;
                        break;
                    }
                    prev = p;
                    p = next;
                }
            }
        }
    }
```

知道了`expungeStaleEntries`方法的作用，下面看看它是何时被调用的
<center>
    <img src="https://img.alicdn.com/imgextra/i4/581166664/TB2nMe3fFXXXXaFXXXXXXXXXXXX_!!581166664.png" alt="expungeStaleEntries调用链"/>
</center>

可以看到，在对`WeakHashMap`进行增删改查时，都调用了`expungeStaleEntries`方法。

## 实战

上面说了，下面来个具体的例子帮助大家消化

```java
import java.util.WeakHashMap;

class KeyHolder {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("I am over from key");
        super.finalize();
    }
}
class ValueHolder {
    @Override
    protected void finalize() throws Throwable {
        System.out.println("I am over from value");
        super.finalize();
    }
}

public class RefTest {
    public static void main(String[] args) {
        WeakHashMap<KeyHolder, ValueHolder> weakMap = new WeakHashMap<KeyHolder, ValueHolder>();

        KeyHolder kh = new KeyHolder();    
        ValueHolder vh = new ValueHolder();

        weakMap.put(kh, vh);

        while (true) {
            for (KeyHolder key : weakMap.keySet()) {
                System.out.println(key + " : " + weakMap.get(key));
            }
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("here...");
            //这里把kh设为null，这样一来就只有弱引用指向kh指向的对象
            kh = null;
            System.gc();
        }
    }
}

```
输出
```
KeyHolder@a15670a : ValueHolder@20e1ed5b
here...
I am over from key   //输出这句话说明，该key对应的Entry已经被 GC 清理
here...
here...
here...
...
...
...

```

## 总结

说实话，之前我是没怎么了解过引用，更是没有用过`WeakHashMap`这个类，这次算是把这个坑给填上了。引用的使用场景应该是在常驻类或消耗内存较大应用中才用得上，我自己确实没怎么经历过这种类型的项目，只能现在打好基础，以后有机会在尝试。

其实关于引用，本文重点介绍了弱引用的使用场景，其他的没怎么介绍，感兴趣的可以阅读参考中给出的链接。😊

## 参考

- https://weblogs.java.net/blog/2006/05/04/understanding-weak-references
- http://www.onjava.com/pub/a/onjava/2001/07/09/optimization.html?page=1
- [whats-the-state-of-a-weak-reference-that-has-been-manually-enqueued](http://stackoverflow.com/questions/5585694/whats-the-state-of-a-weak-reference-that-has-been-manually-enqueued)
