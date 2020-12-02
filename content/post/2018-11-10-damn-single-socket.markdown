title: 形单影只的 Socket
date: 2018-11-10 22:15:18
categories: [理解计算机]
tags: [Linux]
---

最近工作上遇到过几次因 http client 没有配置超时相关参数，导致线程数占满或应用卡住的情况，出问题时线程的堆栈大致是这样的：

```sh
"qtp325266363-35729" #35729 prio=5 os_prio=0 tid=0x00007f5154033000 nid=0x1cf8f runnable [0x00007f4f7f511000]
   java.lang.Thread.State: RUNNABLE
        at java.net.SocketInputStream.socketRead0(Native Method)
        at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
        at java.net.SocketInputStream.read(SocketInputStream.java:171)
        at java.net.SocketInputStream.read(SocketInputStream.java:141)
        at sun.security.ssl.InputRecord.readFully(InputRecord.java:465)
        at sun.security.ssl.InputRecord.read(InputRecord.java:503)
        at sun.security.ssl.SSLSocketImpl.readRecord(SSLSocketImpl.java:983)
        - locked <0x00000006e1494d68> (a java.lang.Object)
        at sun.security.ssl.SSLSocketImpl.readDataRecord(SSLSocketImpl.java:940)
        at sun.security.ssl.AppInputStream.read(AppInputStream.java:105)
        - locked <0x00000006e1496d88> (a sun.security.ssl.AppInputStream)
        at org.apache.http.impl.conn.LoggingInputStream.read(LoggingInputStream.java:84)
        at org.apache.http.impl.io.SessionInputBufferImpl.streamRead(SessionInputBufferImpl.java:137)
        at org.apache.http.impl.io.SessionInputBufferImpl.fillBuffer(SessionInputBufferImpl.java:153)
        at org.apache.http.impl.io.SessionInputBufferImpl.readLine(SessionInputBufferImpl.java:282)
        at org.apache.http.impl.conn.DefaultHttpResponseParser.parseHead(DefaultHttpResponseParser.java:138)
        at org.apache.http.impl.conn.DefaultHttpResponseParser.parseHead(DefaultHttpResponseParser.java:56)
        at org.apache.http.impl.io.AbstractMessageParser.parse(AbstractMessageParser.java:259)
        at org.apache.http.impl.DefaultBHttpClientConnection.receiveResponseHeader(DefaultBHttpClientConnection.java:163)
```
程序卡在了 `socketRead0` 上，我们线上版本用的是 [httpclient 4.4.5](https://hc.apache.org/httpcomponents-client-ga/)，配置下面参数即可：

```java
int timeout = 5;
RequestConfig config = RequestConfig.custom()
  .setConnectTimeout(timeout * 1000)
  .setConnectionRequestTimeout(timeout * 1000)
  .setSocketTimeout(timeout * 1000).build();
CloseableHttpClient client = 
  HttpClientBuilder.create().setDefaultRequestConfig(config).build();
```
上面设置了三个超时时间，含义分别是
- Connection Timeout，表示与远端服务期建立连接的超时
- Socket Timeout，表示连接上两个 packet 之间的超时，当空闲时间超过这个后该连接就会自动断开
- Connection Manager Timeout，表示从连接池申请连接时的超时

好了，其实这不是这篇文章的重点，重点是在 debug 这个问题时，发现的一个有趣现象，为了阐述该现象，需要先回顾下 [socket 编程](/blog/2016/10/31/socket-programming/)的基本知识。

## Socket 定义

计算机领域里的 socket ，表示可以进行通讯的两个程序，一般称为 endpoint，如果是同一台机器上，则对应 [Unix domain socket](https://en.wikipedia.org/wiki/Unix_domain_socket)，如果是不同机器，则为 [network socket](https://en.wikipedia.org/wiki/Network_socket)，一方称为 client，另一方称为 server。

对于 TCP socket 来说，使用流程如下：

![TCP socket API](https://img.alicdn.com/imgextra/i1/581166664/TB2egBSbOKO.eBjSZPhXXXqcpXa_!!581166664.png_620x10000.jpg)

连接建立后，可以通过 [ss 命令](https://linux.die.net/man/8/ss)查看到

```sh
# 3000 端口为一 Java 写的 HTTP Server，35050 为 curl 访问时随机选择的本地端口
$ ss -np | grep 3000
Netid  State      Recv-Q Send-Q     Local Address:Port       Peer Address:Port
tcp    ESTAB      0      0              127.0.0.1:35050         127.0.0.1:3000   users:(("curl",12436,3))
tcp    ESTAB      0      0              127.0.0.1:3000          127.0.0.1:35050  users:(("java",12279,82))

```

由于 socket 涉及两端，每一端用 ip + port 去标示，再加上通讯协议，所以需要用五个字段来标示，一般表述为 

```sh
# protocol 一般为 tcp/udp
(protocol, src_ip:src_port, dst_ip:dst_port)
```

## 形单影只的 socket 

经过上面的介绍，往往会以为 TCP socket 都是成对出现的，毕竟有两方参与。这也符合 99.99% 的场景，但是 TCP 协议在定义时，并没有严格要通讯双方必须为不同的程序，也就是说只要符合 TCP 状态机的模型，就可以做到自己与自己通讯（即 ESTABLISHED 状态）。通过下面一示例可以证明：

```sh
$ while true; do nc -v localhost 11111; done
...
...
nc: connect to localhost port 11111 (tcp) failed: Connection refused
nc: connect to localhost port 11111 (tcp) failed: Connection refused
nc: connect to localhost port 11111 (tcp) failed: Connection refused
nc: connect to localhost port 11111 (tcp) failed: Connection refused
Connection to localhost 11111 port [tcp/*] succeeded!
```

上面示例在开始运行时一直失败，说明 11111 端口没有被 LISTEN，所以连接一直失败，但是在某一时刻突然就连上了！还是请出我们的老朋友 ss 看看怎么回事

```sh
$ ss -np  | grep 11111
tcp    ESTAB      0      0              127.0.0.1:11111         127.0.0.1:11111  users:(("nc",8419,3))
```

额，竟然只有一个 socket！这时的 nc 命令同时兼具了 server 与 client 两个角色，这时其实是个 echo server，输入什么，就会输出什么。

这看上去有些不可思议，为了弄清问题，可以通过 tcpdump 来分析连接是怎么建立的。

```sh
$ sudo tcpdump -i any port 11111 -Snw /tmp/debug.pcap -vvv

# 新开另一个窗口，输入
$ nc -vp 11111 localhost 11111
Connection to localhost 11111 port [tcp/*] succeeded!
# 这里通过 -p 选项制定了 client 的端口号，方便快速浮现问题
```

然后通过 Wireshark 打开得到的 pcap 文件，发现了著名的「三次握手」

![三次握手](https://img.alicdn.com/imgextra/i3/581166664/O1CN01cgFBcS1z69rFquQhR_!!581166664.png)

虽然第二个 packet 显示为 out of order，但是并没有影响该 socket TCP 状态的转移！

这里需要再复习下 TCP 状态转移过程：

![tcp_state transition](https://img.alicdn.com/imgextra/i2/581166664/TB2Us0HbNeK.eBjSZFlXXaywXXa_!!581166664.gif)

当处于 close 状态的 socket 发出 `SYN` 包后，会处于 `SYN_SENT` 状态，这时如果收到 `SYN,ACK` 并回复 `ACK` 包后，就会处于 `ESTABLISHED`。
可以看到，一个 socket 竟然就可以完成上述步骤。

那么能不能复现「四次挥手」呢？直接 `Ctrl+C` 结束上面的 nc 进程，然后再通过 tcpdump+wireshark 可以得到下面的结果：

![“二次挥手”](https://img.alicdn.com/imgextra/i1/581166664/O1CN011z69rDS08WSZzlD_!!581166664.png)

通过 ss 命令也没找到处于 TIME-WAIT 状态的 11111，说明进行的是「被动关闭」（状态转移图右下角）流程。

## 结论

看完本文的一点“实用”干货可能是解释为什么不要去 LISTEN 比较高的端口，但是更希望大家能多去动手，发现隐藏在表象下的根源，这其实和脱单是一个道理 -:)

最后，留个“动手”问题给大家思考：

> 如何找出一个已经 ESTABLISHED 的 TCP 连接建立时间与最后一次通讯（即有数据传输）的时间？

[在这里](https://github.com/jiacai2050/jiacai2050.github.io/issues/3) 提供一种解决思路。

## 参考

- https://www.baeldung.com/httpclient-timeout
- https://blog.cloudflare.com/this-is-strictly-a-violation-of-the-tcp-specification/
- https://linux.die.net/man/8/ss
