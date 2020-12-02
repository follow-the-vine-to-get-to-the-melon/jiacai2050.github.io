title: 正则表达式“派别”简述
date: 2014-12-07 19:07:48
categories: 理解计算机
tags: [Linux]

---

相信大家对于正则表达式都不陌生，在文本处理中或多或少的都会使用到它。但是，我们在使用linux下的文本处理工具如awk、sed等时，正则表达式的语法貌似还不一样，在awk中能正常工作的正则，在sed中总是不起作用，这是为什么呢？

这个问题产生的缘由是因为正则表达式不断演变的结果，为了弄清楚这些工具使用的正则语法的不同，我们有必要去简单了解下正则的演变过程，做到知己知彼。当然这个过程本身也是很精彩的，我这里抛砖引玉，希望对大家正确使用正则表达式有所帮助。

## 诞生期

正则表示式这一概念最早可以追溯到20世纪40年代的两个神经物理学家Warren McCulloch与Walter Pitts，他们将神经系统中的神经元描述成小而简单的自动控制元；紧接着，在50年代，数学家1950年代，数学家[Stephen Kleene](http://en.wikipedia.org/wiki/Stephen_Cole_Kleene)利用称之为“正则集合”的数学符号来描述此模型，并且建议使用一个简单的概念来表示，于是regular expressions就正式登上历史舞台了。插播一下，这个Kleene可不是凡人，大家都知道图灵是现代人工智能之父，那图灵的博导是[Alonzo Church](http://en.wikipedia.org/wiki/Alonzo_Church)，提出了lambda表达式，而Church的老师，就是Kleene了。关于lambda，之前也写过一篇文章，大家可以参考[编程语言的基石——Lambda calculus](/blog/2014/10/12/lambda-calculus-introduction/)。

在接下来的时间里，一直到60年代的这二十年里，正则表示式在[理论数学领略](http://en.wikipedia.org/wiki/Pure_mathematics)得到了长足的发展，[Robert Constable](http://www.cs.cornell.edu/home/rc/)为数学发烧友们写了一篇总结性文章[The Role of Finite Automata in the Development of Modern Computing Theory](http://www.sciencedirect.com/science/article/pii/S0049237X08712539)，由于版权问题，我在网上没找到这篇文章，大家有兴趣的可以参考[Basics of Automata Theory](http://cs.stanford.edu/people/eroberts/courses/soco/projects/2004-05/automata-theory/basics.html)。

Ken Thompson大牛在1968年发表了[Regular Expression Search Algorithm](http://www.fing.edu.uy/inco/cursos/intropln/material/p419-thompson.pdf)论文，紧接着Thompson根据这篇论文的算法实现了[qed](http://en.wikipedia.org/wiki/QED_%28text_editor%29)，qed是unix上编辑器ed的前身。ed所支持的正则表示式并不比qed的高级，但是ed是第一个在非技术圈广泛传播的工具，ed有一个命令可以展示文本中符合给定正则表达式的行，这个命令是` g/Regular Expression/p`，在英文中读作“Global Regular Expression Print”，由于这个命令非常实用，所以后来有了grep、egrep这两个命令。

## 成长期

相比egrep，grep只支持很少的元符号，`＊`是支持的（但不能用于分组中），但是`+`、`|`与`?`是不支持的；而且，分组时需要加上反斜线转义，像`\( ...\)`这样才行，由于grep的缺陷性日渐明显，AT&T的[Alfred Aho](http://en.wikipedia.org/wiki/Alfred_Aho)实在受不了了，于是egrep诞生了，这里的e表示extended，加强版的意思，支持了`+`、`|`与`?`这三个元符号，并且可以在分组中使用`*`，分组可以直接写成`(...)`，同时用`\1,\2...`来引用分组。

在grep、egrep发展的同时，awk、lex、sed等程序也开始发展起来，而且每个程序所支持的正则表达式都或多或少的和其他的不一样，这应该算是正则表达式发展的混乱期，因为这些程序在不断的发展过程中，有时新增加的功能因为bug原因，在后期的版本中取消了该功能，例如，如果让grep支持元符号`+`的话，那么grep就不能表示字符`+`了，而且grep的老用户会对这很反感。

## 成熟期

这种混乱度情况一直持续到了1986年。在1986年，POSIX（Portable Operating System Interface）标准公诸于世，POSIX制定了不同的操作系统都需要遵守的一套规则，当然，正则表达式也包括其中。

当然，除了POSIX标准外，还有一个Perl分支，也就是我们现在熟知的PCRE，随着Perl语言的发展，Perl语言中的正则表达式功能越来越强悍，为了把Perl语言中正则的功能移植到其他语言中，PCRE就诞生了。现在的编程语言中的正则表达式，大部分都属于PCRE这个分支。

下面分别所说这两个分支。

### POSIX标准
POSIX把正则表达式分为两种（favor）：BRE（Basic Regular Expressions）与ERE（Extended Regular Expressions ）。所有的POSIX程序可以选择支持其中的一种。具体规范如下表：
<img src="http://img03.taobaocdn.com/imgextra/i3/581166664/TB2uVx6bpXXXXaDXpXXXXXXXXXX_!!581166664.png" alt=" posix-regexp-favor"/>

从上图可以看出，有三个空白栏，那么是不是就意味这无法使用该功能了呢？答案是否定的，因为我们现在使用的linux发行版，都是集成GNU套件的，GNU是Gnu's Not Unix的缩写，GNU在实现了POXIS标准的同时，做了一定的扩展，所以上面空白栏中的功能也能使用。下面一一讲解：

1. BRE如何使用`+`、`?`呢？需要用`\+`、`\?`
2. BRE如何使用`|`呢？需要用`\|`
3. ERE如何使用`\1`、`\2`...`\9`这样的反引用？和BRE一样，就是`\1`、`\2`...`\9`

通过上面总结，可以发现：GNU中的ERE与BRE的功能相同，只是语法不同（BRE需要用`\`进行转义，才能表示特殊含义）。例如`a{1,2}`，在ERE表示的是`a`或`aa`，在BRE中表示的是`a{1,2}`这个字符串。为了能够在Linux下熟练使用文本处理工具，我们必须知道这些命令支持那种正则表达式。现对常见的命令总结如下：

－ 使用BRE语法的命令有：grep、ed、sed、vim
－ 使用ERE语法的命令有：egrep、awk、emacs

当然，这也不是绝对的，比如 sed 通过-r选项就可以使用ERE了，大家到时自己man一下就可以了。

还值得一提的是POSIX还定义了一些shorthand，具体如下：

- [:alnum:]
- [:alpha:]
- [:cntrl:]
- [:digit:]
- [:graph:]
- [:lower:]
- [:print:]
- [:punct:]
- [:space:]
- [:upper:]
- [:xdigit:]

在使用这些shorthand时有一个约束：必须在`[]`中使用，也就是说如果像匹配0-9的数字，需要这么写`[[:alnum:]]`，取反就是`[^[:alnum:]]`。shorhand 在BRE与EBE中的用法相同。

如果你对sed、awk比较熟悉，你会发现我们平常在变成语言中用的`\d`、`\w`在这些命令中不能用，原因很简单，因为POSIX规范根本没有定义这些shorthand，这些是由下面将要说的PCRE中定义的。

### PCRE标准

Perl语言第一版是由[Larry Wall](http://en.wikipedia.org/wiki/Larry_Wall)发布于1987年12月，Perl在发布之初，就因其强大的功能而一票走红，Perl的定位目标就是“天天要使用的工具”。Perl比较显诸特征之一是与sed与awk兼容，这造就了Perl成为第一个通用性脚本语言。

随着Perl的不断发展，其支持的正则表达式的功能也越来越强大。其中影响较大的是于1994年10月发布的Perl 5，其增加了很多特性，比如non-capturing parentheses、lazy quantifiers、look-ahead、元符号\\G等等。

正好这时也是WWW兴起的时候，而Perl就是为了文本处理而发明的，所以Perl基本上成了web开发的首选语言。Perl语言应用是如此广泛，以至于其他语言开始移植Perl，最终Perl compatible（兼容）的PCRE诞生了，这其中包括了Tcl, Python, Microsoft’s .NET , Ruby, PHP, C/C++, Java等等。

前面说了shorthand在POSIX与PCRE是不同的，PCRE中我们常用的有如下这些：

- `\w` 表示`[a-zA-Z]`
- `\W` 表示`[^a-zA-Z]`
- `\s` 表示`[ \t\r\n\f]`
- `\S` 表示`[^ \t\r\n\f]`
- `\d` 表示`[1-9]`
- `\D` 表示`[^1-9]`
- `\<` 表示一个单词的起始
- `\>` 表示一个单词的结尾

关于shorthand在两种标准的比较，更多可参考[Wikipedia](http://en.wikipedia.org/wiki/Regular_expression#Character_classes)

## 总结

我相信大家最初接触正则表达式（RE）这东西，都是在某个语言中，像 Java、Python等，其实这些语言的正则表达式都是基于PCRE标准的。
而Linux下使用各种处理文本的命令，是继承自POSIX标准，不过是由GNU扩展后的而已。

大家如果对 sed、awk命令不熟悉，可以参考耗子叔下面的两篇文章：

- [sed 简明教程](http://coolshell.cn/articles/9104.html)
- [awk 简明教程](http://coolshell.cn/articles/9070.html)

## 参考

- [GNU Regular Expression Extensions](http://www.regular-expressions.info/gnu.html)
- [POSIX Bracket Expressions](http://www.regular-expressions.info/posixbrackets.html)
- [Different types of regular expressions Gnulib supports](https://www.gnu.org/software/gnulib/manual/html_node/Regular-expression-syntaxes.html)
- [Regular_expression](http://en.wikipedia.org/wiki/Regular_expression)
- [Linux/Unix工具与正则表达式的POSIX规范](http://www.infoq.com/cn/news/2011/07/regular-expressions-6-POSIX)
