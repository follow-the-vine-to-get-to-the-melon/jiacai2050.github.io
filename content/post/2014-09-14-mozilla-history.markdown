---
date: 2014-09-14 00:14:52 +0800
tags:
- mozilla
title: Mozilla 前世今生
---

用过 Firefox 的同学多多少少都应该对 Mozilla 有些了解，Mozilla 作为一老牌软件公司，诞生了很多传奇性的故事和人物，本篇文章将带来读者重新回顾上个世纪九十年代发生的那些激荡人心的时刻。

Mozilla 这个词现在主要有三个含义:

1. 以开发 Firefox 浏览器出名的[软件套件](http://en.wikipedia.org/wiki/Mozilla)，除此之外，产品还有[Thunderbird](http://en.wikipedia.org/wiki/Mozilla_Thunderbird)、 [Firefox_Mobile](http://en.wikipedia.org/wiki/Firefox_Mobile)、[Firefox OS](http://en.wikipedia.org/wiki/Firefox_OS)
2. [Mozilla Foundation](http://en.wikipedia.org/wiki/Mozilla_Foundation)，成立于2003-7-15,一个支持并且领导开发Mozilla项目的非盈利组织
3. [Mozilla Corporation](http://en.wikipedia.org/wiki/Mozilla_Corporation)，成立于2005-8-3，是Mozilla Foundation的附属公司，创建Corporation的目的是解决Foundation税务相关的问题，其董事会成员很大部分都是Foundation的人员，这里不用区分这两个组织。

## Netscape
要想了解 Mozilla，不的不提上个世纪末的[ Netscape 公司](http://en.wikipedia.org/wiki/Netscape_Communications_Corporation)与[第一次浏览器大战](http://en.wikipedia.org/wiki/Browser_wars#First_browser_war),下面本文从1990年开始兴起的 [WWW](http://en.wikipedia.org/wiki/World_Wide_Web) 开始，简单说一下主流浏览器的发展过程。

WWW是一份[具有超链接的文档系统](http://www.w3.org/Proposal)，主要是为 Internet 设计，也就是我们现在看到的网页了。这份文档也提出了广为所知的URL、HTTP、HTML。[Tim Berners-Lee](http://en.wikipedia.org/wiki/Tim_Berners-Lee) 被认为是 WWW 之父，Tim 也设计出了世界上第一个浏览器 [WorldWideWeb](http://en.wikipedia.org/wiki/WorldWideWeb)。当然，发布的第一版是命令行操作的，如下图：
<img src="http://img04.taobaocdn.com/imgextra/i4/581166664/TB2N9C8apXXXXaoXXXXXXXXXXXX_!!581166664.gif" alt="WorldWideWeb"/>

Tim Berners-Lee 同时还开发了 Libwww 这个接口，用以构建浏览器，Line Mode Browser、ViolaWWW、Erwise、MidasWWW 和 Mac WWW等浏览器均已 Libwww 为基础。

第一个具有 GUI 且较为通用的浏览器是 [Erwise](http://en.wikipedia.org/wiki/Erwise)，之后一直到了1993年，[Marc Andreessen](http://en.wikipedia.org/wiki/Marc_Andreessen) 与他雇的全职程序员 [Eric Bina](http://en.wikipedia.org/wiki/Eric_Bina) 在 [UIUC](http://en.wikipedia.org/wiki/University_of_Illinois_at_Urbana-Champaign) 的 [NCSA](http://en.wikipedia.org/wiki/National_Center_for_Supercomputing_Applications) 开发出了 [Mosaic](http://en.wikipedia.org/wiki/Mosaic_%28web_browser%29)，Andreessen 在 NCSA 时结识 Time Berners-Lee。
当年 Andreessen 在 UIUC 毕业后去加州工作，在那里认识了 [Jim Clark](http://en.wikipedia.org/wiki/James_H._Clark), Clark 觉得 Mosaic 非常有商业价值，想与 Andreessen 合作开个软件公司，就这样，[Mosaic_Communications_Corporation](http://en.wikipedia.org/wiki/Mosaic_Communications_Corporation) 在1994年加州成立了。
UIUC 大学不满意他们的公司名字中有 Mosaic（有可能侵犯了商标权），最后公司名字改为 [Netscape Communications](http://en.wikipedia.org/wiki/Netscape)，旗舰(flagship)产品当然是 [Netscape_Navigator](http://en.wikipedia.org/wiki/Netscape_Navigator)，值得一提的是，Navigator 中没有使用 NCSA Mosaic 中的代码。

Netscape 在1995年8月9号，IPO非常成功，股票由开始的每股$14，到最后涨的$28，翻了一倍。谁都没想到 Netscape 会一夜暴富。Andreessen 也上了当年的[Time Magazine 封面](http://content.time.com/time/covers/0,16641,1101960219,00.html)。

## 浏览器大战
Netscape 的口号是"The Web is For Everyone"，并声明他们的目标是为不同浏览器平台提供一致的浏览体验。这一时期，也正是 Microsoft 在 PC 端发展迅猛，MS 意识到 Netscape 的浏览器对他们是个潜在的定时炸弹，因为用户可以在任何操作系统上使用他们浏览器，也就是说用户从 Windows 切换到其他操作系统，基本没有什么障碍。可见 Gates 真的是个有远见的企业家，在 1995 年就遇见到现在移动互联网的情景了，瘦客户端的兴起，BS 架构也逐渐替代 CS 架构。据某些不可考察的言论说：MS 的行政领导曾在1995年6月拜访过Netscape，建议分割市场，即 Windows 上由 MS 来开发浏览器，其他操作系统由 Netscape 开发操作系统（MS 当然否认了这些言论，否则就触犯了反垄断法）。

MS 在[Windows 95](http://en.wikipedia.org/wiki/Windows_95) [Plus Pack](http://en.wikipedia.org/wiki/Microsoft_Plus!)上发行了 [Internet Explorer](http://en.wikipedia.org/wiki/Internet_Explorer) 1.0，据曾经在 Spyglass 工作过的程序员[Eric Sink](http://en.wikipedia.org/wiki/Eric_Sink)[描述](http://www.ericsink.com/Browser_Wars.html)：IE不是以 NSCA Mosaic 为基础的，而是由 Spyglass 开发的 Mosaic 版本，而 Spyglass 的版本是基于 NSCA 的。

MS为了迅速抢占市场，使用了软件捆绑，即在发布 Windows 时预装 IE，而且是免费的，这样对 Netscape 来说无疑是重创，想想咱们中国的杀毒行业的 360，不也是靠免费把金山、江民、瑞星等等给打的不成样子了嘛。

MS 之后与 Netscape 展开了第一次浏览器大战，这两个公司都在通过不断研发新功能来争夺市场，但 IE 在财力、资源上更胜一筹，毕竟 MS 是靠卖 Windows 与 Office 挣钱的，而 Netscape 虽然也有其他产品，但浏览器是主要收入来源，无疑 Netscape 处于劣势。到 IE3.0 时，IE 的功能基本就与 Netscape Communicator 的相当了，到 IE4.0 Windows 已经比 Macintosh 系统更为稳定。同时， MS 开始研发 Netscape 其产品的替代品，像 [IIS](http://en.wikipedia.org/wiki/Internet_Information_Server),与 Windows NT 捆绑在一起。

[Netscape](http://en.wikipedia.org/wiki/Netscape)在此期间研发出来现在依然广为使用的[SSL](http://en.wikipedia.org/wiki/Transport_Layer_Security)与[JavaScript](http://en.wikipedia.org/wiki/JavaScript)。

Netscape直到1998年1月才向公众免费发放 Netscape Navigator，而 IE 与 IIS 则一直是免费与 Windows 操作系统捆绑售卖。

在 MS 与 Netscape 竞争时也有一些好玩的事，我这里说一件[mozilla stomps IE](http://home.snafu.de/tilman/mozilla/stomps.html)。

### Mozilla stomp IE
事情的简单经过就是 MS 在发布 IE4.0 时，把一个很大的 IE logo（而且貌似是由“重”金属打造而成）在 Netscape 公司前面的草坪上，而且是在深夜，这样第二天有可能会有一些记者看到并且发表出来。但是事情显然没有 MS 想的那么简单，Netscape 不仅在立刻察觉了这件事情，而且还把一个身高 7 英尺（大约2米多）Mozilla 的卡通像放到 IE logo 上，并且 Mozilla 手上拿这着个牌子，上面写着 `Netscape 72, Microsoft 18` ，这是当时他们的市场份额。
<img src="http://img01.taobaocdn.com/imgextra/i1/581166664/TB23EOTapXXXXarXpXXXXXXXXXX_!!581166664.jpg" alt="mozilla-stomps-ie"/>

### Open Source Mozilla
值得一提的是，在1998年1月，Netscape 发动了 [Mozilla](http://en.wikipedia.org/wiki/Mozilla)开源项目（哈哈，终于进入正题了），Mozilla 这个名字是继 Netscape Navigator 代码号之后，由 [Mosaic](http://en.wikipedia.org/wiki/Mosaic_%28web_browser%29) 与 [Godzilla](http://en.wikipedia.org/wiki/Godzilla) 合成而来。[Jamie Zawinski](http://en.wikipedia.org/wiki/Jamie_Zawinski)说是在一次 Netscape 员工会议上[想到这个名字的](http://www.davetitus.com/mozilla/)。

Mozilla 这个开源项目一开始的目的是为像 Netscape 这样的公司提供技术服务，而反过来 Netscape 这些公司可以把 [Mozilla 的代码](http://www-archive.mozilla.org/hacking/coding-introduction.html)商业化。

这里有个[纪录片《Code Rush》](http://v.youku.com/v_show/id_XNjA2NDI2MTUy.html)，记录的是1998年3月到1999年4月 Netscape 内部的一些真实情况，推荐读者观看。

很遗憾，Netscape 这么一个由 Hacker 组成的优秀公司也免不了被收购的命运，Netscape 与 AOL 的收购谈判自1998年12月24号开始，到1999年3月17号结束，收购后很多优秀的程序员也选择了离开。

### AOL 收购 Netscape
AOL 接管 Netscape 之后也发布过几次 Navigator 的版本，但到2003年7月，AOL开始缩减开发 Mozilla 的投入，也就在这时候，[mozilla.org](http://www.mozilla.org/en-US/press/mozilla-foundation.html)应时而出，宣布成立Mozilla Foundation，这之后，Mozilla Foundation 放弃了 Mozilla 套件(suite)，转而研发功能独立的应用，主要就是 [Firefox](http://en.wikipedia.org/wiki/Firefox)浏览器与 [Thunderbird](http://en.wikipedia.org/wiki/Mozilla_Thunderbird) 邮件客户端。

最近在移动互联网时代，Mozilla 推出了[Firefox OS](http://en.wikipedia.org/wiki/Firefox_OS)，基于 WEB 的认证系统[Mozilla Persona](http://en.wikipedia.org/wiki/Mozilla_Persona),以及为开发 HTML5 应用的 marketplace。但貌似市场份额都不高。

## 总结

本文基本上把围绕 Mozilla 的一些重要的事情都整理了一边，大部分资料都来自[wikipedia](http://en.wikipedia.org)，最后附上一张浏览器发展历程的图片，以飨读者。

![Timeline_of_web_browsers](/images/Timeline_of_web_browsers.svg "Timeline_of_web_browsers")
（图比较大，可点击查看原图）

### Code Rush
纪录片[《Code Rush》](http://www.imdb.com/title/tt0499004/)截图

<img src="http://img04.taobaocdn.com/imgextra/i4/581166664/TB2_jO2apXXXXcHXXXXXXXXXXXX_!!581166664.png" alt=" Brendan-Eich"/>
没错，就是[Eich 这家伙](http://en.wikipedia.org/wiki/Brendan_Eich)，用了10天时间开发出来JavaScript，其他一开始他是想把 Scheme 移植到 Navigator 上的，但公司管理层想借当时大红大紫的 Java 的光，于是语法既想 Scheme 又想 Java 的 JS 就这么诞生了。

<img src="http://img04.taobaocdn.com/imgextra/i4/581166664/TB2L4eSapXXXXbtXpXXXXXXXXXX_!!581166664.png" alt=" CEO-of-mozilla"/>
[Jim Barksdale](http://en.wikipedia.org/wiki/Jim_Barksdale) 在纪录片第 15 分钟在审判微软垄断的法案时说的一段话：
> "How many of you use Intel-based PCs in this audience, not Macintoshes?" Most people in the room raised their hands. "Of that group who use PCs? How many of you use a PC without Microsoft's operating system?". All of the hands went down. He said to the Senate panel, "Gentlemen, that is a monopoly."

<img src="http://img03.taobaocdn.com/imgextra/i3/581166664/TB2d4K0apXXXXX4XpXXXXXXXXXX_!!581166664.png" alt="Tara-Hernandez"/>
[Tara-Hernandez](http://www.linkedin.com/pub/tara-hernandez/3/b26/755)这是当时的测试工程师吧，她负责 Navigator 上线前的最后检查。

<img src="http://img02.taobaocdn.com/imgextra/i2/581166664/TB28GG4apXXXXb_XXXXXXXXXXXX_!!581166664.png" alt=" Jamie-Zawinski"/>
<img src="http://img03.taobaocdn.com/imgextra/i3/581166664/TB2w7eVapXXXXacXpXXXXXXXXXX_!!581166664.png" alt=" Jamie-Zawinski自由开源软件布道师"/>
[Jamie-Zawinski](http://en.wikipedia.org/wiki/Jamie_Zawinski)发型好帅，是个LISP程序员，[xemacs](http://www.xemacs.org/)、[xscreensaver](http://www.jwz.org/xscreensaver/)作者，[个人博客](http://www.jwz.org)

<img src="http://img02.taobaocdn.com/imgextra/i2/581166664/TB20A96apXXXXasXXXXXXXXXXXX_!!581166664.png" alt="Jim-Roskind"/>
哥，Chrome 快是快，但是你知道他有多占内存吗！[个人博客](http://www.roskind.com/)

<img src="http://img04.taobaocdn.com/imgextra/i4/581166664/TB2n.S1apXXXXXfXpXXXXXXXXXX_!!581166664.png" alt=" Scott-Collins"/>
比较低调的胖子，网上就找到这么[一篇关于他的采访](http://arstechnica.com/information-technology/2004/06/collins-interview/)。

<img src="http://img03.taobaocdn.com/imgextra/i3/581166664/TB2oB5QapXXXXbYXpXXXXXXXXXX_!!581166664.png" alt=" Stuart-Parmenter"/>
<img src="http://img02.taobaocdn.com/imgextra/i2/581166664/TB2e090apXXXXXxXpXXXXXXXXXX_!!581166664.png" alt=" Stuart-Pamener2"/>
又是一个牛叉的小胖子，[Mozilla 官方博客](https://blog.mozilla.org/blog/author/pavlovmozilla-com/)，创办 [rise](http://www.rise.us/)，并且是CTO。


好了，纪录片截图就这些，看完后我觉得你也一定会忍不住看一遍吧。Go ahead, buddy!
