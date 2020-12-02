title: Java LinkedHashMap源码解析
date: 2015-09-12 18:31:12
categories: [编程语言]
tags: [Java]
---

上周把[HashMap](/blog/2015/09/03/java-hashmap/)、[TreeMap](/blog/2015/09/04/java-treemap/)这两个Map体系中比较有代表性的类介绍完了，大家应该也能体会到，如果该类所对应的数据结构与算法掌握好了，再看这些类的源码真是太简单不过了。

其次，我希望大家能够触类旁通，比如我们已经掌握了HashMap的原理，我们可以推知[HashSet](http://docs.oracle.com/javase/7/docs/api/java/util/HashSet.html)的内部实现

> HashSet 内部用一个HashMap对象存储数据，更具体些，只用到了key，value全部为一dummy对象。

HashSet这个类太简单了，我不打算单独写文章介绍。今天介绍个比较实用的类——[LinkedHashMap](http://docs.oracle.com/javase/7/docs/api/java/util/LinkedHashMap.html)。

> 本文源码分析基于[Oracle JDK 1.7.0_71](http://www.oracle.com/technetwork/java/javase/7u71-relnotes-2296187.html)，请知悉。
```
$ java -version
java version "1.7.0_71"
Java(TM) SE Runtime Environment (build 1.7.0_71-b14)
Java HotSpot(TM) 64-Bit Server VM (build 24.71-b01, mixed mode)
```

## 签名

```
public class LinkedHashMap<K,V>
       extends HashMap<K,V>
       implements Map<K,V>
```
可以看到，LinkedHashMap是HashMap的一子类，它根据自身的特性修改了HashMap的内部某些方法的实现，要想知道LinkedHashMap具体修改了哪些方法，就需要了解LinkedHashMap的设计原理了。

## 设计原理

### 双向链表

LinkedHashMap是key键有序的HashMap的一种实现。它除了使用哈希表这个数据结构，使用双向链表来保证key的顺序
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2WFoafXXXXXaUXXXXXXXXXXXX_!!581166664.gif" alt="双向链表">
</center>
双向链表算是个很常见的数据结构，上图中的头节点的prev、尾节点的next指向null，双向链表还有一种变种，见下图
<center>
<img src="https://img.alicdn.com/imgextra/i1/581166664/TB27MP7fXXXXXb6XXXXXXXXXXXX_!!581166664.png" alt="环型双向链表">
</center>
可以看到，这种链表把首尾节点相连，形成一个环。

LinkedHashMap中采用的这种`环型双向链表`，环型双向链表的用途比较多，感兴趣可以看这里：

- http://stackoverflow.com/questions/3589772/why-exactly-do-we-need-a-circular-linked-list-singly-or-doubly-data-structur

双向链表这种数据结构，最关键的是保证在增加节点、删除节点时不要断链，后面在分析LinkedHashMap具体代码时会具体介绍，这里就不赘述了。


### LinkedHashMap 特点

一般来说，如果需要使用的Map中的key无序，选择HashMap；如果要求key有序，则选择TreeMap。
但是选择TreeMap就会有性能问题，因为TreeMap的get操作的时间复杂度是`O(log(n))`的，相比于HashMap的`O(1)`还是差不少的，LinkedHashMap的出现就是为了平衡这些因素，使得
> 能够以`O(1)`时间复杂度增加查找元素，又能够保证key的有序性

此外，LinkedHashMap提供了两种key的顺序：
- 访问顺序（access order）。非常实用，可以使用这种顺序实现LRU（Least Recently Used）缓存
- 插入顺序（insertion orde）。同一key的多次插入，并不会影响其顺序

## 源码分析

首先打开eclipse的outline面版看看LinkedHashMap里面有那些成员
<center>
    <img src="https://img.alicdn.com/imgextra/i1/581166664/TB25aL6fXXXXXcGXXXXXXXXXXXX_!!581166664.png" alt="LinkedHashMap结构" />
</center>
可以看到，由于LinkedHashMap继承自HashMap，所以大部分的方法都是根据`key的有序性`而重写了HashMap中的部分方法。

### 构造函数

```java
    //accessOrder为true表示该LinkedHashMap的key为访问顺序
    //accessOrder为false表示该LinkedHashMap的key为插入顺序
    private final boolean accessOrder;

    public LinkedHashMap(int initialCapacity, float loadFactor) {
        super(initialCapacity, loadFactor);
        //默认为false，也就是插入顺序
        accessOrder = false;
    }
    public LinkedHashMap(int initialCapacity) {
        super(initialCapacity);
        accessOrder = false;
    }
    public LinkedHashMap() {
        super();
        accessOrder = false;
    }
    public LinkedHashMap(Map<? extends K, ? extends V> m) {
        super(m);
        accessOrder = false;
    }
    public LinkedHashMap(int initialCapacity,
                         float loadFactor,
                         boolean accessOrder) {
        super(initialCapacity, loadFactor);
        this.accessOrder = accessOrder;
    }

    /**
     * Called by superclass constructors and pseudoconstructors (clone,
     * readObject) before any entries are inserted into the map.  Initializes
     * the chain.
     */
    @Override
    void init() {
        header = new Entry<>(-1, null, null, null);
        //通过这里可以看出，LinkedHashMap采用的是环型的双向链表
        header.before = header.after = header;
    }

```

### LinkedHashMap.Entry

```java
    private static class Entry<K,V> extends HashMap.Entry<K,V> {
        // These fields comprise the doubly linked list used for iteration.
        //每个节点包含两个指针，指向前继节点与后继节点
        Entry<K,V> before, after;

        Entry(int hash, K key, V value, HashMap.Entry<K,V> next) {
            super(hash, key, value, next);
        }

        /**
         * Removes this entry from the linked list.
         */
        //删除一个节点时，需要把
        //1. 前继节点的后继指针 指向 要删除节点的后继节点
        //2. 后继节点的前继指针 指向 要删除节点的前继节点
        private void remove() {
            before.after = after;
            after.before = before;
        }

        /**
         * Inserts this entry before the specified existing entry in the list.
         */
        //在某节点前插入节点
        private void addBefore(Entry<K,V> existingEntry) {
            after  = existingEntry;
            before = existingEntry.before;
            before.after = this;
            after.before = this;
        }

        /**
         * This method is invoked by the superclass whenever the value
         * of a pre-existing entry is read by Map.get or modified by Map.set.
         * If the enclosing Map is access-ordered, it moves the entry
         * to the end of the list; otherwise, it does nothing.
         */
        void recordAccess(HashMap<K,V> m) {
            LinkedHashMap<K,V> lm = (LinkedHashMap<K,V>)m;
            // 如果需要key的访问顺序，需要把
            // 当前访问的节点删除，并把它插入到双向链表的起始位置
            if (lm.accessOrder) {
                lm.modCount++;
                remove();
                addBefore(lm.header);
            }
        }

        void recordRemoval(HashMap<K,V> m) {
            remove();
        }
    }

```
为了更形象表示双向链表是如何删除、增加节点，下面用代码加图示的方式

#### 删除节点

<center>
    <img src="https://img.alicdn.com/imgextra/i4/581166664/TB2cA__fXXXXXbQXXXXXXXXXXXX_!!581166664.jpg" alt="删除节点">
</center>
上图中，删除的是b节点
```
    private void remove() {
        before.after = after;  //相当于上图中的操作 1
        after.before = before; //相当于上图中的操作 3
    }
```
#### 增加节点

<center>
    <img src="https://img.alicdn.com/imgextra/i2/581166664/TB2lqv0fXXXXXaeXpXXXXXXXXXX_!!581166664.jpg" alt="增加节点">
</center>
上图中的c节点相当于下面代码中的existingEntry，要插入的是x节点

```java
    private void addBefore(Entry<K,V> existingEntry) {
        after  = existingEntry;         //相当于上图中的操作 1
        before = existingEntry.before;  //相当于上图中的操作 3
        before.after = this;            //相当于上图中的操作 4
        after.before = this;            //相当于上图中的操作 2
    }
```

知道了增加节点的原理，下面看看LinkedHashMap的代码是怎么实现put方法的

```java
    /**
     * This override alters behavior of superclass put method. It causes newly
     * allocated entry to get inserted at the end of the linked list and
     * removes the eldest entry if appropriate.
     */
    void addEntry(int hash, K key, V value, int bucketIndex) {
        super.addEntry(hash, key, value, bucketIndex);

        // Remove eldest entry if instructed
        Entry<K,V> eldest = header.after;
        //如果有必要移除最老的节点，那么就移除。LinkedHashMap默认removeEldestEntry总是返回false
        //也就是这里if里面的语句永远不会执行
        //这里removeEldestEntry主要是给LinkedHashMap的子类留下的一个钩子
        //子类完全可以根据自己的需要重写removeEldestEntry，后面我会举个现实中的例子🌰
        if (removeEldestEntry(eldest)) {
            removeEntryForKey(eldest.key);
        }
    }
    /**
     * This override differs from addEntry in that it doesn't resize the
     * table or remove the eldest entry.
     */
    void createEntry(int hash, K key, V value, int bucketIndex) {
        HashMap.Entry<K,V> old = table[bucketIndex];
        Entry<K,V> e = new Entry<>(hash, key, value, old);
        table[bucketIndex] = e;
        //这里把新增的Entry加到了双向链表的header的前面，成为新的header
        e.addBefore(header);
        size++;
    }   
    /**
     * Returns <tt>true</tt> if this map should remove its eldest entry.
     * This method is invoked by <tt>put</tt> and <tt>putAll</tt> after
     * inserting a new entry into the map.  It provides the implementor
     * with the opportunity to remove the eldest entry each time a new one
     * is added.  This is useful if the map represents a cache: it allows
     * the map to reduce memory consumption by deleting stale entries.
     *
     * <p>Sample use: this override will allow the map to grow up to 100
     * entries and then delete the eldest entry each time a new entry is
     * added, maintaining a steady state of 100 entries.
     * <pre>
     *     private static final int MAX_ENTRIES = 100;
     *
     *     protected boolean removeEldestEntry(Map.Entry eldest) {
     *        return size() > MAX_ENTRIES;
     *     }
     * </pre>
     *
     * <p>This method typically does not modify the map in any way,
     * instead allowing the map to modify itself as directed by its
     * return value.  It <i>is</i> permitted for this method to modify
     * the map directly, but if it does so, it <i>must</i> return
     * <tt>false</tt> (indicating that the map should not attempt any
     * further modification).  The effects of returning <tt>true</tt>
     * after modifying the map from within this method are unspecified.
     *
     * <p>This implementation merely returns <tt>false</tt> (so that this
     * map acts like a normal map - the eldest element is never removed).
     *
     * @param    eldest The least recently inserted entry in the map, or if
     *           this is an access-ordered map, the least recently accessed
     *           entry.  This is the entry that will be removed it this
     *           method returns <tt>true</tt>.  If the map was empty prior
     *           to the <tt>put</tt> or <tt>putAll</tt> invocation resulting
     *           in this invocation, this will be the entry that was just
     *           inserted; in other words, if the map contains a single
     *           entry, the eldest entry is also the newest.
     * @return   <tt>true</tt> if the eldest entry should be removed
     *           from the map; <tt>false</tt> if it should be retained.
     */
    protected boolean removeEldestEntry(Map.Entry<K,V> eldest) {
        return false;
    }
```

上面是LinkedHashMap中重写了HashMap的两个方法，当调用put时添加Entry（新增Entry之前不存在）整个方法调用链是这样的：

> `LinkedHashMap.put` -> `LinkedHashMap.addEntry` ->
> `HashMap.addEntry` -> `LinkedHashMap.createEntry`

有了这个调用链，再结合上面createEntry方法中的注释，就可以明白如何在添加Entry保证双向链表不断链的了。

#### 实战：LRU缓存

上面已经介绍了，利用访问顺序这种方式可以实现LRU缓存，正好最近在用flume向hadoop传数据，发现里面hdfs sink里面就用到了这种思想。

如果你不了解flume、hdfs、sink等这些概念，也不要紧，也不会影响阅读下面的代码，相信我😊。

```java
  /*
   * Extended Java LinkedHashMap for open file handle LRU queue.
   * We want to clear the oldest file handle if there are too many open ones.
   */
  private static class WriterLinkedHashMap
      extends LinkedHashMap<String, BucketWriter> {

    private final int maxOpenFiles;

    public WriterLinkedHashMap(int maxOpenFiles) {
      //这里的第三个参数为true，表示key默认的顺序为访问顺序，而不是插入顺序
      super(16, 0.75f, true); // stock initial capacity/load, access ordering
      this.maxOpenFiles = maxOpenFiles;
    }

    @Override
    protected boolean removeEldestEntry(Entry<String, BucketWriter> eldest) {
      if (size() > maxOpenFiles) {
        // If we have more that max open files, then close the last one and
        // return true
        try {
          eldest.getValue().close();
        } catch (IOException e) {
          LOG.warn(eldest.getKey().toString(), e);
        } catch (InterruptedException e) {
          LOG.warn(eldest.getKey().toString(), e);
          Thread.currentThread().interrupt();
        }
        return true;
      } else {
        return false;
      }
    }
  }
```

可以看到，这里的`WriterLinkedHashMap`主要是重写了removeEldestEntry方法，我们上面介绍了，在LinkedHashMap中，这个方法总是返回false，在这里设定了一个阈值maxOpenFiles，如果打开的文件数超过了这个阈值，就返回true，即把之前最不经常访问的节点给删除掉，达到释放资源的效果。

### 更高效的LinkedHashIterator

由于元素之间用双向链表连接起来了，所以在遍历元素时只需遍历双向链表即可，这比HashMap中的遍历方式要高效。

```java
    private abstract class LinkedHashIterator<T> implements Iterator<T> {
        Entry<K,V> nextEntry    = header.after;
        Entry<K,V> lastReturned = null;

        /**
         * The modCount value that the iterator believes that the backing
         * List should have.  If this expectation is violated, the iterator
         * has detected concurrent modification.
         */
        int expectedModCount = modCount;
        //由于采用环型双向链表，所以可以用header.after == header 来判断双向链表是否为空
        public boolean hasNext() {
            return nextEntry != header;
        }

        public void remove() {
            if (lastReturned == null)
                throw new IllegalStateException();
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();

            LinkedHashMap.this.remove(lastReturned.key);
            lastReturned = null;
            expectedModCount = modCount;
        }

        Entry<K,V> nextEntry() {
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            if (nextEntry == header)
                throw new NoSuchElementException();
            Entry<K,V> e = lastReturned = nextEntry;
            //在访问下一个节点时，直接使用当前节点的后继指针即可
            nextEntry = e.after;
            return e;
        }
    }
```
除了LinkedHashIterator利用了双向链表遍历的优势外，下面的两个方法也利用这个优势加速执行。

```java
    /**
     * Transfers all entries to new table array.  This method is called
     * by superclass resize.  It is overridden for performance, as it is
     * faster to iterate using our linked list.
     */
    @Override
    void transfer(HashMap.Entry[] newTable, boolean rehash) {
        int newCapacity = newTable.length;
        for (Entry<K,V> e = header.after; e != header; e = e.after) {
            if (rehash)
                e.hash = (e.key == null) ? 0 : hash(e.key);
            int index = indexFor(e.hash, newCapacity);
            e.next = newTable[index];
            newTable[index] = e;
        }
    }


    /**
     * Returns <tt>true</tt> if this map maps one or more keys to the
     * specified value.
     *
     * @param value value whose presence in this map is to be tested
     * @return <tt>true</tt> if this map maps one or more keys to the
     *         specified value
     */
    public boolean containsValue(Object value) {
        // Overridden to take advantage of faster iterator
        if (value==null) {
            for (Entry e = header.after; e != header; e = e.after)
                if (e.value==null)
                    return true;
        } else {
            for (Entry e = header.after; e != header; e = e.after)
                if (value.equals(e.value))
                    return true;
        }
        return false;
    }
```

## 总结

通过这次分析LinkedHashMap，我发现JDK里面的类设计确实巧妙，父类中很多为空的方法，看似无用，其实是为子类留的一个钩子，子类可以根据需要重写这个方法，像LinkedHashMap就重写了`init`方法，这个方法在HashMap中的实现为空。

其次我还想强调下一些基础数据结构与算法的重要性，语言现在很多，火的也多，我们不可能一一去学习，语法说白了就是一系列规则（也可以说是语法糖衣），不同的语言创建者所定的规则可能千差万别，但是他们所基于的数据结构与算法肯定是统一的。去伪存真，算法与数据结构才是我们真正需要学习的。

最近在看[Y_combinator](https://en.wikipedia.org/wiki/Fixed-point_combinator#Fixed_point_combinators_in_lambda_calculus)，函数式编程中最迷人的地方，希望自己完全理解后再与大家分享。Stay Tuned！
