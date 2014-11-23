title: MacBook 初体验
date: 2014-11-23 20:40:07
tags: mac
categories: life

---

这个周末终于入手MacBook-Retina了，我觉得每个屌丝在购买这么好（gui）的产品时应该都会再三考虑吧。我的初衷也很简单，一直在用的lenovo z460已经四年了，最近在用时风扇呼呼的，只开个浏览器都觉得有些卡了，在加上老话说的"工欲善其事，必先利其器"、"如果你有两个选择，那么就选择那个成本高的"，正好还可以用同学的学生证搞个教育优惠，于是这周六就去南京路的苹果店潇洒了一把。

上面扯蛋完毕。下面我想说下，作为一个从Windows转到Linux的用户，如何把玩Macbook，不至于产生"为什么XX上有，Mac上为什么没有"的尴尬问题。当然我也是刚接触，也在慢慢熟悉中，如果那里说的不对，欢迎大家斧正。

##Mac OS 简介


Mac OS可以被分成操作系统的两个系列：

- 一个是老旧且已不被支持的“Classic”Mac OS（系统搭载在1984年销售的首部Mac与其后代上，终极版本是Mac OS 9）。采用Mach作为內核，在Mac OS 7.6.1以前用“System vX.X”来称呼。
- 新的OS X结合[BSD Unix](http://zh.wikipedia.org/wiki/BSD)、OpenStep和Mac OS 9的元素。它的最底层建基于Unix基础，其代码被称为Darwin，实行的是部分开放源代码。

关于为什么Mac系统没有采用Linux内核，而是采用了BSD还有个小故事，感兴趣的大家可以看[Mac OS X 背后的故事（二）——Linus Torvalds的短视](http://www.programmer.com.cn/6617/)这篇文章。

##Mac 开发环境部署

###Homebrew

大家都知Mac上下软件需要从Apple Store里面下，但是我们平时开发用到的很多开源软件，比如nodejs、wget等工具需要单独下载，目前Mac上最好的包管理器是[Homebrew](http://brew.sh/)，有了它，我们就能够想在ubuntu下使用apt-get，在Redhat下使用yum一样方便的来管理这些包了。安装很简单，执行下面的命令即可：
```
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
###~/.bashrc

熟悉Linux的一般通过~/.bashrc这个文件进行环境变量的配置，但是在Mac下配置后，发现根本没有效果，这是为什么呢？
其实这时个比较基础的问题，shell有两种：登录式shell与非登录式shell，直观理解，登录(login)式shell就是在你打开shell要求你输入用户名与密码的shell，我们在使用桌面Linux时一般只在登录时接触到这种shell，等我们进入系统后，再打开的Terminal就是非登录式shell了。
* 登录式Shell启动时回去source ~/.profile文件（Redhat、Mac上为~/.bash_profile）
* 非登录式Shell会去source ~/.bashrc文件

在Mac上，我们开机后在打开终端时，这时的shell是登录式shell，因为Terminal.app（或iTerm.app）这个应用程序是通过'/usr/bin/login'这个命令打开终端的，所以不会去source ~/.bashrc了。
解决方法也很简单，在~/.bash_profile加上下面一句代码就ok了
```
[ -r ~/.bashrc ] && source ~/.bashrc
```

###iTerm.app

Mac自带的终端不是很强，程序员们需要一个强劲的终端来工作，于是有了[iTerm](http://iterm2.com/)，这个终端可以很方便的用快捷键来达到分屏（CMD+D）、开多个Tab(CMD+T)、在多个Tab之间进行切换(CMD+数字)，其中有一点不好的是不能按字移动，如果我们在终端上键入"OPTION+向左键"，会输入一下特殊字符，我们需要自定义两个Action为Send Escape Sequence的快捷键，方式如下图：
<img src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB2hTnsbXXXXXbpXXXXXXXXXXXX_!!581166664.png" alt=" iterm2"/>
我这里把向前按字移动设为了"OPTION+CMD+向左键"，向后按字移动设为了"OPTION+CMD+向右键"

###JAVA_HOME

Mac下的使用*dmg方式安装JDK后，JAVA_HOME在那里呢，这对于Linux下使用tar包安装的人可傻眼了，设置JAVA_HOME可参考下面的命令
```
export JAVA_HOME="$(/usr/libexec/java_home)"
```
可以看到，其实就是通过执行'/usr/libexec/java_home'这个命令来获取JAVA_HOME

###修改hostname

Mac下修改hostname也和Linux下不同，命令是
```
sudo scutil --set HostName <name>
```
###FileSystem

尽管Mac的文件系统目录和*nix差不多，但还是有些差距，可参考下面的表格：
<img src="http://img04.taobaocdn.com/imgextra/i4/581166664/TB2SgzpbXXXXXbSXpXXXXXXXXXX_!!581166664.png" alt=" Mac-FileSystem"/>

###软件的安装与删除

我们用的软件都在'/Applications'下，每个应用程序就是一个单独的文件夹，我们常用的eclipse、sublime、iTerm之类的软件，下载tar包解压后直接放到里面就可以了。
删除直接把对应文件夹删除即可，但是需要注意一点的时，应用程序一般都会有些配置文件，存放的位置是'/Users/<username>/Library/Application Support'这个文件夹下，也是一个应用程序对于一个文件夹，直接删除相应文件夹即可~~~

##总结

Mac的Retina屏幕真是无与伦比，虽说一开始需要适应适应软件、键盘的操作，但我相信，Mac绝对不会让你失望的，不是有句话嘛：

> Once you get Mac, you never come back!

毕竟刚用Mac两天，很多Mac的特性都还不知道，随着今后的使用，我会在更新文章，与大家分享使用Mac的心得的~~

