---
title: "Yarn的安全模式与高可靠性安装总结"
date: 2014-08-06 22:36:08 +0800
comments: true
categories: hadoop
tags: hadoop
---

最近几天又重新把cdh的安全模块与高可靠性模块重新搭建了一遍，这次用是的目前最新的5.1.0的tar包安装，以前把MRv1搭建了好，这次主要是熟悉安装过程，并且把YARN的安全模块与HA模块成功搭建起来。遇到的错误还是不少，安装过程也是废了我好几天，现在想想很多错误都比较典型，现在此记录下我搭建过程中遇到的错误与心得，一方面为自己以后查阅，另一方面希望也能对遇到同样问题的人有所启发。
<!--more-->
先说下我的环境，centos6.5, cdh用的目前最新的5.1.0的tar包。

下面在先说说YARN的安全模块与HA安装时的遇到的错误，之后在说说我在安装整个CDH的HDFS、MRv1、YARN时一些不容易注意但很难地位的错误。

### （一） YARN的安全模块与HA安装时遇到的错误

#### 安全模块
1. 对于container-executor文件，tar包中没有，需要自己编译
2. 按照[官方教程](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Security-Guide/cdh5sg_yarn_security.html)做配置后，执行 mapreduce 任务时，在 shuffle 阶段，会报下面的错误：
```
2014-08-03 00:34:19,619 WARN [main] org.apache.hadoop.mapred.YarnChild: Exception running child : org.apache.hadoop.mapreduce.task.reduce.Shuffle$ShuffleError: error in shuffle in fetcher#4
        at org.apache.hadoop.mapreduce.task.reduce.Shuffle.run(Shuffle.java:134)
        at org.apache.hadoop.mapred.ReduceTask.run(ReduceTask.java:376)
        at org.apache.hadoop.mapred.YarnChild$2.run(YarnChild.java:167)
        at java.security.AccessController.doPrivileged(Native Method)
        at javax.security.auth.Subject.doAs(Subject.java:415)
        at org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1554)
        at org.apache.hadoop.mapred.YarnChild.main(YarnChild.java:162)
Caused by: java.io.IOException: Exceeded MAX_FAILED_UNIQUE_FETCHES; bailing-out.
        at org.apache.hadoop.mapreduce.task.reduce.ShuffleSchedulerImpl.checkReducerHealth(ShuffleSchedulerImpl.java:323)
        at org.apache.hadoop.mapreduce.task.reduce.ShuffleSchedulerImpl.copyFailed(ShuffleSchedulerImpl.java:245)
        at org.apache.hadoop.mapreduce.task.reduce.Fetcher.copyFromHost(Fetcher.java:347)
        at org.apache.hadoop.mapreduce.task.reduce.Fetcher.run(Fetcher.java:165)        
```
在nodemanger服务器上，在执行该job的container的syslog日志中还可以找到下面的错误 
```
2014-08-03 00:34:19,614 WARN [fetcher#3] org.apache.hadoop.mapreduce.task.reduce.Fetcher: Invalid map id
java.lang.IllegalArgumentException: TaskAttemptId string : TTP/1.1 500 Internal Server Error
Content-Type: text/plain; charset=UTF is not properly formed
        at org.apache.hadoop.mapreduce.TaskAttemptID.forName(TaskAttemptID.java:201)
        at org.apache.hadoop.mapreduce.task.reduce.Fetcher.copyMapOutput(Fetcher.java:386)
        at org.apache.hadoop.mapreduce.task.reduce.Fetcher.copyFromHost(Fetcher.java:341)
        at org.apache.hadoop.mapreduce.task.reduce.Fetcher.run(Fetcher.java:165)
2014-08-03 00:34:19,614 WARN [fetcher#4] org.apache.hadoop.mapreduce.task.reduce.Fetcher: Invalid map id
java.lang.IllegalArgumentException: TaskAttemptId string : TTP/1.1 500 Internal Server Error
```
[网上很多说](http://mail-archives.apache.org/mod_mbox/hadoop-hdfs-user/201211.mbox/%3CBD42F346AE90F544A731516A805D1B8AD8548A@SMAIL1.prd.mpac.ca%3E)**Shuffle$ShuffleError: error in shuffle in fetcher#4**这个错误与内存，很明显，我这里不是这种情况，因为从** TTP/1.1 500 Internal Server Error**就应该知道是resourcemanager内部的错误。

经过我验证，这时由于tar包默认并不包含native的lib，位置在`<hadoop>/lib/native`文件夹，需要我们自己编译，把编译好的native文件拷贝到这里即可。

#### HA

按照[官方教程](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Installation-Guide/cdh5ig_yarn_cluster_deploy.html?scroll=topic_11_4_10_unique_1)，先直接安装YARN时有点小错误，就是historyserver进程开启（由maprd用户开启）后无法aggregate log，我发现是有两个问题导致：

1. 我服务器上的mapred用户只属于mapred用户组（useradd mapred这条命令执行后，就会创建mapred用户，并且属于mapred组），而由mapred启动的historyserver需要访问${yarn.app.mapreduce.am.staging-dir}/history/done_intermediate/${username}文件夹下不同用户的文件，而这个文件夹的权限是770,own为${username}:hadoop，所以historyserver没有权限读取，我这里把mapred添加到hadoop用户组去即可：s
这里mapred用户也需要属于mapred组，是因为也需要向${yarn.nodemanager.remote-app-log-dir}/${username}目录下写一些日志（因为开启了log-aggregation），而这个目录权限也是770,own为${username}:mapred。
```
usermod -a G hadoop mapred #这里需要-a选项，这样mapred用户即属于mapred组又属于hadoop组
```
2. 教程上说的开启log-aggregation的配置不对，教程上写的是
```
<property>
    <name>yarn.log.aggregation.enable</name>
    <value>true</value> 
</property>
```
应改为
```
<property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value> 
</property>
```

---------------下面正式说HA------------------

YARN的HA想对于hdfs与MRv1的简单了许多，自动Failover也不需要另起个进程，ResourceManager中一个ActiveStandbyElector，它负责Automatic failover。这里只需要修改yarn-site.xml文件即可。[官方教程](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-High-Availability-Guide/cdh5hag_rm_ha_config.html)的给出的默认配置改一项就能运行成功。

把
```
<property>
    <name>yarn.resourcemanager.zk.state-store.address</name>
    <value>localhost:2181</value>
</property>
```
改成
```
<property>
    <name>yarn.resourcemanager.zk-address</name>
    <value>localhost:2181</value>
</property>
```
其实上面的表格说的很详细了，不知道为什么给出的示例没写，不过这个错也比较好找，因为按照上面配置的开启RM时会报**yarn.resourcemanager.zk-address**没定义。

其次需要注意的是**yarn.resourcemanager.ha.id**在active与standby的服务器上的值是不一样的，按照官方给的配置，那就一个是rm1,一个是rm2。

如果我们在开启了安全模式还需要修改一处property即**yarn.resourcemanager.hostname**，ha中的两个RM这个property值是不一样的，分别为其hostname。这是因为我们在配置yarn的principal时用了**yarn/_HOST**这种方式，而_HOST对于NN与RM来说，不是按照hostname来替换的，而是分别按照**fs.defaultFS**与**yarn.resourcemanager.hostname**这两个property的值来替换的。DN与NM是按照每个服务器的hostname来替换的。替换规则也在[HDFS的安全模式文档](http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Security-Guide/cdh5sg_secure_hdfs_config.html)中有说明。

下面是我rm1服务器上这两个property的配置：
```
<property>
    <name>yarn.resourcemanager.ha.id</name>
    <value>rm1</value>
</property>
<property>
    <name>yarn.resourcemanager.hostname</name>
    <value>master</value>
</property> 
```
下面是我rm2服务器上这两个property的配置：
```
<property>
    <name>yarn.resourcemanager.ha.id</name>
    <value>rm2</value>
</property>
<property>
    <name>yarn.resourcemanager.hostname</name>
    <value>master2</value>
</property> 
```

### （二） CDH各个模块安装总结

还是先说些我在安装过程中遇到的一些不起眼但遇到后就很难定位的错误。

1. 如果把hadoop放到/root下，像hdfs、yarn这些用户是没法执行bin、sbin下面的脚本的，因为/root的默认权限是550，我安装时直接放到/opt下。
2. 在安装HDFS的安全模块时，开启某个进程，比如namenode时，经常会出现某个文件找不到，这是因为我在前后开启、关闭、格式化namenode过程中，先后用了root与hdfs，用root用户开启的namenode在本地写文件hdfs用户是没法读取的。这里一定要谨记，除了开启datanode时需要用root用户，与namenode相关的都是用hdfs用户，包括namenode的format、start与stop。
3. 还有个比较tricky的问题，本来的journalnode是开启在slaves节点上的，我现在想把它们分开，我集群内的hosts文件是这样的
```
127.0.0.1   localhost
10.4.13.85  master
10.4.15.239 master2 zk1 jn1  #hostname为master2
10.4.9.14   zk2 jn2          #hostname为zk2
10.4.14.123 zk3 jn3          #hostname为zk3
10.4.13.63  node1
10.4.13.2   node2
10.4.11.89  node3
```
我这里为一台服务器配置多个domain.name是方便我在后面的配置时做到见名知意，比如，我在配置journalnode时我可以这么配置
```
<property>
<name>dfs.namenode.shared.edits.dir</name>
<value>qjournal://jn1:8485;jn2:8485;jn3:8485/ljc</value>
</property>
<property>
<name>dfs.journalnode.kerberos.principal</name>
<value>hdfs/_HOST@MY-REALM</value>
</property>
…………
```
但这里问题来了，因为journalnode从active的NameNode那里取数据时需要验证身份，而我这里的principal用了**_HOST**，按理说CDH在运行时会自动把 _HOST替换为hostname，而且我在生产keytab时也是根据hostname来生成的，比如对于master2,我会生产下面的principal：
```
hdfs/master2@MY-REALM
HTTP/master2@MY-REALM
mapred/master2@MY-REALM
yarn/master2@MY-REALM
```
但是我这样配置后，开启第一个时namenode就会报错，
```
2014-08-06 18:27:05,929 WARN org.apache.hadoop.security.UserGroupInformation: PriviledgedActionException as:hdfs/master@MY-REALM (auth:KERBEROS) cause:java.io.IOException: org.apache.hadoop.security.authentication.client.AuthenticationException: GSSException: No valid credentials provided (Mechanism level: Server not found in Kerberos database (7) - UNKNOWN_SERVER)
2014-08-06 18:27:05,929 ERROR org.apache.hadoop.hdfs.server.namenode.EditLogInputStream: caught exception initializing http://jn3:8480/getJournal?jid=ljc&segmentTxId=1&storageInfo=-55%3A845458164%3A0%3ACID-b6f3e623-e3c0-45d0-a44c-ec3f01d57ea3
java.io.IOException: org.apache.hadoop.security.authentication.client.AuthenticationException: GSSException: No valid credentials provided (Mechanism level: Server not found in Kerberos database (7) - UNKNOWN_SERVER)
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream$URLLog$1.run(EditLogFileInputStream.java:406) 
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream$URLLog$1.run(EditLogFileInputStream.java:398)
    at java.security.AccessController.doPrivileged(Native Method)
    at javax.security.auth.Subject.doAs(Subject.java:415)
    at org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1554)
    at org.apache.hadoop.security.SecurityUtil.doAsUser(SecurityUtil.java:448)
    at org.apache.hadoop.security.SecurityUtil.doAsCurrentUser(SecurityUtil.java:442)
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream$URLLog.getInputStream(EditLogFileInputStream.java:397)
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream.init(EditLogFileInputStream.java:139)
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream.nextOpImpl(EditLogFileInputStream.java:188)
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream.nextOp(EditLogFileInputStream.java:239)
    at org.apache.hadoop.hdfs.server.namenode.EditLogInputStream.readOp(EditLogInputStream.java:83)
    at org.apache.hadoop.hdfs.server.namenode.EditLogInputStream.skipUntil(EditLogInputStream.java:140)
    at org.apache.hadoop.hdfs.server.namenode.RedundantEditLogInputStream.nextOp(RedundantEditLogInputStream.java:178)
    at org.apache.hadoop.hdfs.server.namenode.EditLogInputStream.readOp(EditLogInputStream.java:83)

Caused by: org.apache.hadoop.security.authentication.client.AuthenticationException: GSSException: No valid credentials provided (Mechanism level: Server not found in Kerberos database (7) - UNKNOWN_SERVER)
    at org.apache.hadoop.security.authentication.client.KerberosAuthenticator.doSpnegoSequence(KerberosAuthenticator.java:306)
    at org.apache.hadoop.security.authentication.client.KerberosAuthenticator.authenticate(KerberosAuthenticator.java:196)
    at org.apache.hadoop.security.authentication.client.AuthenticatedURL.openConnection(AuthenticatedURL.java:232)
    at org.apache.hadoop.hdfs.web.URLConnectionFactory.openConnection(URLConnectionFactory.java:164)
    at org.apache.hadoop.hdfs.server.namenode.EditLogFileInputStream$URLLog$1.run(EditLogFileInputStream.java:403)
    ... 30 more
Caused by: GSSException: No valid credentials provided (Mechanism level: Server not found in Kerberos database (7) - UNKNOWN_SERVER)
    at sun.security.jgss.krb5.Krb5Context.initSecContext(Krb5Context.java:710)
    at sun.security.jgss.GSSContextImpl.initSecContext(GSSContextImpl.java:248)
    at sun.security.jgss.GSSContextImpl.initSecContext(GSSContextImpl.java:179)
    at org.apache.hadoop.security.authentication.client.KerberosAuthenticator$1.run(KerberosAuthenticator.java:285)
    at org.apache.hadoop.security.authentication.client.KerberosAuthenticator$1.run(KerberosAuthenticator.java:261)
    at java.security.AccessController.doPrivileged(Native Method)
    at javax.security.auth.Subject.doAs(Subject.java:415)

```
大致意思是说无法读取journalnode那里的edits，认证失败了，没有权限。我还以为是我生产的keytab有错，我去jn1所在服务器（hostname为master2）上用kinit加上tabkey也能的到TGT，后来我把配置改成这样：
```
<property>
<name>dfs.namenode.shared.edits.dir</name>
<value>qjournal://master2:8485;zk2:8485;zk3:8485/ljc</value>
</property>
```
这样就能吧Namenode起来了，证明这里**_HOST**被直接替换成了我这里的domain.name了，而不是每个服务器上的hostname，我这里不用domain.name，直接换为ip，也没问题。要是想了解这个细节，需要看源代码了，以后在看吧。
4. 如果遇到
```
Exception in thread "main" org.apache.hadoop.HadoopIllegalArgumentException: HA is not enabled for this namenode.
        at org.apache.hadoop.hdfs.tools.DFSZKFailoverController.create(DFSZKFailoverController.java:121)
        at org.apache.hadoop.hdfs.tools.DFSZKFailoverController.main(DFSZKFailoverController.java:172)
```
说明 **dfs.nameservices** 配置有误，我当时把值配置成 **hdfs://ljc** 了，其实应该配成 **ljc** 就可以了。

## 总结

从熟悉hadoop各个模块开始，到现在把最基本的环境搭建起来，前前后后也是有一个月的时间了，我发现我耗时比较多的是遇到问题后，没有看源码的意识，去网上搜，虽然有可能有人也遇到这个问题，但是明显和我的不相符，这时我就仔细检查我的配置文件，看看是否遗漏官方教程上的某一项，有些盲目，最近开始把cdh的src导入了eclipse，遇到一些错误后开始慢慢看源代码，我发现这样能很快定位到问题出错的范围，以后一定多尝试。

其次就是服务器比较多，hadoop也需要配置不少东西，这就需要自动化来帮助了，我最近把shell脚本又熟悉起来，写了一些用于管理hadoop的脚本，加上使用了[salt][]这个自动化工具，这样方便多了。但是shell我还不是很熟悉，像数组的使用，很恶心有木有，交互式shell加载环境变量与非交互式（ssh -t -t hostname cmd这种方式就是非交互式）的不一样，等回来还要慢慢总结。

[salt]: http://en.wikipedia.org/wiki/Salt_(software)