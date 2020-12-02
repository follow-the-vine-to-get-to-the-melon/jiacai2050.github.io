title: Java HashMap 源码解析
date: 2015-09-03 11:51:12
categories: 编程语言
tags: [Java]
---

继上一篇文章[Java集合框架综述](/blog/2015/09/01/java-collection-overview)后，今天正式开始分析具体集合类的代码，首先以既熟悉又陌生的[HashMap](http://docs.oracle.com/javase/7/docs/api/index.html?java/util/HashMap.html)开始。

> 本文源码分析基于[Oracle JDK 1.7.0_71](http://www.oracle.com/technetwork/java/javase/7u71-relnotes-2296187.html)，请知悉。
```
$ java -version
java version "1.7.0_71"
Java(TM) SE Runtime Environment (build 1.7.0_71-b14)
Java HotSpot(TM) 64-Bit Server VM (build 24.71-b01, mixed mode)
```

## 签名（signature）

```
public class HashMap<K,V>
       extends AbstractMap<K,V>
       implements Map<K,V>, Cloneable, Serializable
```
可以看到`HashMap`继承了

- 标记接口[Cloneable](http://docs.oracle.com/javase/7/docs/api/index.html?java/lang/Cloneable.html)，用于表明`HashMap`对象会重写`java.lang.Object#clone()`方法，HashMap实现的是浅拷贝（shallow copy）。
- 标记接口[Serializable](http://docs.oracle.com/javase/7/docs/api/index.html?java/io/Serializable.html)，用于表明`HashMap`对象可以被序列化

比较有意思的是，`HashMap`同时继承了抽象类`AbstractMap`与接口`Map`，因为抽象类`AbstractMap`的签名为
```
public abstract class AbstractMap<K,V> implements Map<K,V>
```
[Stack Overfloooow](http://stackoverflow.com/questions/14062286/java-why-does-weakhashmap-implement-map-whereas-it-is-already-implemented-by-ab)上解释到：

> 在语法层面继承接口`Map`是多余的，这么做仅仅是为了让阅读代码的人明确知道`HashMap`是属于`Map`体系的，起到了文档的作用

`AbstractMap`相当于个辅助类，`Map`的一些操作这里面已经提供了默认实现，后面具体的子类如果没有特殊行为，可直接使用`AbstractMap`提供的实现。

### [Cloneable](http://docs.oracle.com/javase/7/docs/api/index.html?java/lang/Cloneable.html)接口

    It's evil, don't use it.

`Cloneable`这个接口设计的非常不好，最致命的一点是它里面竟然没有`clone`方法，也就是说我们自己写的类完全可以实现这个接口的同时不重写`clone`方法。

关于`Cloneable`的不足，大家可以去看看《Effective Java》一书的作者[给出的理由](http://www.artima.com/intv/bloch13.html)，在所给链接的文章里，Josh Bloch也会讲如何实现深拷贝比较好，我这里就不在赘述了。

### [Map](http://docs.oracle.com/javase/7/docs/api/index.html?java/util/Map.html)接口

在eclipse中的outline面板可以看到`Map`接口里面包含以下成员方法与内部类：
<center>
<img src="https://img.alicdn.com/imgextra/i1/581166664/TB2Pt6LeVXXXXboXpXXXXXXXXXX_!!581166664.png" width="400" height="400" alt="Map_field_method">
</center>

可以看到，这里的成员方法不外乎是“增删改查”，这也反映了我们编写程序时，一定是以“数据”为导向的。

在[上篇文章](/blog/2015/09/01/java-collection-overview/#Map)讲了`Map`虽然并不是`Collection`，但是它提供了三种“集合视角”（collection views），与下面三个方法一一对应：
- `Set<K> keySet()`，提供key的集合视角
- `Collection<V> values()`，提供value的集合视角
- `Set<Map.Entry<K, V>> entrySet()`，提供key-value序对的集合视角，这里用内部类`Map.Entry`表示序对

### [AbstractMap](http://docs.oracle.com/javase/7/docs/api/index.html?java/util/AbstractMap.html)抽象类

`AbstractMap`对`Map`中的方法提供了一个基本实现，减少了实现`Map`接口的工作量。
举例来说：
> 如果要实现个不可变（unmodifiable）的map，那么只需继承`AbstractMap`，然后实现其`entrySet`方法，这个方法返回的set不支持add与remove，同时这个set的迭代器（iterator）不支持remove操作即可。
>
> 相反，如果要实现个可变（modifiable）的map，首先继承`AbstractMap`，然后重写（override）`AbstractMap`的put方法，同时实现`entrySet`所返回set的迭代器的remove方法即可。

## 设计理念（design concept）

### 哈希表（hash table）
`HashMap`是一种基于[哈希表（hash table）](https://en.wikipedia.org/wiki/Hash_table)实现的map，哈希表（也叫关联数组）一种通用的数据结构，大多数的现代语言都原生支持，其概念也比较简单：`key经过hash函数作用后得到一个槽（buckets或slots）的索引（index），槽中保存着我们想要获取的值`，如下图所示
<center>
<img src="https://img.alicdn.com/imgextra/i2/581166664/TB2ZGZbeVXXXXXtXXXXXXXXXXXX_!!581166664.png" alt="hash table demo" width="300" height="300">
</center>

很容易想到，一些不同的key经过同一hash函数后可能产生相同的索引，也就是产生了冲突，这是在所难免的。
所以利用哈希表这种数据结构实现具体类时，需要：
- 设计个好的hash函数，使冲突尽可能的减少
- 其次是需要解决发生冲突后如何处理。

后面会重点介绍`HashMap`是如何解决这两个问题的。

### HashMap的一些特点

- 线程非安全，并且允许key与value都为null值，`HashTable`与之相反，为线程安全，key与value都不允许null值。
- 不保证其内部元素的顺序，而且随着时间的推移，同一元素的位置也可能改变（resize的情况）
- put、get操作的时间复杂度为O(1)。
- 遍历其集合视角的时间复杂度与其容量（capacity，槽的个数）和现有元素的大小（entry的个数）成正比，所以如果遍历的性能要求很高，不要把capactiy设置的过高或把平衡因子（load factor，当entry数大于capacity*loadFactor时，会进行resize，reside会导致key进行rehash）设置的过低。
- 由于HashMap是线程非安全的，这也就是意味着如果多个线程同时对一hashmap的集合试图做迭代时有结构的上改变（添加、删除entry，只改变entry的value的值不算结构改变），那么会报[ConcurrentModificationException](http://docs.oracle.com/javase/7/docs/api/java/util/ConcurrentModificationException.html)，专业术语叫`fail-fast`，尽早报错对于多线程程序来说是很有必要的。
- `Map m = Collections.synchronizedMap(new HashMap(...));` 通过这种方式可以得到一个线程安全的map。

## 源码剖析

首先从构造函数开始讲，`HashMap`遵循[集合框架的约束](/blog/2015/09/01/java-collection-overview/#两大基类Collection与Map)，提供了一个参数为空的构造函数与有一个参数且参数类型为Map的构造函数。除此之外，还提供了两个构造函数，用于设置`HashMap`的容量（capacity）与平衡因子（loadFactor）。

```java
    public HashMap(int initialCapacity, float loadFactor) {
        if (initialCapacity < 0)
            throw new IllegalArgumentException("Illegal initial capacity: " +
                                               initialCapacity);
        if (initialCapacity > MAXIMUM_CAPACITY)
            initialCapacity = MAXIMUM_CAPACITY;
        if (loadFactor <= 0 || Float.isNaN(loadFactor))
            throw new IllegalArgumentException("Illegal load factor: " +
                                               loadFactor);

        this.loadFactor = loadFactor;
        threshold = initialCapacity;
        init();
    }
    public HashMap(int initialCapacity) {
        this(initialCapacity, DEFAULT_LOAD_FACTOR);
    }
    public HashMap() {
        this(DEFAULT_INITIAL_CAPACITY, DEFAULT_LOAD_FACTOR);
    }
```

从代码上可以看到，容量与平衡因子都有个默认值，并且容量有个最大值

```java
    /**
     * The default initial capacity - MUST be a power of two.
     */
    static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; // aka 16

    /**
     * The maximum capacity, used if a higher value is implicitly specified
     * by either of the constructors with arguments.
     * MUST be a power of two <= 1<<30.
     */
    static final int MAXIMUM_CAPACITY = 1 << 30;

    /**
     * The load factor used when none specified in constructor.
     */
    static final float DEFAULT_LOAD_FACTOR = 0.75f;
```

可以看到，默认的平衡因子为0.75，这是权衡了时间复杂度与空间复杂度之后的最好取值（JDK说是最好的😂），过高的因子会降低存储空间但是查找（lookup，包括HashMap中的put与get方法）的时间就会增加。

这里比较奇怪的是问题：容量必须为2的指数倍（默认为16），这是为什么呢？解答这个问题，需要了解HashMap中哈希函数的设计原理。

### 哈希函数的设计原理

```java
   /**
     * Retrieve object hash code and applies a supplemental hash function to the
     * result hash, which defends against poor quality hash functions.  This is
     * critical because HashMap uses power-of-two length hash tables, that
     * otherwise encounter collisions for hashCodes that do not differ
     * in lower bits. Note: Null keys always map to hash 0, thus index 0.
     */
    final int hash(Object k) {
        int h = hashSeed;
        if (0 != h && k instanceof String) {
            return sun.misc.Hashing.stringHash32((String) k);
        }

        h ^= k.hashCode();

        // This function ensures that hashCodes that differ only by
        // constant multiples at each bit position have a bounded
        // number of collisions (approximately 8 at default load factor).
        h ^= (h >>> 20) ^ (h >>> 12);
        return h ^ (h >>> 7) ^ (h >>> 4);
    }

    /**
     * Returns index for hash code h.
     */
    static int indexFor(int h, int length) {
        // assert Integer.bitCount(length) == 1 : "length must be a non-zero power of 2";
        return h & (length-1);
    }
```

看到这么多位操作，是不是觉得晕头转向了呢，还是搞清楚原理就行了，毕竟位操作速度是很快的，不能因为不好理解就不用了😊。
网上说这个问题的也比较多，我这里根据自己的理解，尽量做到通俗易懂。

在哈希表容量（也就是buckets或slots大小）为length的情况下，为了使每个key都能在冲突最小的情况下映射到`[0,length)`（注意是左闭右开区间）的索引（index）内，一般有两种做法：
1. 让length为素数，然后用`hashCode(key) mod length`的方法得到索引
2. 让length为2的指数倍，然后用`hashCode(key) & (length-1)`的方法得到索引

[HashTable](http://docs.oracle.com/javase/7/docs/api/index.html?java/util/Hashtable.html)用的是方法1，`HashMap`用的是方法2。

因为本篇主题讲的是HashMap，所以关于方法1为什么要用素数，我这里不想过多介绍，大家可以看[这里](http://math.stackexchange.com/questions/183909/why-choose-a-prime-number-as-the-number-of-slots-for-hashing-function-that-uses)。

重点说说方法2的情况，方法2其实也比较好理解：
> 因为length为2的指数倍，所以`length-1`所对应的二进制位都为1，然后在与`hashCode(key)`做与运算，即可得到`[0,length)`内的索引

但是这里有个问题，如果`hashCode(key)`的大于`length`的值，而且`hashCode(key)`的二进制位的低位变化不大，那么冲突就会很多，举个例子：

> Java中对象的哈希值都32位整数，而HashMap默认大小为16，那么有两个对象那么的哈希值分别为：`0xABAB0000`与`0xBABA0000`，它们的后几位都是一样，那么与16异或后得到结果应该也是一样的，也就是产生了冲突。

造成冲突的原因关键在于16限制了只能用低位来计算，高位直接舍弃了，所以我们需要额外的哈希函数而不只是简单的对象的`hashCode`方法了。
具体来说，就是HashMap中`hash`函数干的事了
> 首先有个随机的hashSeed，来降低冲突发生的几率
>
> 然后如果是字符串，用了`sun.misc.Hashing.stringHash32((String) k);`来获取索引值
>
> 最后，通过一系列无符号右移操作，来把高位与低位进行异或操作，来降低冲突发生的几率

右移的偏移量20，12，7，4是怎么来的呢？因为Java中对象的哈希值都是32位的，所以这几个数应该就是把高位与低位做异或运算，至于这几个数是如何选取的，就不清楚了，网上搜了半天也没统一且让人信服的说法，大家可以参考下面几个链接：

- http://stackoverflow.com/questions/7922019/openjdks-rehashing-mechanism/7922219#7922219
- http://stackoverflow.com/questions/9335169/understanding-strange-java-hash-function/9336103#9336103
- http://stackoverflow.com/questions/14453163/can-anybody-explain-how-java-design-hashmaps-hash-function/14479945#14479945

### HashMap.Entry

HashMap中存放的是HashMap.Entry对象，它继承自Map.Entry，其比较重要的是构造函数

```java
    static class Entry<K,V> implements Map.Entry<K,V> {
        final K key;
        V value;
        Entry<K,V> next;
        int hash;

        Entry(int h, K k, V v, Entry<K,V> n) {
            value = v;
            next = n;
            key = k;
            hash = h;
        }
        // setter, getter, equals, toString 方法省略
        public final int hashCode() {
            //用key的hash值与上value的hash值作为Entry的hash值
            return Objects.hashCode(getKey()) ^ Objects.hashCode(getValue());
        }
        /**
         * This method is invoked whenever the value in an entry is
         * overwritten by an invocation of put(k,v) for a key k that's already
         * in the HashMap.
         */
        void recordAccess(HashMap<K,V> m) {
        }

        /**
         * This method is invoked whenever the entry is
         * removed from the table.
         */
        void recordRemoval(HashMap<K,V> m) {
        }
    }
```
可以看到，Entry实现了单向链表的功能，用`next`成员变量来级连起来。

介绍完Entry对象，下面要说一个比较重要的成员变量
```    
    /**
     * The table, resized as necessary. Length MUST Always be a power of two.
     */
    //HashMap内部维护了一个为数组类型的Entry变量table，用来保存添加进来的Entry对象
    transient Entry<K,V>[] table = (Entry<K,V>[]) EMPTY_TABLE;
```
你也许会疑问，Entry不是单向链表嘛，怎么这里又需要个数组类型的table呢？
我翻了下之前的算法书，其实这是解决冲突的一个方式：[链地址法（开散列法）](https://en.wikipedia.org/wiki/Hash_table#Separate_chaining)，效果如下：
<center>
<img src="https://img.alicdn.com/imgextra/i2/581166664/TB2rlT0eVXXXXazXpXXXXXXXXXX_!!581166664.gif" alt="链地址法处理冲突得到的散列表">
</center>
就是相同索引值的Entry，会以单向链表的形式存在

#### 链地址法的可视化

网上找到个很好的网站，用来可视化各种常见的算法，很棒。瞬间觉得国外大学比国内的强不知多少倍。
下面的链接可以模仿哈希表采用链地址法解决冲突，大家可以自己去玩玩😊
- https://www.cs.usfca.edu/~galles/visualization/OpenHash.html

### get操作

get操作相比put操作简单，所以先介绍get操作

```java
    public V get(Object key) {
        //单独处理key为null的情况
        if (key == null)
            return getForNullKey();
        Entry<K,V> entry = getEntry(key);

        return null == entry ? null : entry.getValue();
    }
    private V getForNullKey() {
        if (size == 0) {
            return null;
        }
        //key为null的Entry用于放在table[0]中，但是在table[0]冲突链中的Entry的key不一定为null
        //所以需要遍历冲突链，查找key是否存在
        for (Entry<K,V> e = table[0]; e != null; e = e.next) {
            if (e.key == null)
                return e.value;
        }
        return null;
    }
    final Entry<K,V> getEntry(Object key) {
        if (size == 0) {
            return null;
        }

        int hash = (key == null) ? 0 : hash(key);
        //首先定位到索引在table中的位置
        //然后遍历冲突链，查找key是否存在
        for (Entry<K,V> e = table[indexFor(hash, table.length)];
             e != null;
             e = e.next) {
            Object k;
            if (e.hash == hash &&
                ((k = e.key) == key || (key != null && key.equals(k))))
                return e;
        }
        return null;
    }
```

### put操作（含update操作）
因为put操作有可能需要对HashMap进行resize，所以实现略复杂些

```java
    private void inflateTable(int toSize) {
        //辅助函数，用于填充HashMap到指定的capacity
        // Find a power of 2 >= toSize
        int capacity = roundUpToPowerOf2(toSize);
        //threshold为resize的阈值，超过后HashMap会进行resize，内容的entry会进行rehash
        threshold = (int) Math.min(capacity * loadFactor, MAXIMUM_CAPACITY + 1);
        table = new Entry[capacity];
        initHashSeedAsNeeded(capacity);
    }
    /**
     * Associates the specified value with the specified key in this map.
     * If the map previously contained a mapping for the key, the old
     * value is replaced.
     */
    public V put(K key, V value) {
        if (table == EMPTY_TABLE) {
            inflateTable(threshold);
        }
        if (key == null)
            return putForNullKey(value);
        int hash = hash(key);
        int i = indexFor(hash, table.length);
        //这里的循环是关键
        //当新增的key所对应的索引i，对应table[i]中已经有值时，进入循环体
        for (Entry<K,V> e = table[i]; e != null; e = e.next) {
            Object k;
            //判断是否存在本次插入的key，如果存在用本次的value替换之前oldValue，相当于update操作
            //并返回之前的oldValue
            if (e.hash == hash && ((k = e.key) == key || key.equals(k))) {
                V oldValue = e.value;
                e.value = value;
                e.recordAccess(this);
                return oldValue;
            }
        }
        //如果本次新增key之前不存在于HashMap中，modCount加1，说明结构改变了
        modCount++;
        addEntry(hash, key, value, i);
        return null;
    }
    void addEntry(int hash, K key, V value, int bucketIndex) {
        //如果增加一个元素会后，HashMap的大小超过阈值，需要resize
        if ((size >= threshold) && (null != table[bucketIndex])) {
            //增加的幅度是之前的1倍
            resize(2 * table.length);
            hash = (null != key) ? hash(key) : 0;
            bucketIndex = indexFor(hash, table.length);
        }

        createEntry(hash, key, value, bucketIndex);
    }
    void createEntry(int hash, K key, V value, int bucketIndex) {
        //首先得到该索引处的冲突链Entries，第一次插入bucketIndex位置时冲突链为null，也就是e为null
        Entry<K,V> e = table[bucketIndex];
        //然后把新的Entry添加到冲突链的开头，也就是说，后插入的反而在前面（第一次还真没看明白）
        //table[bucketIndex]为新加入的Entry，是bucketIndex位置的冲突链的第一个元素
        table[bucketIndex] = new Entry<>(hash, key, value, e);
        size++;
    }
    //下面看看HashMap是如何进行resize，庐山真面目就要揭晓了😊
    void resize(int newCapacity) {
        Entry[] oldTable = table;
        int oldCapacity = oldTable.length;
        //如果已经达到最大容量，那么就直接返回
        if (oldCapacity == MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return;
        }

        Entry[] newTable = new Entry[newCapacity];
        //initHashSeedAsNeeded(newCapacity)的返回值决定了是否需要重新计算Entry的hash值
        transfer(newTable, initHashSeedAsNeeded(newCapacity));
        table = newTable;
        threshold = (int)Math.min(newCapacity * loadFactor, MAXIMUM_CAPACITY + 1);
    }

    /**
     * Transfers all entries from current table to newTable.
     */
    void transfer(Entry[] newTable, boolean rehash) {
        int newCapacity = newTable.length;
        //遍历当前的table，将里面的元素添加到新的newTable中
        for (Entry<K,V> e : table) {
            while(null != e) {
                Entry<K,V> next = e.next;
                if (rehash) {
                    e.hash = null == e.key ? 0 : hash(e.key);
                }
                int i = indexFor(e.hash, newCapacity);
                e.next = newTable[i];
                //最后这两句用了与put放过相同的技巧
                //将后插入的反而在前面
                newTable[i] = e;
                e = next;
            }
        }
    }
    /**
     * Initialize the hashing mask value. We defer initialization until we
     * really need it.
     */
    final boolean initHashSeedAsNeeded(int capacity) {
        boolean currentAltHashing = hashSeed != 0;
        boolean useAltHashing = sun.misc.VM.isBooted() &&
                (capacity >= Holder.ALTERNATIVE_HASHING_THRESHOLD);
        //这里说明了，在hashSeed不为0或满足useAltHash时，会重算Entry的hash值
        //至于useAltHashing的作用可以参考下面的链接
        // http://stackoverflow.com/questions/29918624/what-is-the-use-of-holder-class-in-hashmap
        boolean switching = currentAltHashing ^ useAltHashing;
        if (switching) {
            hashSeed = useAltHashing
                ? sun.misc.Hashing.randomHashSeed(this)
                : 0;
        }
        return switching;
    }

```

### remove操作

```java
    public V remove(Object key) {
        Entry<K,V> e = removeEntryForKey(key);
        //可以看到删除的key如果存在，就返回其所对应的value
        return (e == null ? null : e.value);
    }
    final Entry<K,V> removeEntryForKey(Object key) {
        if (size == 0) {
            return null;
        }
        int hash = (key == null) ? 0 : hash(key);
        int i = indexFor(hash, table.length);
        //这里用了两个Entry对象，相当于两个指针，为的是防治冲突链发生断裂的情况
        //这里的思路就是一般的单向链表的删除思路
        Entry<K,V> prev = table[i];
        Entry<K,V> e = prev;

        //当table[i]中存在冲突链时，开始遍历里面的元素
        while (e != null) {
            Entry<K,V> next = e.next;
            Object k;
            if (e.hash == hash &&
                ((k = e.key) == key || (key != null && key.equals(k)))) {
                modCount++;
                size--;
                if (prev == e) //当冲突链只有一个Entry时
                    table[i] = next;
                else
                    prev.next = next;
                e.recordRemoval(this);
                return e;
            }
            prev = e;
            e = next;
        }

        return e;
    }
```

> 到现在为止，HashMap的增删改查都介绍完了。
一般而言，认为HashMap的这四种操作时间复杂度为O(1)，因为它hash函数性质较好，保证了冲突发生的几率较小。

### fast-fail的HashIterator

集合类用[Iterator](http://docs.oracle.com/javase/7/docs/api/java/util/Iterator.html)类来遍历其包含的元素，[接口Enumeration](http://docs.oracle.com/javase/7/docs/api/java/util/Enumeration.html)已经不推荐使用。相比Enumeration，Iterator有下面两个优势：

1. Iterator允许调用者在遍历集合类时删除集合类中包含的元素（相比Enumeration增加了remove方法）
2. 比Enumeration的命名更简短

HashMap中提供的三种集合视角，底层都是用HashIterator实现的。

```java
    private abstract class HashIterator<E> implements Iterator<E> {
        Entry<K,V> next;        // next entry to return
        //在初始化Iterator实例时，纪录下当前的修改次数
        int expectedModCount;   // For fast-fail
        int index;              // current slot
        Entry<K,V> current;     // current entry

        HashIterator() {
            expectedModCount = modCount;
            if (size > 0) { // advance to first entry
                Entry[] t = table;
                //遍历HashMap的table，依次查找元素
                while (index < t.length && (next = t[index++]) == null)
                    ;
            }
        }

        public final boolean hasNext() {
            return next != null;
        }

        final Entry<K,V> nextEntry() {
            //在访问下一个Entry时，判断是否有其他线程有对集合的修改
            //说明HashMap是线程非安全的
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            Entry<K,V> e = next;
            if (e == null)
                throw new NoSuchElementException();

            if ((next = e.next) == null) {
                Entry[] t = table;
                while (index < t.length && (next = t[index++]) == null)
                    ;
            }
            current = e;
            return e;
        }

        public void remove() {
            if (current == null)
                throw new IllegalStateException();
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            Object k = current.key;
            current = null;
            HashMap.this.removeEntryForKey(k);
            expectedModCount = modCount;
        }
    }

    private final class ValueIterator extends HashIterator<V> {
        public V next() {
            return nextEntry().value;
        }
    }

    private final class KeyIterator extends HashIterator<K> {
        public K next() {
            return nextEntry().getKey();
        }
    }

    private final class EntryIterator extends HashIterator<Map.Entry<K,V>> {
        public Map.Entry<K,V> next() {
            return nextEntry();
        }
    }
```

### 序列化

介绍到这里，基本上算是把HashMap中一些核心的点讲完了，但还有个比较严重的问题：保存Entry的table数组为transient的，也就是说在进行序列化时，并不会包含该成员，这是为什么呢？
```
transient Entry<K,V>[] table = (Entry<K,V>[]) EMPTY_TABLE;
```

为了解答这个问题，我们需要明确下面事实：
- Object.hashCode方法对于一个类的两个实例返回的是不同的哈希值

我们可以试想下面的场景：
> 我们在机器A上算出对象A的哈希值与索引，然后把它插入到HashMap中，然后把该HashMap序列化后，在机器B上重新算对象的哈希值与索引，这与机器A上算出的是不一样的，所以我们在机器B上get对象A时，会得到错误的结果。
>
> 所以说，当序列化一个HashMap对象时，保存Entry的table是不需要序列化进来的，因为它在另一台机器上是错误的。

因为这个原因，HashMap重写了`writeObject`与`readObject` 方法

```java
private void writeObject(java.io.ObjectOutputStream s)
    throws IOException
{
    // Write out the threshold, loadfactor, and any hidden stuff
    s.defaultWriteObject();

    // Write out number of buckets
    if (table==EMPTY_TABLE) {
        s.writeInt(roundUpToPowerOf2(threshold));
    } else {
       s.writeInt(table.length);
    }

    // Write out size (number of Mappings)
    s.writeInt(size);

    // Write out keys and values (alternating)
    if (size > 0) {
        for(Map.Entry<K,V> e : entrySet0()) {
            s.writeObject(e.getKey());
            s.writeObject(e.getValue());
        }
    }
}

private static final long serialVersionUID = 362498820763181265L;

private void readObject(java.io.ObjectInputStream s)
     throws IOException, ClassNotFoundException
{
    // Read in the threshold (ignored), loadfactor, and any hidden stuff
    s.defaultReadObject();
    if (loadFactor <= 0 || Float.isNaN(loadFactor)) {
        throw new InvalidObjectException("Illegal load factor: " +
                                           loadFactor);
    }

    // set other fields that need values
    table = (Entry<K,V>[]) EMPTY_TABLE;

    // Read in number of buckets
    s.readInt(); // ignored.

    // Read number of mappings
    int mappings = s.readInt();
    if (mappings < 0)
        throw new InvalidObjectException("Illegal mappings count: " +
                                           mappings);

    // capacity chosen by number of mappings and desired load (if >= 0.25)
    int capacity = (int) Math.min(
                mappings * Math.min(1 / loadFactor, 4.0f),
                // we have limits...
                HashMap.MAXIMUM_CAPACITY);

    // allocate the bucket array;
    if (mappings > 0) {
        inflateTable(capacity);
    } else {
        threshold = capacity;
    }

    init();  // Give subclass a chance to do its thing.

    // Read the keys and values, and put the mappings in the HashMap
    for (int i = 0; i < mappings; i++) {
        K key = (K) s.readObject();
        V value = (V) s.readObject();
        putForCreate(key, value);
    }
}
private void putForCreate(K key, V value) {
    int hash = null == key ? 0 : hash(key);
    int i = indexFor(hash, table.length);

    /**
     * Look for preexisting entry for key.  This will never happen for
     * clone or deserialize.  It will only happen for construction if the
     * input Map is a sorted map whose ordering is inconsistent w/ equals.
     */
    for (Entry<K,V> e = table[i]; e != null; e = e.next) {
        Object k;
        if (e.hash == hash &&
            ((k = e.key) == key || (key != null && key.equals(k)))) {
            e.value = value;
            return;
        }
    }

    createEntry(hash, key, value, i);
}
```

简单来说，在序列化时，针对Entry的key与value分别单独序列化，当反序列化时，再单独处理即可。

## 总结

在总结完HashMap后，发现这里面一些核心的东西，像哈希表的冲突解决，都是算法课上学到，不过由于“年代久远”，已经忘得差不多了，我觉得忘
- 一方面是由于时间久不用
- 另一方面是由于本身没理解好

平时多去思考，这样在遇到一些性能问题时也好排查。

还有一点就是我们在分析某些具体类或方法时，不要花太多时间一些细枝末节的边界条件上，这样很得不偿失，倒不是说这么边界条件不重要，程序的bug往往就是边界条件没考虑周全导致的。
只是说我们可以在理解了这个类或方法的总体思路后，再来分析这些边界条件。
如果一开始就分析，那真是丈二和尚——摸不着头脑了，随着对它工作原理的加深，才有可能理解这些边界条件的场景。

今天到此为止，下次打算分析[TreeMap](/blog/2015/09/04/java-treemap/)。<del>Stay Tuned！🍺</del>。我已经写完了，两篇文章对比看，效果更好。

## 参考

- http://supercoderz.in/understanding-transient-variables-in-java-and-how-they-are-practically-used-in-hashmap/
- http://stackoverflow.com/questions/9144472/why-is-the-hash-table-of-hashmap-marked-as-transient-although-the-class-is-seria
