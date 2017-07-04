title: MacBook 最佳实践
date: 2014-11-23 20:40:07
tags: 最佳实践

---

MacBook 兼具命令行的高效与图形界面的酷炫，实在是程序员必备利器。本文主要介绍我在两年的使用过程中总结出的一些最佳实践，供大家参考、借鉴。

![MacBook 你值得拥有](https://dn-mhke0kuv.qbox.me/cb49a18efb421a9624c5.png)

## Mac OS 简介

Mac OS可以被分成操作系统的两个系列：

- 一个是老旧且已不被支持的“Classic”Mac OS（系统搭载在1984年销售的首部Mac与其后代上，终极版本是Mac OS 9）。采用Mach作为內核，在Mac OS 7.6.1以前用“System vX.X”来称呼。
- 新的OS X结合[BSD Unix](http://zh.wikipedia.org/wiki/BSD)、OpenStep和Mac OS 9的元素。它的最底层建基于Unix基础，其代码被称为Darwin，实行的是部分开放源代码。

关于为什么Mac系统没有采用Linux内核，而是采用了BSD还有个小故事，感兴趣的大家可以看[Mac OS X 背后的故事（二）——Linus Torvalds的短视](https://zhuanlan.zhihu.com/p/20263877)这篇文章。

尽管 Mac 的文件系统目录和 Linux 差不多，但还是有些差距，可参考下面的表格：

![Mac-FileSystem](http://img04.taobaocdn.com/imgextra/i4/581166664/TB2SgzpbXXXXXbSXpXXXXXXXXXX_!!581166664.png)

## Mac 开发环境部署

### 包管理器 [Homebrew](http://brew.sh/)

> The missing package manager for macOS

`brew`相当于`Ubuntu`下的`apt-get`，`CentOS`中的`yum`。非常方便实用，一条命令即可安装：

```
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
- `brew install <cli-program>`，安装命令行工具
- `brew cask install <gui-program>`，安装图形界面软件，这得益于[Homebrew-Cask](https://github.com/caskroom/homebrew-cask)扩展

### 文本编辑器 [VSCode](https://code.visualstudio.com/)

```
# 安装命令
brew cask install visual-studio-code
```
新时代的文本编辑器，功能和 Sublime 差不多，快捷键也类似，可以无缝迁移。两个非常实用的快捷键：

- Multiple Selection `Control+Command+G`（在 Linux/Windows 下，是`Alt+F3`）
- 选中多行 `Shift+Command+L`

我个人使用编辑器的经历是 Sublime --> Atom --> VSCode。·

### 神之编辑器 [Emacs](https://www.emacswiki.org/emacs?interface=en)

```
# 安装命令
brew install --with-cocoa --srgb emacs
```
其实 Mac 是有自带 Emacs 的，位置是`/usr/bin/emacs`，只是版本非常旧，通过`brew`安装的位置在`/usr/local/bin/emacs`，可以通过下面的命令删除 Mac 自带的 Emacs：
```
sudo rm /usr/bin/emacs
sudo rm -rf /usr/share/emacs
```
为了能在 git，终端中默认使用 Emacs，需要做以下配置：
```
# ~/.bashrc
export EDITOR="emacsclient -t -a=\"\""
export ALTERNATE_EDITOR=""

# ~/.gitconfig
[core]
    editor = emacsclient -t -a=\\\"\\\"
```
上面的配置会调用 `emacsclient` 去连接 `emacs daemon`服务，如果服务没启，就先启动服务再去连接。

### API 查阅工具[Dash](https://kapeli.com/dash)

```
# 安装命令
brew cask install dash
```
> Dash gives your Mac instant offline access to 150+ API documentation sets.

安装 Dash 后，就可以离线查各种语言/框架的 API 文档了。🍺

![](https://img.alicdn.com/imgextra/i2/581166664/TB2x_3QcNdkpuFjy0FbXXaNnpXa_!!581166664.png)

### 抓包工具 [Wireshark](https://www.wireshark.org/)

```
# 安装命令
brew cask install wireshark
```
也许是最强大的抓包工具，从其名字上就能体现出：wire（线路）+ shark（鲨鱼）。但这个软件初次使用时有些难度，最重要的是区分两个概念：
- `capture filter`，在抓包开始时指定。
![capture filter](https://img.alicdn.com/imgextra/i1/581166664/TB2dcIUcHXlpuFjSszfXXcSGXXa_!!581166664.png)
常见表达式

```
# Capture only traffic to or from IP address 172.18.5.4:
host 172.18.5.4

# Capture traffic to or from a range of IP addresses:
net 192.168.0.0/24

# Capture non-HTTP and non-SMTP traffic on your server (both are equivalent):
host www.example.com and not (port 80 or port 25)
host www.example.com and not port 80 and not port 25

# Capture traffic within a range of ports  with newer versions of libpcap (0.9.1 and later):
tcp portrange 1501-1549

#Capture only IPv4 traffic - the shortest filter, but sometimes very useful to get rid of lower layer protocols like ARP and STP:
ip

# Capture only unicast traffic - useful to get rid of noise on the network if you only want to see traffic to and from your machine, not, for example, broadcast and multicast announcements:
not broadcast and not multicast
```
- `display filter`，在抓取一定包后进行过滤。
![display filter](https://img.alicdn.com/imgextra/i2/581166664/TB2L5U0cHJkpuFjy1zcXXa5FFXa_!!581166664.png)
常见表达式

```
ip.dst_host == 192.168.30.103 and tcp.dstport == 80

ip.addr == 10.43.54.65
# is equivalent to
ip.src == 10.43.54.65 or ip.dst == 10.43.54.65
```

### 终端 [iTerm 2](http://iterm2.com/)
```
# 安装命令
brew cask install iterm2
```
Mac自带的终端不是很强，程序员们需要一个强劲的终端来工作，于是有了 iTerm2，这个终端可以很方便的用快捷键来达到分屏（CMD+D）、开多个Tab(CMD+T)、在多个Tab之间进行切换(CMD+数字)，其中有一点不好的是不能按字移动，如果我们在终端上键入"OPTION+向左键"，会输入一个特殊字符，我们需要自定义两个Action为Send Escape Sequence的快捷键，效果如下图：
![iTerm2](http://img01.taobaocdn.com/imgextra/i1/581166664/TB2hTnsbXXXXXbpXXXXXXXXXXXX_!!581166664.png)
我这里把向前按字移动设为了"OPTION+CMD+向左键"，向后按字移动设为了"OPTION+CMD+向右键"。

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
- `Ctrl+x Ctrl+e` 调用[默认编辑器去编辑一个特别长的命令](http://www.commandlinefu.com/commands/view/1446/rapidly-invoke-an-editor-to-write-a-long-complex-or-tricky-command)


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
为了在命令行提示符中显示时间，可以设置`PS1`变量
```
export PS1="\n\e[1;37m[\e[m\e[1;35m\u\e[m\e[1;36m@\e[m\e[1;37m\h\e[m \e[1;33m\t\e[m \w\e[m\e[1;37m]\e[m\e[1;36m\e[m\n\$ "

# 效果如下
[liujiacai@macbook 22:02:13 ~]
```

### 系统快捷键

- 查看桌面`F11`
- HOME  `Command + <-`
- END   `Command + ->`
- 锁屏   `Shift + Control + 电源键` （Windows 下为`Win+L`）
- 强制关闭程序 `Command + Option + esc`（Windows 下为`Ctrl+Alt+Delete`）

### Finder
Finder是Mac上的文件浏览器，其中有个比较严重的问题时，没有“剪贴(cut)”功能，当我们选中一个文件后，菜单中的“Edit”->“Cut”是灰色的，也就是无法使用，这是因为Finder中的“Cut”只适用于文本，对于文件就无能为力了。
我们当然可以通过打开两个Finder窗口，然后“拖”过去。但是这样未免太麻烦了，其实我们可以这么做：
1. 首先`Cmd + C`复制文件
2. 然后找到你想要放到文件夹
3. 最后`Cmd + Option + V`就能实现“剪贴”的效果了。

参考：[Why is it not possible to use the “cut” command to manipulate a file in the Finder?](http://apple.stackexchange.com/questions/12391/why-is-it-not-possible-to-use-the-cut-command-to-manipulate-a-file-in-the-find)

### JDK

```
# 安装命令
brew cask install java
```
通过`brew cask`安装后，可以通过执行`/usr/libexec/java_home`这个命令来获取JAVA_HOME
```
export JAVA_HOME="$(/usr/libexec/java_home)"
```

### 实用命令

```
# 修改hostname
sudo scutil --set HostName <name>
# 查看USB设备
system_profiler SPUSBDataType
```

下面的命令需要通过`brew`进行安装后在使用
```
# 查看网络请求
brew install httpstat
$ httpstat baidu.com
Connected to 180.149.132.47:80 from 172.17.10.80:54727

HTTP/1.1 200 OK
Date: Sat, 14 Jan 2017 13:49:16 GMT
Server: Apache
Last-Modified: Tue, 12 Jan 2010 13:48:00 GMT
ETag: "51-47cf7e6ee8400"
Accept-Ranges: bytes
Content-Length: 81
Cache-Control: max-age=86400
Expires: Sun, 15 Jan 2017 13:49:16 GMT
Connection: Keep-Alive
Content-Type: text/html

Body stored in: /var/folders/2g/fxz_98ks0lgc79sjp5vn5cxc0000gn/T/tmpsawHq4

  DNS Lookup   TCP Connection   Server Processing   Content Transfer
[    69ms    |      37ms      |       33ms        |        0ms       ]
             |                |                   |                  |
    namelookup:69ms           |                   |                  |
                        connect:106ms             |                  |
                                      starttransfer:139ms            |
                                                                 total:139ms

# Swiss Army Knife for macOS !
brew install m-cli
$ m trash status
Size:  51G
Number of files: 252172

```

## 常用软件

日常使用的软件首选通过`App Store`进行安装，默认安装在`/Applications`下，个人从互联网上单独下载的软件放在这里面即可出现在`Launchpad`中找到。
对于通过`App Store`安装的软件，在`Launchpad`界面，按住`Option`键可进行删除。但是需要注意一点的时，应用程序一般都会有些历史文件，存放的位置有如下三处

- `~/Library/Application Support/<Application name>`
- `~/Library/Cache/<Application name>`
- `~/Library/Preferences/<Application name>.plist`

使用`find + grep`的方式就能轻松找出来了。网上也有诸如[AppCleaner](http://appcleaner.en.softonic.com/mac)、[AppZapper](http://www.appzapper.com/)的小软件，大家可以根据需要自取之。

下面介绍下我日常使用的一些免费软件，供大家参考。

> PS: Mac 下有很多非常实用的收费软件，我个人用的并不多，这里就不在列举了。
大家可以参考知乎上的 [macOS (OS X) 平台上有哪些值得推荐的常用软件？](https://www.zhihu.com/question/19550256)

### 浏览器

Mac 上自带的 Safari 比较轻量，虽然比较省电，但扩展性远不如 Chrome、Firefox，所以这两个是必须的。
```
brew cask install firefox
brew cask install google-chrome
```

### 科学上网 Shadowsocks

```
brew install shadowsocks-libev
```
Mac 下不推荐安装 GUI 版本，已经很久没人维护了。安装之后编辑`/usr/local/etc/shadowsocks-libev.json`，填入 server 地址即可。
```
# 测试
ss-local -v -c /usr/local/etc/shadowsocks-libev.json
# 开机启动
brew services start shadowsocks-libev

```

### 图片截屏、合并

Mac上的截图工具已经很好了，`Cmd + Shift + 3/4`就够用了，但是如果想在图片上写些文字，马赛克某部分，就不行了，推荐用 Snip，才 2M 大小，虽说是腾讯开发的，但是不流氓。可以设置快捷键，我设定的是`Cmd + Shift + 6`。
更重要的一点是，[Snip](http://snip.qq.com/) 可以解决Retina下截屏2x问题（就是截出来的图超大），就光这个特点就足以让你使用snip。
<center>
<img width="500px" src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB2UXoxbFXXXXXnXXXXXXXXXXXX_!!581166664.png" alt="我的snip配置"/>
</center>
Mac自带的 Preview 可以对图片进行旋转、调整大小、添加文字，不需要在额外安装软件。
<center>
<img src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB2KtMobFXXXXXkXpXXXXXXXXXX_!!581166664.png" alt="Preview工具栏"/>
</center>

此外，如果要对两张图片进行合并，需要通过安装 [ImageMagick](https://www.imagemagick.org)，并且通过以下命令操作：[出处](http://apple.stackexchange.com/a/52882/103966)

```
brew install ImageMagick

# 下面两条命令都会把 left.png right.png 合并到 merged.png 里面
convert +append left.png right.png merged.png

montage -geometry 100% left.jpg right.jpg merged.jpg
```

如果你依赖于Evernote，可以试试[圈点](https://www.yinxiang.com/skitch/)，洋名skitch，同样很好很强大。

### 录屏 gif
```
# 安装命令
brew cask install licecap
```
很多时候我们需要把自己的操作展示给别人看，比较好的做法是通过录屏软件将自己的操作保存成 gif 格式的图片。
[开源免费](https://github.com/lepht/licecap)的[licecap](http://www.cockos.com/licecap/) 很好的解决了这个问题。

![使用 licecap 制作的例子](http://ww3.sinaimg.cn/mw690/5fee18eegw1f17799uiz1g20ci0cijs2.gif)

### 流程图制作工具

对于程序员来说，流程图应该是再亲切不过的了，一张图胜过千言万语。之前我都是用 Keynote 来画，但是实在是不好用，<del>后来在[知乎](https://www.zhihu.com/question/19588698)上发现了在线版的[ProcessOn](https://www.processon.com/)，大大减少了我画流程图的时间，上手也比较快。</del>现在 ProcessOn 有了限制，只能保留 9 张流程图。我又找到了新的工具，[draw.io](https://www.draw.io)，时序图、状态图统统不在话下。

其次，国外很多项目的图是用纯文本画的，比较好用的在线工具是：[asciiflow](http://asciiflow.com/)。

### 视频播放器、截取

```
# 安装命令
brew cask install vlc
```
Mac下的自带的播放器QuickTime，功能实在是太弱了，支持的格式既少又难用，快进什么的貌似都没快捷键，只能手动点击进度条，试用了一段时间的[Mplayer](http://mplayerosx.ch/)，发现效果也不好，会有视频卡顿的现象，最终选择了 [VLC](http://www.videolan.org/vlc/download-macosx.html)，一直用的还不错。
此外， 有网友补充道 [mpv](https://mpv.io/) 才是程序员最佳播放器，大家也可以尝试下。

很多时候，我们只需要截取视频中的某一段视频，或者简单的进行格式转换，这时候就需要 ffmpeg 出马了。
```
# 安装命令
brew  install ffmpeg

# 将 mov 格式的视频转为 mp4，ffmpeg 能根据文件后缀名自动识别
ffmpeg  -i foo.mov foo.mp4
# 从第 6 秒开始，截取10s 视频，并且转为 mp4 格式
ffmpeg -t 10 -ss 00:00:06 -i foo.mov smaller.mp4
```

### 音乐频播放器
```
# 安装命令
brew cask install vox
```
官方的 iTunes 实在是不适应，喜欢简洁清爽的朋友可以试试 [VOX](http://coppertino.com/)

### *.webarchive

在windows下保存网页时，如果想把网页上的资源，比如css、js、image等一起下载下来，会单独生成个文件夹，但是用 Mac 上的 Safari 保存整个网页时，是以`webarchive`为后缀名的文件进行保存的，如何把打开这种文件呢？推荐：

http://sourceforge.net/projects/webarchivext/

### 虚拟机 [Virtualbox](https://www.virtualbox.org/)

```
# 安装命令
brew cask install virtualbox
```

在天朝，很多网站是只支持 IE 的，Mac 下的 Firefox, Chrome, Safari 这时候都显得心有力而不足了，而且很多软件也只有 Windows 版，所以装个虚拟机是非常有必要的。 Virtualbox 是我自用 Ubuntu 以来一直用的虚拟机，开源免费。

![Virtualbox](https://img.alicdn.com/imgextra/i4/581166664/TB2aVGdcNlmpuFjSZPfXXc9iXXa_!!581166664.png)

## 常见问题

### 不能写 NTFS

用惯了 Windows 的大家都习惯用 NTFS 文件系统格式，但是很遗憾，这个文件系统是微软自己搞得，不是开放的，所以 Mac 是不支持的，如果你以前的 NTFS 格式的硬盘放到 Mac 上，会发现只能进行读操作，不能写入，这属于正常现象，不要惊慌。

解决的方法也很简单，把移动硬盘格式化成FAT32(单个文件大小不能超过4G)或FAText 格式都可以，Mac 自带的磁盘工具就可以进行格式转化，当然你需要先把移动硬盘上的数据拷贝出来。

### Wi-Fi 时常中断

Mac 生于乔帮主之手时，为了凸显尊贵，接口与一般的电脑有很大不同。常见的网线没办法直接连接 Mac 电脑，需要单独购买一个[以太网转接器](http://www.apple.com/cn/shop/product/MC704FE/A/apple-usb-ethernet-adapter)，所以大部分同学都是使用无线连接，但 Mac 这里应该是有个 bug，而且是很久的 bug，我用 Mac 两年了，偶尔会遇到几次，网上解决的方法有如下几种：

1. 修改网络位置，不是其默认的“自动”就好
2. 修改路由器，把无线信道改为6或9
3. 关闭蓝牙，Mac 中，同时打开蓝牙与 Wi-Fi 会冲突。[详情](http://apple.stackexchange.com/a/162406/103966)

如果你的 Mac 也遇到了 Wi-Fi 问题，可以试试上面三个解决方法。

## 总结

> Once you get Mac, you never come back!

## 参考

- [OS X 的一些技巧汇总](http://havee.me/mac/2014-01/os-x-tips-and-tricks.html)

## 更新日志

- 2017/01/14，增加 emacs、dash、`brew cask`、`httpstat`、`m-cli`
- 2017/06/03，增加 ffmpeg、asciiflow
