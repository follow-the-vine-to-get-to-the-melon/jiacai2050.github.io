title: 让firefox与chrome一样快
date: 2014-11-08 20:23:53 +0800
tags: mozilla
categories: story
---

在如今这个Web时代，浏览器可以说是仅次于操作系统的软件了，各种应用都可以放到云端、移动端随时随地的使用，[HTML5标准](http://www.w3.org/TR/html5/)的最终版正式[发布](http://www.w3.org/blog/news/archives/4167)， 再次为使用Web技术开发跨平台应用奠定了基石。

HTML5现在是有统一标准了，但用户使用的浏览器可是五花八门了，身为程序员，IE可以忽略，一般linux下就是chrome与firefox，chrome快是快，就是太吃内存，所以在一些”老机器“上不敢用，下面就剩下firefox了，其实我自从看了《Code Rush》这个记录片以后，十分崇拜上个世纪有那么一群极客聚在一起，开发了很多促进了互联网发展的技术，以前我也写的文章[《Mozilla前世今生》](/blog/2014/09/14/mozilla-history/)说过，这里就不在多说了。

但是不得不说的是firefox确实比chrome慢，有时候感觉chrome只需要一眨眼就能打开的网页，而firefox却要等上那么3、4秒，我真是无法忍受了。趁着这几天开发[gooreplacer](/gooreplacer/)这个插件，又深入了解了下firefox一些工作机制，发现我们可以在不升级内存的情况下加速firefox打开网页的时间，我自己亲自实验了下，速度确实提了不少，现与大家分享之。

firefox的配置我们一般可以在”工具 -> 选项“菜单中找到，但是还有一些配置项并不在这里，在firefox中地址栏输入about:config，回车，进入时应该会有个警告，忽略之，之后就应该能看到很多如下的配置项了。

<img src="http://img04.taobaocdn.com/imgextra/i4/581166664/TB2L8ImaVXXXXcqXpXXXXXXXXXX_!!581166664.png" alt=" about-config截图"/>

这些配置项定义了很多浏览器的的默认参数，但不是全部，我们可以根据实际情况自己添加。使用过滤我们能够很容易地找到感兴趣的配置项。这里的配置项类型分三种：integer、boolean、string。这些配置项保存在本地一个叫prefs.js的文件中，prefs.js根据操作系统不同位置不同：
- Linxu下，在`~/.mozilla/firefox/<profile ID>.default/`中
- WinXP下，在`C:\Documents and Settings\<username>\Application Data\Mozilla\Firefox\Profiles\<profile ID>.default\`中

需要说明一点的是，我们最好不要直接修改这个文件，如果非修改不可，**最好事先备份一份**（如果你想找到你机器上prefs.js文件在哪里，使用搜索功能就好了。）

下面重点说一些能够改善用户体验的配置项。

##渲染(render)相关

###减少渲染延迟
创建一个整型配置项`nglayout.initialpaint.delay`，这个配置定义了firefox在下载完HTML、CSS等资源后，到真正开始渲染的时间间隔，如果不设置，默认为250毫秒。如果设置为0,就能在使浏览器立即渲染了。

###减少reflow次数
当firefox加载一个网页时，它会在加载过程中，根据加载的数据，不间断的对页面进行[reflow](http://www.blueidea.com/tech/web/2007/4950.asp)。创建一个整型配置项`content.notify.interval`，它能够控制两次reflow的间隔，它的单位是微秒，如果不设置，默认为120000（即0.12秒）。如果reflow次数过多，就会使得浏览器反应迟钝了，所以我们应该把这个值设的大些，500000（即0.5秒）或1000000（即1秒）都可以。
需要注意一点的是，如果要是`content.notify.interval`这个配置项生效，需要先创建一个布尔型的配置项`content.notify.ontimer`，并且设为true。

###控制”不响应“时间
在渲染一个网页时，firefox会间歇性地加速渲染过程，mozilla称之为tokenizing。但是这个加速是有代价的，在tokenizing过程中，浏览器不能响应用户的输入，tokenizing的时间长度是由一个整型配置项`content.max.tokenizing.time`控制的。一般来说，把这个配置项的值设为`content.notify.interval`值或者它的倍数。如果`content.max.tokenizing.time`的值小于`content.notify.interval`的值，浏览器就会因为过多响应用户输入而导致整个加载过程变慢。
需要注意一点的是，如果要是`content.max.tokenizing.time`这个配置项生效，需要先创建两个个布尔型的配置项`content.notify.ontimer`与`content.interrupt.parsing`，并且都设为true。

###控制”高响应“时间
在渲染一个页面时，用户如果进行了某些操作（比如向下滚动）时，firefox会预留更多的时间来响应用户的输入，这里的时间间隔是由一个整型配置项`content.switch.threshold`设置的。它的值一般是`content.notify.interval`的三倍，  但是如果我们把这个值调小些，这时firefox虽然对用户的响应不会那么及时，但是会明显加速页面的渲染过程。
如果你倾向于在网页加载完成后在进行操作（比如向下滚动），可以把`content.max.tokenizing.time`值设的大些，`content.switch.threshold`值设的小些；

##网络(network)相关

### pipelining
把`network.http.pipelining`与`network.http.proxy.pipelining`设置为true
`network.http.pipelining.maxrequests`可根据实际情况设置，我电脑上是默认值32.

### dns
把`network.dns.disableIPv6`设为true，因为现在的网站都是ipv4,没听过那个网站是v6的。
`network.dnsCacheEntries`，这个设置firefox最多保存dns的数目，可根据个人情况设置，我电脑上chrome大约缓存了1500多个，这是chrome快的原因之一。
`network.dnsCacheExpiration`，dns的有限期限，单位为秒，可根据个人情况设置。

## 总结

我这里只是介绍了很小一部分配置项，更多的配置项大家可以在[mozillazine](http://kb.mozillazine.org/Category:Preferences)中找到，到时大家根据自己的需求修改就好了。
我发现firefox比chrome慢的原因是，很多配置项firefox设置的比较保守，这么做无非是照顾一些“老机器”了，把更多的选择权交给了用户；chrome的默认配置就比较简单暴力了，光是separate-process-per-tab这个就把大家电脑的内存占用了大半。Firefox的[E10 project也称Electrolysis](https://wiki.mozilla.org/Electrolysis)其实也对这项技术提供了支持，但是只在[nightly](http://nightly.mozilla.org/)版本上可用，因为这个技术会导致一些[插件无法使用](https://developer.mozilla.org/en-US/Add-ons/Working_with_multiprocess_Firefox)，所有没有集成到正式版上，firefox更看重软件的兼容性。
其实chrome自2008年9月发布，在很短的时间内就超过了firefox的市场份额，究其原因就是顺应了大家对“用户体验”的追求，硬件升级现在很简单，买个内存条也很便宜；而从上个世纪走过来的firefox，相比之下显得保守了，这也可以理解，毕竟早期大家的电脑配置都不高。大家有兴趣的可以去看看[Firefox Release Notes](https://www.mozilla.org/en-US/firefox/releases/)了解Firefox的版本更新信息。

Happy Hacking！

## 参考

- [Hacking Firefox: The secrets of about:config](http://www.computerworld.com/article/2541429/networking/hacking-firefox--the-secrets-of-about-config.html)
- [Making Firefox as Fast as Chrome](http://wikimatze.de/making-firefox-as-fast-as-chrome/)
- [Chrome_vs_Firefox](https://www.wikivs.com/wiki/Chrome_vs_Firefox)
- [Why-hasnt-firefox-adopted-tab-as-a-separate-process-like-chrome](http://www.quora.com/Mozilla-Firefox-Why-hasnt-firefox-adopted-a-chrome-like-model-of-having-each-tab-as-a-separate-process)
- [Firefox memory benchmark](https://areweslimyet.com/)