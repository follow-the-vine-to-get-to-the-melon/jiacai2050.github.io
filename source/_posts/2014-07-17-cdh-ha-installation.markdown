---
layout: post
title: "hadoop1.0 高可靠性(HA)安装与总结"
date: 2014-07-17 23:07:34 +0800
comments: true
categories: hadoop
---
继上次[安装完Kerberos安全认证](/blog/2014/07/15/cdh-kerberos-installation/)后，现在我在这基础上，又给CDH加上了HA（high availability），也就是高可靠性，具体来讲就是双NameNode，双Jobtracker（我还是在MRv1模式下），有了HA后，这下集群的健壮性就能够得到很好的保证了。

我还是按照[官方文档][guide]来操作的，有了上次的经验，建议大家在具体操作实施前，先快速阅读一遍，做到心中有数，我还阅读了[Apache官方的说明][apache-ha]，也不用怎么详细，大概知道怎么回事就行了。
<!--more-->
首先说明一点的就是，CDH5 只支持Quorum Journal Manager(QJM)模式下的HA，不支持NFS模式的，这点和Apache官方的不一样，大家要留意下。

下面说说我遇到的坑：

- 按照[software_config][]上面说的配置一步步来，如果要实现自动的Failover，需要安装zookeeper，安装也很简单，从[http://archive.cloudera.com/cdh5/cdh/5/](http://archive.cloudera.com/cdh5/cdh/5/)下载[zookeeper-3.4.5-cdh5.0.2.tar.gz](http://archive.cloudera.com/cdh5/cdh/5/zookeeper-3.4.5-cdh5.0.2.tar.gz)，然后按照[zookeeper的安装说明](http://archive.cloudera.com/cdh5/cdh/5/zookeeper/zookeeperStarted.html)安装即可，官方推荐zookeeper的集群数目为奇数，推荐值为3,我这样也配置了3台，zookeeper服务在在启动时会向集群内其他服务器发送认证数据，但是在第一次启动时难免有个先后顺序，所以先启动的节点向还没有启动的服务器发生数据时会报错，类型下面的错误信息
```
2014-07-17 14:49:06,151 [myid:1] - INFO  [WorkerReceiver[myid=1]:FastLeaderElection@542] - Notification: 1 (n.leader), 0x100000106 (n.zxid), 0x1 (n.round), LOOKING (n.state), 1 (n.sid), 0x2 (n.peerEPoch), LOOKING (my state)
2014-07-17 14:49:06,153 [myid:1] - WARN  [WorkerSender[myid=1]:QuorumCnxManager@368] - Cannot open channel to 2 at election address node1/10.4.13.63:3888
java.net.ConnectException: Connection refused
    at java.net.PlainSocketImpl.socketConnect(Native Method)
    at java.net.AbstractPlainSocketImpl.doConnect(AbstractPlainSocketImpl.java:339)
    at java.net.AbstractPlainSocketImpl.connectToAddress(AbstractPlainSocketImpl.java:200)
    at java.net.AbstractPlainSocketImpl.connect(AbstractPlainSocketImpl.java:182)
    at java.net.SocksSocketImpl.connect(SocksSocketImpl.java:392)
    at java.net.Socket.connect(Socket.java:579)
    at org.apache.zookeeper.server.quorum.QuorumCnxManager.connectOne(QuorumCnxManager.java:354)
    at org.apache.zookeeper.server.quorum.QuorumCnxManager.toSend(QuorumCnxManager.java:327)
    at org.apache.zookeeper.server.quorum.FastLeaderElection$Messenger$WorkerSender.process(FastLeaderElection.java:393)
    at org.apache.zookeeper.server.quorum.FastLeaderElection$Messenger$WorkerSender.run(FastLeaderElection.java:365)
    at java.lang.Thread.run(Thread.java:745)

```
这个是正常的，等3台全部启动后，有如下日志就证明没问题了
```
2014-07-17 11:26:44,425 [myid:3] - INFO  [WorkerReceiver[myid=3]:FastLeaderElection@542] - Notification: 3 (n.leader), 0x0 (n.zxid), 0x1 (n.round), LOOKING (n.state), 3 (n.sid), 0x0 (n.peerEPoch), LOOKING (my state)
2014-07-17 11:26:44,426 [myid:3] - INFO  [WorkerReceiver[myid=3]:FastLeaderElection@542] - Notification: 2 (n.leader), 0x0 (n.zxid), 0x1 (n.round), LOOKING (n.state), 1 (n.sid), 0x0 (n.peerEPoch), LOOKING (my state)
```

- 在配置Securing access to ZooKeeper这步时，我也能得到像官方教程上说的
```
digest:hdfs-zkfcs:vlUvLnd8MlacsE80rDuu6ONESbM=:rwcda
```
与这个类似的信息，但是在执行zkfc -formatZK时，老是说的我得到的字符串（'->' 后面的那部分）不对，我也不知道为什么，不知道是不是哪步少了什么，因为zookeeper集群在内网，集群内安全性一般不用考虑，我这里就直接忽略了这步，以后机会再找原因。

- 在配置Fencing Configuration时，我用了sshfence的方式，这里需要配置ssh的密钥，我直接把hdfs用户的密钥路径给上，后来在我验证双Namenode是否生效（通过kill掉active的NN，看看standby的NN能不能变为active的NN）发现不对，老是报错，连接不上另一个Namenode，后来发现需要用root的密钥，但是hdfs用户又不能读取root的密钥，所以我这里直接把root的.ssh文件下的文件全copy到hdfs用户的$HOME下，并设置为hdfs为其owner（我的root用户在集群内也是可以免密码登录的），这样就没问题了。

- 需要说明的是，在开启namenode之前，必须先开启journalnode，因为namenode开启时会去连接journalnode

- 然后就是开启双Namenode的步骤了，下面记录一些需要用到的命令
```
sudo -u hdfs bin/hdfs zkfc -formatZK
sudo -u hdfs sbin/hadoop-daemon.sh start journalnode #开启journalnode进程

sudo -u hdfs sbin/hadoop-daemon.sh start zkfc #开启automatic failover进程

sudo -u hdfs bin/hdfs namenode -initializeSharedEdits #把一个non-HA的NameNode转为HA时用到

sudo -u hdfs bin/hdfs namenode -bootstrapStandby 
sudo -u hdfs sbin/hadoop-daemon.sh start namenode
#上面命这两个命令在运行第二个Namenode服务器上执行，必须先执行-bootstrapStandby 这行命令再开启namenode 


#下面这些命令之前，需要以hdfs用户用kinit拿到TGT，否则会报错
sudo -u hdfs bin/hdfs haadmin -getServiceState nn1 #查看nn1是active的还是standby的

```


- 按照[jobtracker的HA官方配置](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-High-Availability-Guide/cdh5hag_jt_ha_config.html)进行配置后，使用
```
sudo -u mapred sbin/hadoop-daemon.sh start jobtrackerha
```
命令开启jobtrackerha

- 通过
```
#运行下面这些命令之前，要先以mapred用户用kinit拿到TGT，否则会报错

sudo -u mapred bin/hadoop mrhaadmin -getServiceState jt1 
```
查看jt1是active的还是standby的

- 最后一个，还是关于HDFS的权限问题，因为mapreduce在执行任务时会向HDFS上写一些临时文件，如果权限不对，肯定就会报错了，不过这种错误也很好该，根据错误信息就能知道那个目录权限不对，然后改过来就行了，我这里进行下总结：

- 根据官方的教程配置教程，配置了如下选项：
```
  <property>
    <name>mapred.job.tracker.persist.jobstatus.dir</name>
    <value>/jobtracker/jobsInfo</value>
  </property>
```
所以需要在HDFS上创建相应目录，并修改其owner为mapred

- 其次是staging目录，如果没有配置，其默认值从[默认配置](http://archive.cloudera.com/cdh4/cdh/4/hadoop/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml)可以看到mapreduce.jobtracker.staging.root.dir的值为${hadoop.tmp.dir}/mapred/staging，而${hadoop.tmp.dir}的值从[这里](http://archive.cloudera.com/cdh4/cdh/4/hadoop/hadoop-project-dist/hadoop-common/core-default.xml)可以看到值默认是/tmp/hadoop-${user.name}，有因为我们使用mapred用户来执行tasktracker进行的，所以需要创建/tmp/hadoop-mapred/mapred/staging文件夹，并且其owner为mapred，权限为1777，可以用下面的命令来实现：
```
sudo -u hdfs bin/hdfs dfs -mkdir -p /tmp/hadoop-mapred/mapred/staging
sudo -u hdfs bin/hdfs dfs -chown mapred /tmp/hadoop-mapred/mapred/staging
sudo -u hdfs bin/hdfs dfs -chmod 1777 /tmp/hadoop-mapred/mapred/staging
```
此外，还需要配置mapreduce.jobtracker.system.dir指定的文件，默认为${hadoop.tmp.dir}/mapred/system，所以还需要执行下面的命令：
```
sudo -u hdfs bin/hdfs dfs -mkdir -p /tmp/hadoop-mapred/mapred/system
sudo -u hdfs bin/hdfs dfs -chown mapred /tmp/hadoop-mapred/mapred/system

```
这个目录只由mapred用户来写入，所以不用再修改其权限（的755即可）。

总结：这次配置HA的整个过程还是比较顺利的，除了烦人的各种权限问题，我觉得这也是我没有弄明白hadoop各个进程是如何工作导致的，通过支持配置HA，算是对job的运行又有了更深的的认识。

[guide]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-High-Availability-Guide/CDH5-High-Availability-Guide.html
[apache-ha]: http://hadoop.apache.org/docs/r2.3.0/hadoop-yarn/hadoop-yarn-site/HDFSHighAvailabilityWithNFS.html
[software_config]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-High-Availability-Guide/cdh5hag_hdfs_ha_software_config.html