---
date: 2014-11-23 20:40:07
tags:
- 最佳实践
title: MacBook 最佳实践
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

可以根据需要，配置国内源：
- 中科大，https://lug.ustc.edu.cn/wiki/mirrors/help/brew.git
- 清华，https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/

### 文本编辑器 [VSCode](https://code.visualstudio.com/)

```
# 安装命令
brew cask install visual-studio-code
```
新时代的文本编辑器，功能和 Atom/Sublime 差不多，但是不会出现卡顿现象，而且官方提供了 [Sublime Text Keymap](https://github.com/Microsoft/vscode-sublime-keybindings) 插件，如果之前熟悉 Sublime，推荐安装。下面是我非常依赖的快捷键：

- Multiple Selection: `Control+Command+G`（在 Linux/Windows 下，是 Alt+F3）
- 选中多行 `Shift+Command+L`
- 多行合并为一行`Command+J`


### 神之编辑器 [Emacs](https://www.emacswiki.org/emacs?interface=en)

```
# 安装命令
brew install --with-cocoa --srgb emacs
brew install sbcl # 顺便把 common lisp 也装上
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
Mac自带的终端不是很强，程序员们需要一个强劲的终端来工作，于是有了 iTerm2。需要设置一项：Left Option act as +Esc（Preferences-->Profiles-->Keys），这样 Option 就可以用作 Meta 键了。
- `Cmd + D` 垂直分屏 
- `Cmd + Shift + D` 水平分屏 
- `Cmd + T` 开多个Tab 
- `Cmd + 数字` 在多个Tab之间进行切换 
- `Option + F/B（向前、向后）` 按字移动。Bash Shell 光标默认按照 Emacs 风格移动，也可改为 VIM，可参考[Modifying the Bash Shell with the set Command](http://www.hypexr.org/bash_tutorial.php#set)。 
- `Ctrl + r` 搜索历史命令
- `!!` 执行上条命令
- `Ctrl+x Ctrl+e` 调用[默认编辑器去编辑一个特别长的命令](http://www.commandlinefu.com/commands/view/1446/rapidly-invoke-an-editor-to-write-a-long-complex-or-tricky-command)


当然，说到了 iTerm2，不得不提到终端复用软件 [tmux](https://tmux.github.io/)，tmux 默认配置文件在 Mac 上很别扭，你可以参考我这里的[配置文件](https://github.com/jiacai2050/conf/blob/master/.tmux.conf)，这样 tmux 就可以像 vim 一样实现各种分屏的效果了。如果你还不知道 tmux 为何物，强烈推荐你看这个13分钟的[视频](http://pan.baidu.com/s/1gdLZzB9)，绝对物超所值，感谢 [happypeter](http://haoduoshipin.com/u/happypeter) 的分享。

我现在用的主题是：[Tomorrow Night](https://github.com/chriskempson/tomorrow-theme/blob/master/iTerm2/Tomorrow%20Night.itermcolors)。

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

### ~/.ssh/config

在 macOS/OS X 截止到 Yosemite，ssh-agent 会一直记住 `ssh-add -K` 添加的 key，即使重启 keychain，ssh-agent 也会自动去读取保存在 keychain 中的密码（passphrase）。但在 Sierra 中，重启 keychain 后，ssh-agent 就不会去读取了。Apple 开发者也对这一现象作出[回应](https://openradar.appspot.com/27348363)：

> That’s expected. We re-aligned our behavior with the mainstream OpenSSH in this area. 

解决办法也很简单，将`ssh-add -A` 放到 `~/.bashrc` 里面就可以了。除了这种方式，还可以在`~/.ssh/config`里面加入如下配置：
```
Host * (asterisk for all hosts or add specific host)
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile <key> (e.g. ~/.ssh/userKey)
```
参考：
- [Saving SSH keys in macOS Sierra keychain](https://github.com/jirsbek/SSH-keys-in-macOS-Sierra-keychain)

除此之外，对于 OpenSSH 4.0 以及之后的版本，引入一新功能 ControlMaster，可以复用之前已经登录的连接，建议开启：
```
Host *
  ControlMaster auto
  ControlPath ~/.ssh/master-%r@%h:%p
  ControlPersist 60m
```
参考：
- [Accelerating OpenSSH connections with ControlMaster](https://www.linux.com/news/accelerating-openssh-connections-controlmaster)
- [https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Multiplexing](OpenSSH/Cookbook/Multiplexing)

### Java

```
# 安装命令
brew cask install java
brew install maven
brew cask install intellij-idea-ce  # IDE，不要告诉我你还在用 eclipse
```
通过`brew cask`安装后，可以通过执行`/usr/libexec/java_home`这个命令来获取JAVA_HOME
```
export JAVA_HOME="$(/usr/libexec/java_home)"
```

### Docker

```
# 安装命令
brew cask install docker
```
国内访问 Docker Hub 有时会遇到困难，最好可以配置[镜像加速器](https://yeasy.gitbooks.io/docker_practice/install/mirror.html)。

### 数据库 GUI 客户端

```
# 安装命令
brew cask install sequel-pro # mysql
brew cask install robo-3t    # mongodb
brew cask install rdm        # redis
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
为了让终端可以使用代理，需要将 http(s) 转为 socks 流量。ss 官方推荐的是 [proxychains](https://github.com/shadowsocks/shadowsocks/wiki/Using-Shadowsocks-with-Command-Line-Tools)，但是在OS X 10.11 以后引入了 [SIP安全机制](https://developer.apple.com/library/content/releasenotes/MacOSX/WhatsNewInOSX/Articles/MacOSX10_11.html)，导致无法直接使用，关闭 SIP 貌似也不可取，可以选用 [privoxy](https://www.privoxy.org/) 来替代 proxychains。（[参考](https://tech.jandou.com/to-accelerate-the-terminal.html)）
```
brew install privoxy
# privoxy 使用 8118 端口， ss 使用 1080
echo 'listen-address 0.0.0.0:8118\nforward-socks5 / localhost:1080 .' >> /usr/local/etc/privoxy/config
# 测试，查看 8118 有没有在监听， netstat -an | grep 8118
/usr/local/sbin/privoxy /usr/local/etc/privoxy/config
# 开机启动
brew services start privoxy
```
经过上面这几步 `http(s)->socks5` 就完成，下面只需要让终端走这个代理即可：
```
export http_proxy='http://localhost:8118'
export https_proxy='http://localhost:8118'

# 可以将以下函数放入 ~/.bashrc 中，方便开启/关闭代理
function proxy_off(){
    unset http_proxy
    unset https_proxy
    echo -e "已关闭代理"
}
function proxy_on() {
    export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"
    export http_proxy="http://127.0.0.1:8118"
    export https_proxy=$http_proxy
    echo -e "已开启代理"
}
```

### 虚拟机 [Virtualbox](https://www.virtualbox.org/)

```
# 安装命令
brew cask install virtualbox
brew cask install vagrant   # 虚拟机管理工具，方便命令行操作
```

在天朝，很多网站是只支持 IE 的，Mac 下的 Firefox, Chrome, Safari 这时候都显得心有力而不足了，而且很多软件也只有 Windows 版，所以装个虚拟机是非常有必要的。 Virtualbox 是我自用 Ubuntu 以来一直用的虚拟机，开源免费。

[vagrant](https://github.com/hashicorp/vagrant) 是一款非常简单且使用的虚拟机命令行工具，支持市面上主流虚拟机，当然包括 VBox，通过下面的命令即可安装一个干净的 Ubuntu 环境：
```
vagrant init hashicorp/precise32
vagrant up
```
为了方便今后操作，我自己制作了一个基于 debian8 的 box，安装上了 [Clojure 开发环境](https://app.vagrantup.com/jiacai2050/boxes/debian8)，一键即可安装。

![Virtualbox](https://img.alicdn.com/imgextra/i4/581166664/TB2aVGdcNlmpuFjSZPfXXc9iXXa_!!581166664.png)


### 系统快捷键

| 功能| 快捷键 |
| ---------|--------- |
| 查看桌面|`F11` |
| 查看Dashboard|`F12` |
| HOME|`Command + <-` |
| END|`Command + ->` |
| 锁屏|`Shift + Control + 电源键` （Windows 下为`Win+L`） |
| 强制关闭程序|`Command + Option + esc`（Windows 下为`Ctrl+Alt+Delete`） |
| [在同一应用不同窗口切换](https://apple.stackexchange.com/questions/193937/shortcut-for-toggling-between-different-windows-of-same-app)|`Command + ~` |
| [Finder 里面剪切](http://apple.stackexchange.com/questions/12391/why-is-it-not-possible-to-use-the-cut-command-to-manipulate-a-file-in-the-find)|`Cmd + Option + V` |

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
Chrome 默认会按照一个 Update 程序，在 `~/Library/Google/GoogleSoftwareUpdate`，可以执行[下面命令删除](https://superuser.com/a/1077420)：
```
cd /Users/liujiacai/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Resources/GoogleSoftwareUpdateAgent.app/Contents/Resources

./ksinstall --nuke
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

### Calibre mobi 转化器

如果你有 Kinder 阅读器，那么这个应该适合你！
```
# 安装命令
brew cask install calibre

==> Installing Cask calibre
==> Moving App 'calibre.app' to '/Applications/calibre.app'.
==> Linking Binary 'calibre' to '/usr/local/bin/calibre'.
==> Linking Binary 'calibre-complete' to '/usr/local/bin/calibre-complete'.
==> Linking Binary 'calibre-customize' to '/usr/local/bin/calibre-customize'.
==> Linking Binary 'calibre-debug' to '/usr/local/bin/calibre-debug'.
==> Linking Binary 'calibre-parallel' to '/usr/local/bin/calibre-parallel'.
==> Linking Binary 'calibre-server' to '/usr/local/bin/calibre-server'.
==> Linking Binary 'calibre-smtp' to '/usr/local/bin/calibre-smtp'.
==> Linking Binary 'calibredb' to '/usr/local/bin/calibredb'.
==> Linking Binary 'ebook-convert' to '/usr/local/bin/ebook-convert'.
==> Linking Binary 'ebook-device' to '/usr/local/bin/ebook-device'.
==> Linking Binary 'ebook-edit' to '/usr/local/bin/ebook-edit'.
==> Linking Binary 'ebook-meta' to '/usr/local/bin/ebook-meta'.
==> Linking Binary 'ebook-polish' to '/usr/local/bin/ebook-polish'.
==> Linking Binary 'ebook-viewer' to '/usr/local/bin/ebook-viewer'.
==> Linking Binary 'fetch-ebook-metadata' to '/usr/local/bin/fetch-ebook-metadata'.
==> Linking Binary 'lrf2lrs' to '/usr/local/bin/lrf2lrs'.
==> Linking Binary 'lrfviewer' to '/usr/local/bin/lrfviewer'.
==> Linking Binary 'lrs2lrf' to '/usr/local/bin/lrs2lrf'.
==> Linking Binary 'markdown-calibre' to '/usr/local/bin/markdown-calibre'.
==> Linking Binary 'web2disk' to '/usr/local/bin/web2disk'.
```


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
- 2017/07/06，修改 iTerm2 部分，增加 docker
