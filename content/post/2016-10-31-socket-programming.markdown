---
title: Socket 编程实战
date: 2016-10-31 16:24:17
categories: [理解计算机]
tags: [Python]

---

Socket 在英文中的含义为“（连接两个物品的）凹槽”，像`the eye socket`，意为“眼窝”，此外还有“插座”的意思。在计算机科学中，socket 通常是指一个连接的两个端点，这里的连接可以是同一机器上的，像[unix domain socket](https://en.wikipedia.org/wiki/Unix_domain_socket)，也可以是不同机器上的，像[network socket](https://en.wikipedia.org/wiki/Network_socket)。

本文着重介绍现在用的最多的 network socket，包括其在网络模型中的位置、API 的编程范式、常见错误等方面，最后用 Python 语言中的 socket API 实现几个实际的例子。Socket 中文一般翻译为“套接字”，不得不说这是个让人摸不着头脑的翻译，我也没想到啥“信达雅”的翻译，所以本文直接用其英文表述。本文中所有代码均可在 [socket.py](https://github.com/jiacai2050/socket.py) 仓库中找到。

## 概述

Socket 作为一种通用的技术规范，首次是由 Berkeley 大学在 1983 为 4.2BSD Unix 提供的，后来逐渐演化为 POSIX 标准。Socket API 是由操作系统提供的一个编程接口，让应用程序可以控制使用 socket 技术。Unix 哲学中有一条`一切皆为文件`，所以 `socket` 和 `file` 的 API 使用很类似：可以进行`read`、`write`、`open`、`close`等操作。

现在的网络系统是分层的，理论上有[OSI模型](https://en.wikipedia.org/wiki/OSI_model)，工业界有[TCP/IP协议簇](https://en.wikipedia.org/wiki/Internet_protocol_suite)。其对比如下：
<center>
<img src="https://img.alicdn.com/imgextra/i2/581166664/TB2V0wfbmqJ.eBjy1zbXXbx8FXa_!!581166664.gif" alt=" osi vs tcp/ip"/>
</center>
每层上都有其相应的协议，socket API 不属于TCP/IP协议簇，只是操作系统提供的一个用于网络编程的接口，工作在应用层与传输层之间：
<center>
<img src="https://img.alicdn.com/imgextra/i3/581166664/TB2fzkbbhmJ.eBjy0FhXXbBdFXa_!!581166664.gif" alt="where socket works in tcp/ip"/>
</center>

我们平常浏览网站所使用的http协议，收发邮件用的smtp与imap，都是基于 socket API 构建的。

一个 socket，包含两个必要组成部分：

1. 地址，由 ip 与 端口组成，像`192.168.0.1:80`。
2. 协议，socket 所是用的传输协议，目前有三种：[TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)、[UDP](https://en.wikipedia.org/wiki/User_Datagram_Protocol)、[raw IP](https://en.wikipedia.org/wiki/Raw_socket)。

地址与协议可以确定一个socket；一台机器上，只允许存在一个同样的socket。TCP 端口 53 的 socket 与 UDP 端口 53 的 socket 是两个不同的 socket。

根据 socket 传输数据方式的不同（使用协议不同），可以分为以下三种：

1. [Stream sockets](https://en.wikipedia.org/wiki/Stream_socket)，也称为“面向连接”的 socket，使用 TCP 协议。实际通信前需要进行连接，传输的数据没有特定的结构，所以高层协议需要自己去界定数据的分隔符，但其优势是数据是可靠的。
2. [Datagram sockets](https://en.wikipedia.org/wiki/Datagram_socket)，也称为“无连接”的 socket，使用 UDP 协议。实际通信前不需要连接，一个优势时 UDP 的数据包自身是可分割的（self-delimiting），也就是说每个数据包就标示了数据的开始与结束，其劣势是数据不可靠。
3. [Raw sockets](https://en.wikipedia.org/wiki/Raw_socket)，通常用在路由器或其他网络设备中，这种 socket 不经过TCP/IP协议簇中的传输层（transport layer），直接由网络层（Internet layer）通向应用层（Application layer），所以这时的数据包就不会包含 tcp 或 udp 头信息。
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2qOeFX3hJc1FjSZFDXXbvnFXa_!!581166664.png_310x310.jpg" alt=" 数据包在各个层间的变更"/>
</center>
## Python socket API

Python 里面用`(ip, port)`的元组来表示 socket 的地址属性，用`AF_*`来表示协议类型。
数据通信有两组动词可供选择：`send/recv` 或 `read/write`。`read/write` 方式也是 Java 采用的方式，这里不会对这种方式进行过多的解释，但是需要注意的是：

> `read/write` 操作的具有 buffer 的“文件”，所以在进行读写后需要调用`flush`方法去真正发送或读取数据，否则数据会一直停留在缓冲区内。

### TCP socket
TCP socket 由于在通信前需要建立连接，所以其模式较 UDP socket 复杂些。具体如下：
<center>
<img width="400px" height="700px" src="https://img.alicdn.com/imgextra/i1/581166664/TB2egBSbOKO.eBjSZPhXXXqcpXa_!!581166664.png_620x10000.jpg" alt="TCP socket API "/>
</center>

API 的具体含义这里不在赘述，可以查看[手册](https://en.wikipedia.org/wiki/Berkeley_sockets#Socket_API_functions)，这里给出 Python 语言实现的 echo server。

- [echo_server.py](https://github.com/jiacai2050/socket.py/blob/master/simple_tcp_echo/echo_server.py)

```python

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handler(client_sock, addr):
    try:
        print('new client from %s:%s' % addr)
        msg = client_sock.recv(100)
        client_sock.send(msg)
        print('received data[%s] from %s:%s' % ((msg,) + addr))
    finally:
        client_sock.close()
        print('client[%s:%s] socket closed' % addr)

if __name__ == '__main__':
    # 设置 SO_REUSEADDR 后,可以立即使用 TIME_WAIT 状态的 socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 5500))
    sock.listen(5)

    while 1:
        client_sock, addr = sock.accept()
        handler(client_sock, addr)
```

- [echo_client.py](https://github.com/jiacai2050/socket.py/blob/master/simple_tcp_echo/echo_client.py)

```python

import socket

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_to_sent = 'hello tcp socket'
    try:
        sock.connect(('', 5500))

        sent = sock.send(data_to_sent)
        print(sock.recv(1024))
    finally:
        sock.close()
print('socket closed')
```

上面代码有一点需要注意：server 端的 socket 设置了`SO_REUSEADDR`为1，目的是可以立即使用处于`TIME_WAIT`状态的socket，那么`TIME_WAIT`又是什么意思呢？后面在讲解 [tcp 状态机](#TCP_的状态机)时再做详细介绍。

### UDP socket

<center>
<img width="400px" height="400px" src="https://img.alicdn.com/imgextra/i3/581166664/TB2.pEmbmGI.eBjSspcXXcVjFXa_!!581166664.jpg_620x10000.jpg" alt=" udp_socket_api"/>
</center>

UDP 版的 socket server 的代码在进行`bind`后，无需调用`listen`方法。

- [udp_echo_server.py](https://github.com/jiacai2050/socket.py/blob/master/simple_udp_echo/echo_server.py)

```python

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 设置 SO_REUSEADDR 后,可以立即使用 TIME_WAIT 状态的 socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5500))
# 没有调用 listen

if __name__ == '__main__':
    while 1:
        data, addr = sock.recvfrom(1024)

        print('new client from %s:%s' % addr)
        sock.sendto(data, addr)
```

- [udp_echo_client.py](https://github.com/jiacai2050/socket.py/blob/master/simple_udp_echo/echo_client.py)

```python

import socket

udp_server_addr = ('', 5500)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_to_sent = 'hello udp socket'
    try:
        sent = sock.sendto(data_to_sent, udp_server_addr)
        data, server = sock.recvfrom(1024)
        print('receive data:[%s] from %s:%s' % ((data,) + server))
    finally:
        sock.close()
```

## 常见陷阱

### 忽略返回值

本文中的 echo server 示例因为篇幅限制，也忽略了返回值。网络通信是个非常复杂的问题，通常无法保障通信双方的网络状态，很有可能在发送/接收数据时失败或部分失败。所以有必要对发送/接收函数的返回值进行检查。本文中的 tcp echo client 发送数据时，正确写法应该如下：

```python
total_send = 0
content_length = len(data_to_sent)
while total_send < content_length:
    sent = sock.send(data_to_sent[total_send:])
    if sent == 0:
        raise RuntimeError("socket connection broken")
    total_send += total_send + sent
```

同理，接收数据时也应该检查返回值：

```python
chunks = []
bytes_recd = 0
while bytes_recd < MSGLEN:   # MSGLEN 为实际数据大小
    chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
    if chunk == b'':
        raise RuntimeError("socket connection broken")
    chunks.append(chunk)
    bytes_recd = bytes_recd + len(chunk)
return b''.join(chunks)    
```

`send/recv`操作的是网络缓冲区的数据，它们不必处理传入的所有数据。
> 一般来说，当网络缓冲区填满时，[send函数](https://docs.python.org/3/library/socket.html#socket.socket.send)就返回了；当网络缓冲区被清空时，[recv 函数](https://docs.python.org/3/library/socket.html#socket.socket.recv)就返回。

可以通过下面的方式设置缓冲区大小。

    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)  # 发送
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)  # 接受

### 误认为 TCP 具有 framing

TCP 不提供 framing，这使得其很适合于传输数据流。这是其与 UDP 的重要区别之一。UDP 是一个面向消息的协议，能保持一条消息在发送者与接受者之间的完备性。
<center>
<img src="https://img.alicdn.com/imgextra/i4/581166664/TB2SB4bbB9J.eBjy0FoXXXyvpXa_!!581166664.gif" alt="Framing capabilities of UDP and the lack of framing in TCP"/>
</center>

代码示例参考：[framing_assumptions](https://github.com/jiacai2050/socket.py/tree/master/framing_assumptions)

## TCP 的状态机
在前面echo server 的示例中，提到了TIME_WAIT状态，为了正式介绍其概念，需要了解下 TCP 从生成到结束的状态机。（[图片来源](https://www.ibm.com/support/knowledgecenter/SSLTBW_2.1.0/com.ibm.zos.v2r1.halu101/constatus.htm)）

<center>
<img width="500px" height="600px" src="https://img.alicdn.com/imgextra/i2/581166664/TB2Us0HbNeK.eBjSZFlXXaywXXa_!!581166664.gif" alt=" tcp_state transition"/>
</center>

这个状图转移图非常非常关键，也比较复杂，总共涉及了 11 种状态。我自己为了方便记忆，对这个图进行了拆解，仔细分析这个图，可以得出这样一个结论：
> 连接的打开与关闭有被动（passive）与主动（active）两种情况。主动关闭时，涉及到的状态转移最多，包括FIN_WAIT_1、FIN_WAIT_2、CLOSING、TIME_WAIT。（是不是有种 no zuo no die 的感觉）

此外，由于 TCP 是可靠的传输协议，所以每次发送一个数据包后，都需要得到对方的确认（ACK），有了上面这两个知识后，再来看下面的图：（[图片来源](http://coolshell.cn/articles/11564.html)）
<center>
<img width="400px" height="500px" src="https://img.alicdn.com/imgextra/i4/581166664/TB2nwCFbNaK.eBjSZFwXXXjsFXa_!!581166664.jpg" alt=" tcp 关闭时的状态转移时序图"/>
</center>

我们重点分析上图中链接断开的过程，其中主动关闭端为 Client，被动关闭端为 Server 。

1. Client 调用 `close` 方法的同时，会向 Server 发送一个 FIN，然后自己处于 FIN_WAIT_1 状态，在收到 server ACK 回应后变为 FIN_WAIT_2
2. Server 收到 FIN 后，向 Client 回复 ACK 确认，状态变化为 CLOSE_WAIT，然后开始进行一些清理工作
3. 在 Server 清理工作完成后，会调用`close`方法，这时向 Client 发送 FIN 信号，状态变化为 LAST_ACK
4. Client 接收到 FIN 后，状态由 FIN_WAIT_2 变化为 TIME_WAIT，同时向 Server 回复 ACK
5. Server 收到 ACK 后，状态变化为 CLOSE，表明 Server 端的 socket 已经关闭
6. 处于 TIME_WAIT 状态的 Client 不会立刻转为 CLOSED 状态，而是需要等待 2MSL（max segment life，一个数据包在网络传输中最大的生命周期），以确保 Server 能够收到最后发出的 ACK。如果 Server 没有收到最后的 ACK，那么 Server 就会重新发送 FIN，所以处于TIME_WAIT的 Client 会再次发送一个 ACK 信号，这么一来（FIN来）一回（ACK），正好是两个 MSL 的时间。如果等待的时间小于 2MSL，那么新的 socket 就可以收到之前连接的数据。

上面是正常逻辑时的关闭顺序，如果任意一步出现问题都会导致 Socket 状态变化出现问题，下面说几种常见的问题：

1. 在上述过程第二步，回复完 ACK 后，如果忘记调用 CLOSE 方法，那么 Server 端在会一直处于 CLOSE_TIME 状态，处于 FIN_WAIT_2 状态的 Client 端会在 60 秒后超时，直接关闭。这个问题的具体案例可参考[《This is strictly a violation of the TCP specification》](https://blog.cloudflare.com/this-is-strictly-a-violation-of-the-tcp-specification)
2. 前面 echo server 的示例也说明了，处于 TIME_WAIT 并不是说一定不能使用，可以通过设置 socket 的 `SO_REUSEADDR` 属性以达到不用等待 2MSL 的时间就可以复用socket 的目的，当然，这仅仅适用于测试环境，正常情况下不要修改这个属性。

## 实战

### HTTP UA

http 协议是如今万维网的基石，可以通过 socket API 来简单模拟一个浏览器（UA）是如何解析 HTTP 协议数据的。

```

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
baidu_ip = socket.gethostbyname('baidu.com')
sock.connect((baidu_ip, 80))
print('connected to %s' % baidu_ip)

req_msg = [
    'GET / HTTP/1.1',
    'User-Agent: curl/7.37.1',
    'Host: baidu.com',
    'Accept: */*',
]
delimiter = '\r\n'

sock.send(delimiter.join(req_msg))
sock.send(delimiter)
sock.send(delimiter)

print('%sreceived%s' % ('-'*20, '-'*20))
http_response = sock.recv(4096)
print(http_response)
```

运行上面的代码可以得到下面的输出

```
--------------------received--------------------
HTTP/1.1 200 OK
Date: Tue, 01 Nov 2016 12:16:53 GMT
Server: Apache
Last-Modified: Tue, 12 Jan 2010 13:48:00 GMT
ETag: "51-47cf7e6ee8400"
Accept-Ranges: bytes
Content-Length: 81
Cache-Control: max-age=86400
Expires: Wed, 02 Nov 2016 12:16:53 GMT
Connection: Keep-Alive
Content-Type: text/html

<html>
<meta http-equiv="refresh" content="0;url=http://www.baidu.com/">
</html>
```

`http_response`是通过直接调用`recv(4096)`得到的，万一真正的返回大于这个值怎么办？我们前面知道了 TCP 协议是面向流的，它本身并不关心消息的内容，需要应用程序自己去界定消息的边界，对于应用层的 HTTP 协议来说，有几种情况，最简单的一种时通过解析返回值头部的`Content-Length`属性，这样就知道`body`的大小了，对于 HTTP 1.1版本，支持`Transfer-Encoding: chunked`传输，对于这种格式，这里不在展开讲解，大家只需要知道， TCP 协议本身无法区分消息体就可以了。对这块感兴趣的可以查看 CPython 核心模块 [http.client](https://github.com/python/cpython/blob/master/Lib/http/client.py)

### Unix_domain_socket

UDS 用于同一机器上不同进程通信的一种机制，其API适用与 network socket 很类似。只是其连接地址为本地文件而已。

代码示例参考：[uds_server.py](https://github.com/jiacai2050/socket.py/blob/master/in_action/uds_server.py)、[uds_client.py](https://github.com/jiacai2050/socket.py/blob/master/in_action/uds_client.py)

### ping

ping 命令作为检测网络联通性最常用的工具，其适用的传输协议既不是TCP，也不是 UDP，而是 [ICMP](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol)。
ICMP 消息（messages）通常用于诊断 IP 协议产生的错误，traceroute 命令也是基于 ICMP 协议实现。利用 Python raw sockets API 可以模拟发送 ICMP 消息，实现类似 ping 的功能。

代码示例参考：[ping.py](https://github.com/jiacai2050/socket.py/blob/master/in_action/ping.py)


### netstat vs ss

netstat 与 ss 都是类 Unix 系统上查看 Socket 信息的命令。netstat 是比较老牌的命令，常用的选择有

- `-t`，只显示 tcp 连接
- `-u`，只显示 udp 连接
- `-n`，不用解析hostname，用 IP 显示主机，可以加快执行速度
- `-p`，查看连接的进程信息
- `-l`，只显示监听的连接

ss 是新兴的命令，其选项和 netstat 差不多，主要区别是能够进行过滤（通过`state`与`exclude`关键字）。

```shell
$ ss -o state time-wait -n | head
Recv-Q Send-Q             Local Address:Port               Peer Address:Port
0      0                 10.200.181.220:2222              10.200.180.28:12865  timer:(timewait,33sec,0)
0      0                      127.0.0.1:45977                 127.0.0.1:3306   timer:(timewait,46sec,0)
0      0                      127.0.0.1:45945                 127.0.0.1:3306   timer:(timewait,6.621ms,0)
0      0                 10.200.181.220:2222              10.200.180.28:12280  timer:(timewait,12sec,0)
0      0                 10.200.181.220:2222              10.200.180.28:35045  timer:(timewait,43sec,0)
0      0                 10.200.181.220:2222              10.200.180.28:42675  timer:(timewait,46sec,0)
0      0                      127.0.0.1:45949                 127.0.0.1:3306   timer:(timewait,11sec,0)
0      0                      127.0.0.1:45954                 127.0.0.1:3306   timer:(timewait,21sec,0)
0      0               ::ffff:127.0.0.1:3306           ::ffff:127.0.0.1:45964  timer:(timewait,31sec,0)
```

这两个命令更多用法可以参考：
- [SS Utility: Quick Intro](http://www.cyberciti.biz/files/ss.html)
- [10 basic examples of linux netstat command](http://www.binarytides.com/linux-netstat-command-examples/)


## 总结

我们的生活已经离不开网络，平时的开发也充斥着各种复杂的网络应用，从最基本的数据库，到各种分布式系统，不论其应用层怎么复杂，其底层传输数据的的协议簇是一致的。Socket 这一概念我们很少直接与其打交道，但是当我们的系统出现问题时，往往是对底层的协议认识不足造成的，希望这篇文章能对大家编程网络方面的程序有所帮助。


## 参考

- [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
- [TCP: About FIN_WAIT_2, TIME_WAIT and CLOSE_WAIT](https://benohead.com/tcp-about-fin_wait_2-time_wait-and-close_wait/)
- [Five pitfalls of Linux sockets programming](http://www.ibm.com/developerworks/library/l-sockpit/)
- [Programming Linux sockets, Part 1: Using TCP/IP](http://www.ibm.com/developerworks/linux/tutorials/l-sock/)
- http://stackoverflow.com/questions/10328675/how-to-know-content-length
- [What’s The Difference Between The OSI Seven-Layer Network Model And TCP/IP?](http://electronicdesign.com/what-s-difference-between/what-s-difference-between-osi-seven-layer-network-model-and-tcpip)
- [TCP 的那些事儿（上）](http://coolshell.cn/articles/11564.html)
- [Coping with the TCP TIME-WAIT state on busy Linux servers](https://vincent.bernat.im/en/blog/2014-tcp-time-wait-state-linux.html)
