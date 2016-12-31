title: MacBook 最佳实践
date: 2014-11-23 20:40:07
categories: 热爱生活

---

这个周末终于入手 [MacBook Pro](http://www.apple.com/macbook-pro/) 了，我觉得每个屌丝在购买这么好（gui）的产品时应该都会再三考虑吧。我的初衷也很简单，一直在用的lenovo z460已经四年了，最近在用时风扇呼呼的，只开个浏览器都觉得有些卡了，在加上老话说的"工欲善其事，必先利其器"、"如果你有两个选择，那么就选择那个成本高的"，正好还可以用同学的学生证搞个教育优惠，于是这周六就去南京路的苹果店潇洒了一把。

上面扯蛋完毕。下面我想说下，作为一个从Windows转到Linux的用户，如何把玩Macbook，不至于产生"为什么XX上有，Mac上为什么没有"的尴尬问题。当然我也是刚接触，也在慢慢熟悉中，后面有更好的最佳实践我会更新文章，希望对初入 Mac 的你有些许帮助。😊

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
### ~/.bashrc

Linux 一般通过`~/.bashrc`进行环境变量的配置，但是在 Mac 下配置后，发现根本没有效果，这是为什么呢？
其实这是个比较基础的问题，shell有两种：登录式shell与非登录式shell，直观理解，登录(login)式shell就是在你打开shell要求你输入用户名与密码的shell，我们在使用桌面Linux时一般只在登录时接触到这种shell，等我们进入系统后，再打开的Terminal就是非登录式shell了。这两种 shell 读取配置的文件是不同的：

- 登录式Shell启动时会去读取`~/.profile`文件（Redhat、Mac上为 `~/.bash_profile`）
- 非登录式Shell会去读取`~/.bashrc`文件

这也就解释了为什么在 Linux 系统上只需要修改 `~/.bashrc` 后即可生效的原因。但在 Mac 上有些不同，开机后再通过 Terminal.app（或iTerm.app） 打开终端时，这时的 shell 是登录式shell，因为Terminal.app（或iTerm.app）这个应用程序是通过`/usr/bin/login`这个命令打开终端的，所以不会去`source ~/.bashrc`了。
解决方法也很简单，在~/.bash_profile加上下面一句代码就ok了
```
[ -r ~/.bashrc ] && source ~/.bashrc
```

Mac下`ls`命令默认是没有颜色的，不是很直观，可以自己设置一个alias，参考[链接](http://apple.stackexchange.com/questions/33677/how-can-i-configure-mac-terminal-to-have-color-ls-output)
```
export LSCOLORS=gxBxhxDxfxhxhxhxhxcxcx
alias ls='ls -FG'
alias ll='ls -l'
```

###JAVA_HOME

Mac下的使用`*dmg`文件安装JDK后，JAVA_HOME在那里呢，可以通过执行`/usr/libexec/java_home`这个命令来获取JAVA_HOME
```
export JAVA_HOME="$(/usr/libexec/java_home)"
```

### 修改hostname

Mac下修改hostname也和Linux下不同，命令是
```
sudo scutil --set HostName <name>
```

###查看USB设备
```
system_profiler SPUSBDataType
```

## 常用软件

我们用的软件都在`/Applications`下，每个应用程序就是一个单独的文件夹，我们常用的eclipse、sublime、iTerm之类的软件，下载压缩包解压后直接放到里面就可以了。
删除直接把对应文件夹删除即可，但是需要注意一点的时，应用程序一般都会有些历史文件，存放的位置是
- `~/Library/Application Support/<Application name>`
- `~/Library/Cache/<Application name>`
- `~/Library/Preferences/<Application name>.plist`
大家使用`find + grep`的方式就能轻松找出来了。
网上也有诸如[AppCleaner](http://appcleaner.en.softonic.com/mac)、[AppZapper](http://www.appzapper.com/)的小软件，大家可以根据需要自取之。

下面介绍下我日常编程、娱乐时的一些免费软件，供大家参考。

### 文本编辑器 [Atom](https://atom.io/)

Atom 新时代的文本编辑器，功能和 Sublime 差不多，但是免费开源，快捷键也类似，可以无缝迁移。两个非常实用的快捷键：

- Multiple Selection `Control+Command+G`（在 Linux/Windows 下，是`Alt+F3`）
- 选中多行 `Shift+Command+L`

### 终端 [iTerm 2](http://iterm2.com/)

Mac自带的终端不是很强，程序员们需要一个强劲的终端来工作，于是有了 iTerm2，这个终端可以很方便的用快捷键来达到分屏（CMD+D）、开多个Tab(CMD+T)、在多个Tab之间进行切换(CMD+数字)，其中有一点不好的是不能按字移动，如果我们在终端上键入"OPTION+向左键"，会输入一个特殊字符，我们需要自定义两个Action为Send Escape Sequence的快捷键，效果如下图：
![iTerm2](http://img01.taobaocdn.com/imgextra/i1/581166664/TB2hTnsbXXXXXbpXXXXXXXXXXXX_!!581166664.png)
我这里把向前按字移动设为了"OPTION+CMD+向左键"，向后按字移动设为了"OPTION+CMD+向右键"

当然，说到了 iTerm2，不得不提到终端复用软件 [tmux](https://tmux.github.io/)，tmux 默认配置文件在 Mac 上很别扭，你可以参考我这里的[配置文件](https://github.com/jiacai2050/code-wheels/blob/master/config/.tmux.conf)，这样 tmux 就可以像 vim 一样实现各种分屏的效果了。如果你还不知道 tmux 为何物，强烈推荐你看这个13分钟的[视频](http://pan.baidu.com/s/1gdLZzB9)，绝对物超所值，感谢 [happypeter](http://haoduoshipin.com/u/happypeter) 的分享。

终端中输入命令时，移动光标有两种方式，一个是 emacs，一个 vi，可以通过 set 命令来设置，默认的是 emacs 模式，也可以通过`set -o emacs`来显式设置，有如下快捷键：
- `ctrl + a`  Move cursor to beginning of line
- `ctrl + e`  Move cursor to end of line
- `meta + b`  Move cursor back one word
- `meta + f`  Move cursor forward one word
- `ctrl + w`  Cut the last word
- `ctrl + u`  Cut everything before the cursor
- `ctrl + k`  Cut everything after the cursor
- `ctrl + y`  Paste the last thing to be cut
- `ctrl + _`  Undo

如果想使用 vi 模式，可以使用如下命令`set -o vi`开启。
开启vi 模式后，默认是 insert 模式，按下`esc`键进入命令模式。

- `h`   Move cursor left
- `l`   Move cursor right
- `A`   Move cursor to end of line and put in insert mode
- `0`   (zero) Move cursor to beginning of line (doesn't put in insert mode)
- `i`   Put into insert mode at current position
- `a`   Put into insert mode after current position
- `dd`  Delete line (saved for pasting)
- `D`   Delete text after current cursor position (saved for pasting)
- `p`   Paste text that was deleted
- `j`   Move up through history commands
- `k`   Move down through history commands
- `u`   Undo

参考：
- [Getting Started with BASH](http://www.hypexr.org/bash_tutorial.php)
- [How To Use the Emacs Editor in Linux](https://www.digitalocean.com/community/tutorials/how-to-use-the-emacs-editor-in-linux)

其他一些有用的快捷键：
- `Ctrl + r` 搜索历史命令
- `!!` 执行上条命令
- `Ctrl+X Ctrl+E` 调用默认编辑器去编辑一个特别长的命令

###图片截屏、编辑

Mac上的截图工具已经很好了，`Cmd + Shift + 3/4`就够用了，但是如果想在图片上写些文字，马赛克某部分，就不行了，推荐用 Snip，才 2M 大小，虽说是腾讯开发的，但是不流氓。可以设置快捷键，我设定的是`Cmd + Shift + 6`。
更重要的一点是，[Snip](http://snip.qq.com/) 可以解决Retina下截屏2x问题（就是截出来的图超大），就光这个特点就足以让你使用snip。
<center>
<img width="500px" src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB2UXoxbFXXXXXnXXXXXXXXXXXX_!!581166664.png" alt="我的snip配置"/>
</center>
我平常用图片编辑就是修改像素大小，mac自带的preview就够用了。 像旋转、添加文字功能Preview也有，基本能够满足大部分人的需求。
<center>
<img src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB2KtMobFXXXXXkXpXXXXXXXXXX_!!581166664.png" alt="Preview工具栏"/>
</center>
如果你依赖于Evernote，可以试试[圈点](https://www.yinxiang.com/skitch/)，洋名skitch，同样很好很强大。

###录屏 gif

很多时候我们需要把自己的操作展示给别人看，比较好的做法是通过录屏软件将自己的操作保存成 gif 格式的图片。
[开源免费](https://github.com/lepht/licecap)的[licecap](http://www.cockos.com/licecap/) 很好的解决了这个问题。

![使用 licecap 制作的例子](http://ww3.sinaimg.cn/mw690/5fee18eegw1f17799uiz1g20ci0cijs2.gif)


### 流程图制作工具

对于程序员来说，流程图应该是再亲切不过的了，一张图胜过千言万语。之前我都是用 Keynote 来画，但是实在是不好用，后来在[知乎](https://www.zhihu.com/question/19588698)上发现了在线版的[ProcessOn](https://www.processon.com/)，大大减少了我画流程图的时间，上手也比较快。

###视频播放器

Mac下的自带的播放器QuickTime，功能实在是太弱了，支持的格式既少又难用，快进什么的貌似都没快捷键，只能手动点击进度条，试用了一段时间的[Mplayer](http://mplayerosx.ch/)，发现效果也不好，会有视频卡顿的现象，最终选择了 [VLC](http://www.videolan.org/vlc/download-macosx.html)，一直用的还不错。


###音乐频播放器

官方的 iTunes 实在是不适应，喜欢简洁清爽的朋友可以试试 [VOX](http://coppertino.com/)

### *.webarchive

大家都知道，在windows下保存网页时，如果想把网页上的资源，比如css、js、image等一起下载下来，会单独生成个文件夹，但是用mac上的safari保存整个网页时，是以`webarchive`为后缀名的文件进行保存的，如何把打开这种文件呢？推荐：
http://sourceforge.net/projects/webarchivext/

## 常用快捷键

###系统

- 查看桌面`F11`
- HOME  `Command + <-`
- END   `Command + ->`
- 锁屏   `Shift + Control + 电源键` （Windows 下为`Win+L`）
- 强制关闭程序 `Command + Option + esc`（Windows 下为`Ctrl+Alt+Delete`）

###Finder
Finder是Mac上的文件浏览器，其中有个比较严重的问题时，没有“剪贴(cut)”功能，当我们选中一个文件后，菜单中的“Edit”->“Cut”是灰色的，也就是无法使用，这是因为Finder中的“Cut”只适用于文本，对于文件就无能为力了。
我们当然可以通过打开两个Finder窗口，然后“拖”过去。但是这样未免太麻烦了，其实我们可以这么做：
1. 首先`Cmd + C`复制文件
2. 然后找到你想要放到文件夹
3. 最后`Cmd + Option + V`就能实现“剪贴”的效果了。

参考：[Why is it not possible to use the “cut” command to manipulate a file in the Finder?](http://apple.stackexchange.com/questions/12391/why-is-it-not-possible-to-use-the-cut-command-to-manipulate-a-file-in-the-find)


## FileSystem

### 目录结构

尽管Mac的文件系统目录和*nix差不多，但还是有些差距，可参考下面的表格：
![Mac-FileSystem](http://img04.taobaocdn.com/imgextra/i4/581166664/TB2SgzpbXXXXXbSXpXXXXXXXXXX_!!581166664.png)


### NTFS

用惯了 Windows 的大家都习惯用 NTFS 文件系统格式，但是很遗憾，这个文件系统是微软自己搞得，不是开放的，所有我们的 Mac 是不支持的，如果你以前的 NTFS 格式的硬盘放到 Mac 上，会发现只能进行读操作，不能写入，这属于正常现象，不要惊慌。

解决的方法也很简单，把移动硬盘格式化成FAT32(单个文件大小不能超过4G)或FAText 格式都可以，Mac 自带的磁盘工具就可以进行格式转化，当然你需要先把移动硬盘上的数据拷贝出来。

## Wi-Fi 时常中断

Mac 生于乔帮主之手时，为了凸显尊贵，接口与一般的电脑有很大不同。常见的网线没办法直接连接 Mac 电脑，需要单独购买一个[以太网转接器](http://www.apple.com/cn/shop/product/MC704FE/A/apple-usb-ethernet-adapter)，所以大部分同学都是使用无线连接，但 Mac 这里应该是有个 bug，而且是很久的 bug，我用 Mac 两年了，偶尔会遇到几次，网上解决的方法有如下几种：

1. 修改网络位置，不是其默认的“自动”就好
2. 修改路由器，把无线信道改为6或9
3. 关闭蓝牙，Mac 中，同时打开蓝牙与 Wi-Fi 会冲突。[详情](http://apple.stackexchange.com/a/162406/103966)

如果你的 Mac 也遇到了 Wi-Fi 问题，可以试试上面三个解决方法。

## 总结

Mac 的 Retina 屏幕真是无与伦比，虽说系统一开始需要适应，但我相信，Mac Pro 绝对不会让你失望的，不是有句话嘛：

> Once you get Mac, you never come back!

## 参考

- [OS X 的一些技巧汇总](http://havee.me/mac/2014-01/os-x-tips-and-tricks.html)
