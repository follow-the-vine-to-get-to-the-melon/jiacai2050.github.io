title: 使用 ClojureScript 开发浏览器插件的过程与收获
date: 2017-11-22 16:23:34
tags: Clojure
categories: 编程语言
---

随着 Firefox 57 的到来，之前维护的一个浏览器插件 [gooreplacer](https://github.com/jiacai2050/gooreplacer) 必须升级到 WebExtensions 才能继续使用，看了下之前写的 JS 代码，毫无修改的冲动，怕改了这个地方，那个地方突然就 broken 了。因此，这次选择了 cljs，整体下来流程很顺利，除了迁移之前的功能，又加了更多功能，希望能成为最简单易用的重定向插件 :-)

闲话少说，下面的内容依次会介绍 cljs 的工作机制、开发环境，如何让 cljs 适配浏览器插件规范，以及重写 gooreplacer 时的一些经验。
本文的读者需要对 Clojure 语言、浏览器插件开发一般流程有基本了解，并且完成 ClojureScript 的 [Quick Start](https://clojurescript.org/guides/quick-start)。对于 Clojure，我目前在 sf 上有[一套视频课程](https://github.com/jiacai2050/learn_clojure.mp4)，供参考。

为了方便大家使用 cljs 开发插件，我整理了[一份模板](https://github.com/jiacai2050/browser-extenstion.cljs)，供大家参考。gooreplacer 完整代码在[这里](https://github.com/jiacai2050/gooreplacer)，技术栈为  ClojureScript + Reagent + Antd + React-Bootstrap。

## ClojureScript 工作机制

ClojureScript 是使用 Clojure 编写，最终编译生成 JS 代码的一个[编译器](http://blog.fogus.me/2012/04/25/the-clojurescript-compilation-pipeline/)，在编译过程中使用 [Google Closure Compiler](https://github.com/google/closure-compiler) 来优化 JS 代码、解决[模块化引用](https://github.com/google/closure-compiler/wiki/Managing-Dependencies)的问题。整体工作流程如下：

![cljs 编译流程](/images/clojure/cljs_compile.png)

Cljs 还提供 [与原生 JS 的交互](http://cljs.info/cheatsheet/)、[集成](https://clojurescript.org/reference/javascript-module-support)[第三方类库](https://clojurescript.org/news/2017-07-12-clojurescript-is-not-an-island-integrating-node-modules)的支持，所以，只要能用 JS 的地方，都能用 cljs，

## 开发环境准备

开发 cljs 的环境首选 [lein](https://github.com/technomancy/leiningen#installation) + [figwheel](https://github.com/bhauman/lein-figwheel)，figwheel 相比 [lein-cljsbuild](https://github.com/emezeske/lein-cljsbuild) 提供了热加载的功能，这一点对于开发 UI 很重要！

对于一般的 cljs 应用，基本都是用一个 script 标签去引用编译后的 js 文件，然后这个 js 文件再去加载其他依赖。比如：
```html
<html>
    <body>
        <script type="text/javascript" src="js/main.js"></script>
    </body>
</html>
```
js/main.js 是 project.clj 里面指定的输出文件，它会去加载其他所需文件，其内容大致如下：

```js
var CLOSURE_UNCOMPILED_DEFINES = {};
var CLOSURE_NO_DEPS = true;
if(typeof goog == "undefined") document.write('<script src="js/out/goog/base.js"></script>');
document.write('<script src="js/out/goog/deps.js"></script>');
document.write('<script src="js/out/cljs_deps.js"></script>');
document.write('<script>if (typeof goog == "undefined") console.warn("ClojureScript could not load :main, did you forget to specify :asset-path?");</script>');
document.write('<script>goog.require("process.env");</script>');

document.write("<script>if (typeof goog != \"undefined\") { goog.require(\"figwheel.connect.build_dev\"); }</script>");
document.write('<script>goog.require("hello_world.core");</script>');
```

### 消除 inline script

对于一般的 Web 项目，只引用这一个 js 文件就够了，但是对于浏览器插件来说，有一些问题，浏览器插件出于安全因素考虑，是[不让执行 incline script](https://developer.chrome.com/extensions/contentSecurityPolicy#relaxing-inline-script)，会报如下错误

![inline script error](https://img.alicdn.com/imgextra/i1/581166664/TB2xXZVeJnJ8KJjSszdXXaxuFXa_!!581166664.png)

为了去掉这些错误，手动加载 js/main.js 里面动态引入的文件，require 所需命名空间即可，修改后的 html 如下：

```html
<html>
    <body>
        <script src="js/out/goog/base.js"></script>
        <script src="js/out/cljs_deps.js"></script>
        <script src="js/init.js"></script>
    </body>
</html>
```

其中 init.js 内容为：

```js
// figwheel 用于热加载，这里的 build_dev 其实是 build_{build_id}，默认是 dev
goog.require("figwheel.connect.build_dev");
// 加载为 main 的命名空间
goog.require("hello_world.core");
```
这样就可以正常在浏览器插件环境中运行了。可以在 DevTools 中观察到所有引用的 js 文件

![动态加载的 JS 文件](https://img.alicdn.com/imgextra/i2/581166664/TB2buKhe3vD8KJjSsplXXaIEFXa_!!581166664.png) 

在左下角可以看到，总共有 92 个文件。

对于 background page/option page/popup page 这三处都可采用这种措施，但是 content script 没法指定 js 脚本加载顺序，可以想到的一种方式是：

```
"content_scripts": [{
  "matches": ["http://*/*", "https://*/*"],
  "run_at": "document_end",
  "js": ["content/js/out/goog/base.js", "content/js/out/cljs_deps.js", "content/init.js"]
}]
```
这里的 content 的目录与 manifest.json 在同一级目录。采用这种方式会报如下的错误

![content script 报错](https://img.alicdn.com/imgextra/i2/581166664/TB2vEaHbBLN8KJjSZPhXXc.spXa_!!581166664.png)

根据错误提示，可以看出是 base.js 再去动态引用其他 js 文件时，是以访问网站为相对路径开始的，因此也就找不到正确的 JS 文件了。

解决方法是设置 cljsbuild 的 `optimizations` 为 `:whitespace`，把所有文件打包到一个文件，然后引用这一个就可以了，[这个方法不是很完美](https://github.com/binaryage/chromex-sample/issues/2)，采用 whitespace 一方面使编译时间更长，在我机器上需要12s；另一方面是无法使用 figwheel，会报 A Figwheel build must have :compiler > :optimizations default to nil or set to :none 的错误，因此也就无法使用代码热加载的功能。

gooreplacer 里面只使用了 background page 与 option page，所以这个问题也就避免了。

### 区分 dev 与 release 模式

这里的 dev 是指正常的开发流程，release 是指开发完成，准备打包上传到应用商店的过程。

在 dev 过程中，推荐设置 cljsbuild 的 `optimizations` 为 none，以便得到最快的编译速度；
在 release 过程中，可以将其设置为 `advanced`，来压缩、优化 js 文件，以便最终的体积最小。

为了在两种模式中复用使用的图片、css 等资源，可采用了软链的来实现，resources 目录结构如下：

```
.
├── css
│   └── option.css
├── dev
│   ├── background
│   │   ├── index.html
│   │   └── init.js
│   ├── content
│   ├── manifest.json -> ../manifest.json
│   └── option
│       ├── css -> ../../css/
│       ├── images -> ../../images/
│       ├── index.html
│       └── init.js
├── images
│   ├── cljs.png
│   ├── cljs_16.png
│   ├── cljs_32.png
│   └── cljs_48.png
├── manifest.json
└── release
    ├── background
    │   ├── index.html
    │   └── js
    │       └── main.js
    ├── content
    │   └── js
    │       └── main.js
    ├── manifest.json -> ../manifest.json
    └── option
        ├── css -> ../../css/
        ├── images -> ../../images/
        ├── index.html
        └── js
            └── main.js
```

其次，为了方便开启多个 figwheel 实例来分别编译 background、option 里面的 js，定义了多个 lein 的 profiles，来指定不同环境下的配置，具体可参考 [模板的 project.clj](https://github.com/jiacai2050/browser-extenstion.cljs/blob/master/project.clj#L13) 文件。

### externs

在 optimizations 为 advanced 时，cljs 会充分借用 Google Closure Compiler 来压缩、混淆代码，会把变量名重命名为 a b c 之类的简写，为了不使 chrome/firefox 插件 API 里面的函数混淆，需要加载它们对应的 externs 文件，一般只需要这两个 [chrome_extensions.js](https://github.com/google/closure-compiler/blob/master/contrib/externs/chrome_extensions.js)、[chrome.js](https://github.com/google/closure-compiler/blob/master/contrib/externs/chrome.js)。

### 测试环境

cljs 自带的 test 功能比较搓，比较好用的是 [doo](https://github.com/bensu/doo)，为了使用它，需要先提前安装 [phantom](http://phantomjs.org/) 来提供 headless 环境，写好测试就可以执行了：

```
lein doo phantom {build-id} {watch-mode}
```

非常棒的一点是它也能支持热加载，所以在开发过程中我一直开着它。

### re-agent 

[re-agent](http://reagent-project.github.io/) 是对 React 的一个封装，使之符合 cljs 开发习惯。毫无夸张的说，对于非专业前端程序员来说，要想使用 React，cljs 比 jsx 是个更好的选择，[Hiccup-like](https://github.com/weavejester/hiccup) 的语法比 jsx 更紧凑，不用再去理睬 [webpack](https://webpack.js.org/
)，[babel](https://babeljs.io/) 等等层出不穷的 js 工具，更重要的一点是 immutable 在 cljs 中无处不在，re-agent 里面有自己维护状态的机制 atom，不在需要严格区分 React 里面的 props 与 state。

了解 re-agent 的最好方式就是从它[官网给出的示例](http://reagent-project.github.io/)开始，然后阅读 re-frame wiki 里面的 [Creating Reagent Components](https://github.com/Day8/re-frame/wiki/Creating-Reagent-Components)，了解三种不同的 form 的区别，98% gooreplacer 都在使用 form-2。如果对原理感兴趣，建议也把其他 wiki 看完。

re-agent 还有一点比较实用，提供了对 React 原生组件的转化函数：[adapt-react-class](http://nicolovaligi.com/boostrap-components-reagent-clojurescript.html)，使用非常简单：

```
(def Button (reagent/adapt-react-class (aget js/ReactBootstrap "Button")))

[:div
  [:h2 "A sample title"]
  [Button "with a button"]]
```
这样就不用担心 React 的类库不能在 cljs 中使用的问题了。

说到 re-agent，就不能不提到 [om.next](https://github.com/omcljs/om/wiki/Quick-Start-%28om.next%29)，这两个在 cljs 社区里面应该是最有名的 React wrapper，om.next 理念与使用难度均远高于 re-agent，初学者一般不推荐直接用 om.next。感兴趣的可以看看这两者之间的比较：

- [Why Re-frame instead of Om Next](https://purelyfunctional.tv/article/why-re-frame-instead-of-om-next/)，以及 [Reddit 上的讨论](https://www.reddit.com/r/Clojure/comments/6q0jhn/why_reframe_instead_of_om_next/)
- [A rant on Om Next](https://www.reddit.com/r/Clojure/comments/3vk58p/a_rant_on_om_next/)

## 坑

### [宏](https://clojurescript.org/about/differences#_macros)

cljs 里面加载宏的机制有别于 Clojure，一般需要单独把宏定义在一个文件里面，然后在 cljs 里面用`(:require-macros [my.macros :as my])` 这样的方式去引用，而且宏定义的文件名后缀必须是 clj 或 cljc，不能是 cljs，这一点坑了我好久。。。

由于宏编译与 cljs 编程在不同的时期，所以如果宏写错了，就需要把 repl 杀掉重启来把新的宏 feed 给 cljs，这点也比较痛苦，因为 repl 的启动速度实在是有些慢。这一点在 Clojure 里面虽然也存在，但是 Clojure 里面一般 repl 开了就不关了，直到电脑重启。

![我机器上启动的 repl 列表](https://img.alicdn.com/imgextra/i1/581166664/TB2iGyXbvjM8KJjSZFyXXXdzVXa_!!581166664.png)

### IDE

Clojure 里面采用 Emacs + Cider 的开发环境非常完美，但是到了 cljs 里面，开发流程没有那么平滑，总是有些磕磕绊绊，也给 cider [提了个 issue](https://github.com/clojure-emacs/cider/issues/2099)，貌似一直没人理，支持确实不好，不过有了 figwheel，在一定程度上能弥补这个缺陷。在 Emacs 里面配置 repl 可参考：

- https://cider.readthedocs.io/en/latest/up_and_running/#clojurescript-usage

Cider 默认会使用 rhino 作为 repl 求值环境，这个在开发浏览器插件时功能很有限，但是对于查看函数定义还是可以的。可以根据需要换成 figwheel。


## 总结

ClojureScript 可以算是 Clojure 语言的一个[杀手级](https://www.reddit.com/r/Clojure/comments/75apb2/does_clojure_have_a_killer_app/)[应用](https://groups.google.com/forum/#!topic/clojure/YCnG3rmOp5w)，React 使得后端程序员也能快速作出美观实用的界面。ClojureScript + React，用起来不能再开心啦！

JS 社区里面层出不穷的框架每次都让跃跃欲试的我望而却步，有了 cljs，算是把 Lisp 延伸到了更宽广的“领土”。最近看到这么一句话，与大家分享：

> 也许 Lisp 不是解决所有问题最合适的语言，但是它鼓励你设计一种最合适的语言来解决这个难题。

出处忘记了，大体是这么个意思。


## 参考

- [Chrome extension in ClojureScript](https://nvbn.github.io/2014/12/07/chrome-extension-clojurescript/)
- https://github.com/binaryage/chromex-sample