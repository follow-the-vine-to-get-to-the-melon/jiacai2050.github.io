title: Clojure Web 开发-- Ring 使用指南
date: 2017-04-02 23:56:30
tags: Clojure
categories: Web
---


在 Clojure 众多的 Web 框架中，[Ring](https://github.com/ring-clojure/ring) 以其简单统一的 HTTP 抽象模型脱颖而出。Ring 充分体现了函数式编程的思想——通过一系列函数的组合形成了一个易于理解、扩展的 HTTP 处理链。

本篇文章首先介绍 Ring 核心概念及其实现原理，然后介绍如何基于 Ring + [Compojure](https://github.com/weavejester/compojure) 实现一 RESTful 服务。

## [Ring SPEC](https://github.com/ring-clojure/ring/blob/master/SPEC)

Ring 规范里面有如下5个核心概念：

1. handlers，应用逻辑处理的主要单元，由一个普通的 Clojure 函数实现
2. middleware，为 handler 增加额外功能
3. adapter，将 HTTP 请求转为 Clojure 里的 map，将 Clojure 里的 map 转为 HTTP 相应
4. request map，HTTP 请求的 map 表示
5. response map，HTTP 相应的 map 表示

这5个组件的关系可用下图表示（By [Ring 作者](https://github.com/ring-clojure/ring-defaults/issues/20)）：
```
 +---------------+
 |  Middleware   |
 |  +---------+  |             +---------+      +--------+
 |  |         |<-- request ----|         |      |        |
 |  | Handler |  |             | Adapter |<---->| Client |
 |  |         |--- response -->|         |      |        |
 |  +---------+  |             +---------+      +--------+
 +---------------+
```

### Hello World

```
(ns learn-ring.core
  (:require [ring.adapter.jetty :refer [run-jetty]]))

(defn handler [req]
  {:headers {}
   :status 200
   :body "Hello World"})

(defn middleware [handler]
  "Audit a log per request"
  (fn [req]
    (println (:uri req))
    (handler req)))

(def app
  (-> handler
      middleware))

(defn -main [& _]
  (run-jetty app {:port 3000}))
```
运行上面的程序，就可以启动一 Web 应用，然后在浏览器访问就可以返回`Hello World`，同时在控制台里面会打印出请求的 uri。

`run-jetty` 是 Ring 提供的基于 jetty 的 adapter，方便开发测试。其主要功能是两个转换：

1. `HttpServletRequest` ---> `request map`
2. `response map` ---> `HttpServletResponse`

```
;; ring.adapter.jetty
(defn- ^AbstractHandler proxy-handler [handler]
  (proxy [AbstractHandler] []
    (handle [_ ^Request base-request request response]
      (let [request-map  (servlet/build-request-map request)
            response-map (handler request-map)]
        (servlet/update-servlet-response response response-map)
        (.setHandled base-request true)))))

;; ring.util.servlet

;; HttpServletRequest --> request map

(defn build-request-map
  "Create the request map from the HttpServletRequest object."
  [^HttpServletRequest request]
  {:server-port        (.getServerPort request)
   :server-name        (.getServerName request)
   :remote-addr        (.getRemoteAddr request)
   :uri                (.getRequestURI request)
   :query-string       (.getQueryString request)
   :scheme             (keyword (.getScheme request))
   :request-method     (keyword (.toLowerCase (.getMethod request) Locale/ENGLISH))
   :protocol           (.getProtocol request)
   :headers            (get-headers request)
   :content-type       (.getContentType request)
   :content-length     (get-content-length request)
   :character-encoding (.getCharacterEncoding request)
   :ssl-client-cert    (get-client-cert request)
   :body               (.getInputStream request)})

;; response map --> HttpServletResponse

(defn update-servlet-response
  "Update the HttpServletResponse using a response map. Takes an optional
  AsyncContext."
  ([response response-map]
   (update-servlet-response response nil response-map))
  ([^HttpServletResponse response context response-map]
   (let [{:keys [status headers body]} response-map]
     (when (nil? response)
       (throw (NullPointerException. "HttpServletResponse is nil")))
     (when (nil? response-map)
       (throw (NullPointerException. "Response map is nil")))
     (when status
       (.setStatus response status))
     (set-headers response headers)
     (let [output-stream (make-output-stream response context)]
       (protocols/write-body-to-stream body response-map output-stream)))))
```

## [Middleware](https://github.com/ring-clojure/ring/wiki/Middleware-Patterns)

Ring 里面采用 Middleware 模式去扩展 handler 的功能，这其实是函数式编程中常用的技巧，用高阶函数去组合函数，实现更复杂的功能。在 Clojure 里面，函数组合更常见的是用 `comp`，比如
```
((comp #(* % 2) inc) 1)
;; 4
```
这对一些简单的函数非常合适，但是如果逻辑比较复杂，Middleware 模式就比较合适了。例如可以进行一些逻辑判断决定是否需要调用某函数：
```
(defn middleware-comp [handler]
  (fn [x]
    (if (zero? 0)
      (handler (inc x))
      (handler x))))

((-> #(* 2 %)
      middleware-comp) 1)
;; 4
((-> #(* 2 %)
      middleware-comp) 0)
;; 2
```

虽然 Middleware 使用非常方便，但是有一点需要注意：多个 middleware 组合的顺序。后面在讲解 RESTful 示例时会演示不同顺序的 middleware 对请求的影响。

Middleware 这一模式在函数式编程中非常常见，Clojure 生态里面新的构建工具 [boot-clj](https://github.com/boot-clj/boot) 里面的 task 也是通过这种模式组合的。

```
$ cat build.boot
(deftask inc-if-zero-else-dec
  [n number NUM int "number to test"]
  (fn [handler]
    (fn [fileset]
      (if (zero? number)
        (handler (merge fileset {:number (inc number)}))
        (handler (merge fileset {:number (dec number)}))))))

(deftask printer
  []
  (fn [handler]
    (fn [fileset]
      (println (str "number is " (:number fileset)))
      fileset)))

$ boot inc-if-zero-else-dec -n 0    printer
number is 1
$ boot inc-if-zero-else-dec -n 1    printer
number is 0
```

## RESTful 实战

由于 Ring 只是提供了一个 Web 服务最基本的抽象功能，很多其他功能，像 url 路由规则，参数解析等均需通过其他模块实现。[Compojure](https://github.com/weavejester/compojure) 是 Ring 生态里面默认的路由器，同样短小精悍，功能强大。基本用法如下：

```
(def handlers
  (routes
   (GET "/" [] "Hello World")
   (GET "/about" [] "about page")
   (route/not-found "Page not found!")))

```
使用这里的 handlers 代替上面 Hello World 的示例中的 handler 即可得到一个具有2条路由规则的 Web 应用，同时针对其他路由返回 `Page not found!`。

Compojure 里面使用了大量宏来简化路由的定义，像上面例子中的`GET`、`not-found`等。Compojure 底层使用 [clout](https://github.com/weavejester/clout) 这个库实现，而 clout 本身是基于一个 parser generator（[instaparse](https://github.com/Engelberg/instaparse)） 定义的“路由”领域特定语言。[核心规则](https://github.com/weavejester/clout/blob/master/src/clout/core.clj#L56)如下：
```
(def ^:private route-parser
  (insta/parser
   "route    = (scheme / part) part*
    scheme   = #'(https?:)?//'
    <part>   = literal | escaped | wildcard | param
    literal  = #'(:[^\\p{L}_*{}\\\\]|[^:*{}\\\\])+'
    escaped  = #'\\\\.'
    wildcard = '*'
    param    = key pattern?
    key      = <':'> #'([\\p{L}_][\\p{L}_0-9-]*)'
    pattern  = '{' (#'(?:[^{}\\\\]|\\\\.)+' | pattern)* '}'"
   :no-slurp true))
```

Compojure 中路由匹配的方式也非常巧妙，这里详细介绍一下。

### Compojure 路由分发
Compojure 通过 routes 把一系列 handler 封装起来，其内部调用 routing 方法找到正确的 handler。这两个方法代码非常简洁：
```
(defn routing
  "Apply a list of routes to a Ring request map."
  [request & handlers]
  (some #(% request) handlers))

(defn routes
  "Create a Ring handler by combining several handlers into one."
  [& handlers]
  #(apply routing % handlers))
```

routing 里面通过调用 `some` 函数返回第一个非 nil 调用，这样就解决了路由匹配的问题。由这个例子可以看出 Clojure 语言的表达力。

在使用 `GET` 等这类宏定义 handler 时，会调用`wrap-route-matches` 来包装真正的处理逻辑，逻辑如下：

```
(defn- wrap-route-matches [handler method path]
  (fn [request]
     (if (method-matches? request method)
       (if-let [request (route-request request path)]
         (-> (handler request)
             (head-response request method))))))
```
这里看到只有在 url 与 http method 均匹配时，才会去调用 handler 处理 http 请求，其他情况直接返回 nil，这与前面讲的 some 联合起来就形成了完整的路由功能。

由于 `routes` 的返回值与 handler 一样，是一个接受 request map 返回 response map 的函数，所以可以像堆积木一样进行任意组合，实现类似于 [Flask 中 blueprints](http://flask.pocoo.org/docs/0.12/blueprints/) 的模块化功能。例如：

```
;; cat student.clj
(ns demo.student
  (:require [compojure.core :refer [GET POST defroutes context]])

(defroutes handlers
  (context "/student" []
    (GET "/" [] "student index")))

;;cat demo.teacher
(ns demo.teacher
  (:require [compojure.core :refer [GET POST defroutes context]])

(defroutes handlers
  (context "/teacher" []
    (GET "/" [] "teacher index")))

;; cat demo.core.clj
(ns demo.core
  (:require [demo.student :as stu]
            [demo.teacher :as tea])


;; core 里面进行 handler 的组合
(defroutes handlers
  (GET "/" [] "index")
  (stu/handlers)
  (tea/handlers))
```

### Middleware 功能扩展

#### 参数解析
Compojure 解决了路由问题，参数获取是通过定制不能的 middleware 实现的，`compojure.handler` 命名空间提供了常用的 middleware 的组合，针对 RESTful 可以使用 [api](https://github.com/weavejester/compojure/blob/master/src/compojure/handler.clj#L22) 这个组合函数，它会把 QueryString 中的参数解析到 request map 中的`:query-params` key 中，表单中的参数解析到 request map 中的 `:form-params`。
```
(def app
  (-> handlers
      handler/api))
```

#### JSON 序列化
由于 RESTful 服务中，请求的数据与返回的数据通常都是 JSON 格式，所以需要增加两个额外的功能来实现 JSON 的序列化。
```
;; 首先引用 ring.middleware.json

(def app
  (-> handlers
      wrap-json-response
      wrap-json-body
      handler/api))
```

#### 纪录请求时间

通常，我们需要纪录每个请求的处理时间，这很简单，实现个 `record-response-time` 即可：

```
(defn record-response-time [handler]
  (fn [req]
    (let [start-date (System/currentTimeMillis)]
      (handler req)
      (let [res-time (- (System/currentTimeMillis) start-date)]
        (println (format  "%s took %d ms" (:uri req) res-time))))))

(def app
  (-> handlers
      wrap-json-response
      wrap-json-body
      handler/api
      record-response-time))
```
需要注意的是 `record-response-time` 需要放在 middleware 最外层，这样它才能纪录一个请求经过所有 middleware + handler 处理的时间。

#### 封装异常
其次，另一个很常见的需求就是封装异常，当服务端出现错误时返回给客户端友好的错误信息，而不是服务端的错误堆栈。
```
(defn wrap-exception
  [handler]
  (fn [request]
    (try
      (handler request)
      (catch Throwable e
        (response {:code 20001
                   :msg  "inner error})))))

(def app
  (-> handlers
      wrap-json-response
      wrap-json-body
      handler/api
      wrap-exception
      record-response-time))
```

#### 顺序！顺序！顺序！

一个 App 中的 middleware 调用顺序非常重要，因为不同的 middleware 之间 request map 与 response map 是相互依赖的，所以在定义 middleware 时一定要注意顺序。一图胜千言：

![middleware 应用顺序图](https://img.alicdn.com/imgextra/i4/581166664/TB2BkmmmohnpuFjSZFEXXX0PFXa_!!581166664.png)

## 总结
在 Java EE 中，编写 Web 项目通常是配置各种 XML 文件，代码还没开始写就配置了一大堆jar包依赖，这些 jar 包很有可能会冲突，然后需要花大量时间处理这些依赖冲突，真心麻烦。

Ring 与其说是一个框架，不如说是由各个短小精悍的函数组成的 lib，充分展示了 Clojure 语言的威力，通过函数的组合定义出一套完整的 HTTP 抽象机制，通过宏来实现“路由”特定领域语言，极大简化了路由的定义，方便了模块的分解。

除了上面的介绍，Ring 生态里面还有 [lein-ring](https://github.com/weavejester/lein-ring) ，它可以在不重启服务的情况下重新加载有修改的命名空间（以及其影响的），开发从未如何顺畅。

Ring + Compojure + lein-ring 你值得拥有。

## 扩展阅读

- [Boot, the Fancy Clojure Build Framework](http://www.braveclojure.com/appendix-b/)
- http://www.lispcast.com/what-web-framework-should-i-use
- https://github.com/luminus-framework/luminus/blob/master/resources/md/html_templating.md
