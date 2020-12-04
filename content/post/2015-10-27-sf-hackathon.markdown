---
title: SF 黑客马拉松赛后回顾
date: 2015-10-27 21:05:30
tags: [nodejs]
categories: [热爱生活]
---

上个周末，也就是10月24、25号，参加了人生中第一次[黑客马拉松](http://segmentfault.com/hackathon-2015)（hackathon），虽然最终没有获奖，但是这个比赛过程中还是 hack 的挺爽，趁现在还有余热，纪录下比赛时的一些心得与收获。

## 为什么参加 hackathon

当在公司得知有黑客马拉松之后，我就立即报名了，觉得这件事本身就很酷，虽然身边一些同事说此类比赛没意思，大部分人都是奔着投资去的，但我还是觉得要你怎么看了，你如果去是为了那奖品、钱，我觉得那失去了 hackathon 的意义了，hackathon 我理解的就是
> 做一些很酷的事情，而这些事情在平时的工作中“用不到”，但是完成这些事能够让我们有很强的满足感。

也就是玩，虽然当知道自己的作品没有获奖时会有些许失落，但那是一时的，最起码那一天一夜 coding，让我确实很 high。

## 赛前准备

编程语言我毫无疑问的选择了 javascript，一来 javascript 与 Scheme 有[很深的渊源](https://en.wikipedia.org/wiki/JavaScript#JavaScript_and_Java)，其次我也一直想好好系统学习下 nodejs，所以就是它了。参加比赛前的一周，我停止了 [SICP](https://github.com/jiacai2050/sicp) 的阅读，转而进攻[《Node.js实战》](http://book.douban.com/subject/25870705/)，这本书之前断断续续翻过前两章，这次基本把这本书看完了，主要是学习了下如何系统的开发一个完整的 node 应用，包括常用模块、通用架构等，之前写的 node 都是玩具，没有错误处理，没有单元测试（这次比赛虽然也没用上，但是知道了如何使用相应工具去测了）。

书上最后一章介绍了 node 中较为底层的知识，像`net`库，node 的定位就是提供小而美的核心类库，常用的模块都是基于这些核心类库构建。下面纪录两个书中比较有趣的例子：
```
var net = require("net");
var socket = net.connect({host: "github.com", port: 22});
socket.on("data", function(chunk) {
    console.log(chunk.toString());
    socket.end();
})
// 启动后，会输出 SSH-2.0-libssh-0.7.0
```
下面的代码片段实现了类似于 Linux 上 [nc](http://linux.die.net/man/1/nc) 命令的功能：
```
var net = require("net");
var socket = net.connect({host: process.argv[2], port: process.argv[3]});

socket.on("connect", function() {
    process.stdin.pipe(socket);
    socket.pipe(process.stdout);
    process.stdin.resume();
});
socket.on("close", function() {
    console.log("bye...");
});
```
其次在看 expressjs 时，无意间发现其作者 [tj](https://github.com/tj) 早在 2014年4月份，就已经[抛弃 nodejs，投向 go 的怀抱](https://medium.com/@tjholowaychuk/farewell-node-js-4ba9e7f3e52b)，心中难免有些忧伤，大牛总是这样，在我们还在学习某东西时，人家已经发现其缺点，转向更高深的地方......

## 比赛开始了

这次的比赛是命题制——技术改变生活，这基本上是没有限制，经过有赞小伙伴的一番讨论，最终定了3个题目，然后就开始组队做了，我和劲风一组，做的是一个超市扫码购物的微信应用，想要解决的基本问题是——超市排长队付款。对于我来说，主要是想做一些有难度的技术，挑战自己，也没想为什么现在超市为什么不推行扫码购物，当然这也是后来评委问我们的问题。
这个题目主要的技术难点有：

### 微信公众号开发
如何扫码是我们遇到的第一个问题，是借助微信还是自己做原生应用，由于我俩都不会 Android 与 IOS 开发，所以微信成了唯一选择。
微信开发需要有公众号，如果调用 [JS-SDK](http://mp.weixin.qq.com/wiki/7/aaa137b55fb2e0456bf8dd9148dd613f.html)，需要有备过案的域名，我们都没有，这时我想到了[大宝](http://sundabao.com/)兄，他很慷慨的给我提供云主机、mysql、nginx，加上宝贵的域名，很是感谢。（后面知道了可以用[测试号](http://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)）。

这里必须吐槽下微信的开发文档，真是烂：排版烂、个别语句不通顺、经常有死链接，希望微信团队好好维护下。

比如这里的[签名算法](http://mp.weixin.qq.com/wiki/7/aaa137b55fb2e0456bf8dd9148dd613f.html)，由于微信的人不知道[命名锚（named anchors）](http://www.w3school.com.cn/html/html_links.asp)，所以你在打开上面的链接后，需要用`Ctrl + F` 来搜索 “签名算法” 才能找到我这里所指的签名算法，最最坑人的是，由于签名是针对网页 URL 的，所以一个网页需要签名一个，而这个 URL 必须是以`/`结尾，比如，如果用`http://1024.sundabao.com`这个 URL 来签名是不对的，必须是`http://1024.sundabao.com/`，这个真的好坑。

相比之下，Github的[开发者文档](https://developer.github.com/v3)，看起来就很让人舒服，希望微信团队好好学学。

### 订单系统

扫码问题解决了，剩下的就是一个集成购物车的订单系统，之前在公司虽然也是在数据部，但是报表做的不多，真是没想到这订单系统是多么麻烦，我当时遇到问题就是，购物车选好后，点击提交，这时，按理说应该生成订单的，但是生成订单的同时是否需要把购物车的商品删除呢，第一感觉是需要，但是后来发现不是这样的，如果顾客发现还有商品没有购买，这时他会返回上一页继续购买，所以正确的做法是在确认支付订单后，再去把购物车的商品删掉。但是这样也会有问题，因为顾客确认支付方式后，有可能支付失败了，这时按理说购物车里的东西还是应该有的，但是我们这里比较简单，只要用户点击支付，就认为成功了。可见，要做一个完整的订单＋交易系统，是多么不容易的事。

### callback hell

由于订单系统的逻辑比较多，涉及很多数据库的操作，而我们使用 nodejs 也没用什么 ORM 系统，只是用原生的 sql 来做，这时就陷入了 [callback hell](http://callbackhell.com/)，之前写 node 程序一般都不怎么关注错误处理， 所以一直没怎么发现这个问题，这次在做这个订单系统，真是暴露无疑，太难维护了。

下面代码片段的功能是：扫描一个商品，向购物车列表中增加一个商品的 `callback hell`
```
exports.add = function(userId, goodsId, goodsNum, cb) {
    var that = this;
    var dbPool = db.getPool();
    var sql = "insert into 1024_cart values (?,?,?) ON DUPLICATE KEY UPDATE goods_num=goods_num+1";
    sql = db.formatSQL(sql, [userId, goodsId, goodsNum]);
    dbPool.query(sql, function(err, result) {
        if(err) {
            logger.error("exec:" + sql + " error:" + err);
            cb({code:-2, msg: "服务器内部错误！"});
        } else if(result.affectedRows > 0) {
            goodsDAO.select(goodsId, function(err, result) {
                if(err) {
                    logger.error("exec:goodsDAO.select. error:" + err);
                    cb({code:-2, msg: "服务器内部错误！"});
                }
                else if(result.length == 0) {
                    that.delete(userId, goodsId);
                    cb({code:-1, msg: "数据库中没有该商品！"});
                } else {
                    var goods = result[0];
                    getGoodsNum(userId, goodsId, function(err, result) {
                        if(err) {
                            cb({code:-2, msg: "服务器内部错误！"});
                        } else {
                            goods["num"] = result[0]["goods_num"];
                            cb({code:0, data: goods});
                        }
                    })
                }
            }); 
        } else {
            cb({code:-3, msg: "修改失败！"});
        }
    });
}
```

## 编码与生活

在整个比赛过程中（大概20个小时），我睡了不到4个小时，大脑一直处于兴奋状态，一直在解决问题，从动态获取微信签名，到解决订单系统的 bug，到最后的测试，都是极度兴奋的，coding 的比较 high。

> **我觉得我会编码到老**。

记得在学生时代就不断听到有人说，程序员是青春饭，做几年后要转向管理岗，真不知道说这些话的人是出于什么心理，当然有部分人是把编码当成为一份养家糊口的工作，但是我相信更多人是因为热爱编码而编码的，从编码中能汲取无限快乐。

如果你身边在有人 balabala 的说诸如此类的话，我劝你最好离这种人远些，道不同不相为谋，世界这么大，为什么不去做自己喜欢的事呢？

## 精彩瞬间

![美丽的互联网小镇](https://img.alicdn.com/imgextra/i4/581166664/TB29QBpgFXXXXcOXXXXXXXXXXXX_!!581166664.jpg)


![午餐时刻](https://img.alicdn.com/imgextra/i4/581166664/TB2bstCgFXXXXXSXXXXXXXXXXXX_!!581166664.jpg)

![比赛开始了](https://img.alicdn.com/imgextra/i3/581166664/TB2pBXCgFXXXXanXXXXXXXXXXXX_!!581166664.jpg)

![休息，休息一会♨️](https://img.alicdn.com/imgextra/i4/581166664/TB2dNhogFXXXXXmXpXXXXXXXXXX_!!581166664.jpg)
![大家都睡了，但我们还在继续...](https://img.alicdn.com/imgextra/i4/581166664/TB2ZDFngFXXXXXvXpXXXXXXXXXX_!!581166664.jpg)

![凌晨3点的互联网小镇](https://img.alicdn.com/imgextra/i3/581166664/TB2QsppgFXXXXXQXpXXXXXXXXXX_!!581166664.jpg)

![圆满结束，感谢 sf 组办方](https://img.alicdn.com/imgextra/i1/581166664/TB2w8xkgFXXXXX5XpXXXXXXXXXX_!!581166664.jpg)

![有赞小伙伴](https://img.alicdn.com/imgextra/i1/581166664/TB212BEgFXXXXX0XXXXXXXXXXXX_!!581166664.jpg)

注：图片均来自 sf 官方，如涉及个人隐私请告知。

## 总结

这次参加比赛，玩的很开心，没什么遗憾。至于代码就不开源了，写的比较烂，后面等功力提升了在说这事。感兴趣可以看看我们作品[易购 EasyGo](http://note.youdao.com/share/web/file.html?id=134b727dc48180570c66408da03116d4&type=note)的简介。

这里我想回答当时评委问我们组的问题——**为什么现在的超市不推广扫码支付**：

1. 二维码识别后，一般会包含商品的生产日期这个信息，而对于超市某些产品，像海鲜，是不想让顾客知道这个的...
2. 同一商品不同超市买的价格可能不一样，这样卖的贵的超市是不愿意用这套系统的...

对于这些，我只能说，经济基础决定上层建筑，商家还是以盈利为目的的。

比赛是结束了，但生活的挑战还在继续，[SICP](https://github.com/jiacai2050/sicp) 要继续搞起了，这次停了有两个多星期了，真要多下功夫了。

希望大家都能够 happy hacking ！