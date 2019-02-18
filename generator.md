# FISCO generator

# 设计背景
fisco generator是针对多机构组网的企业区块链部署工具。 在使用时，本工具会根据用户配置的配置文件（包含节点的hostip，端口号等信息），及meta目录下用户存放的符合规范的节点证书，生成节点所需启动的安装包。用户生成安装包后，导入私钥，既可以启动节点。同时允许可以使用本工具及目录下的证书，生成新group的相关配置，用户将生成的配置文件拷贝至对应节点下，节点会进行group组网

注1：与1.3不同，fisco generator生成的安装包以node为单位，一个node为一个安装包，原则上不建议一台服务器部署多个节点

注2：本文档中提及的节点证书，均为同一委员会(ca.crt）签发的证书
## 应对场景
按照现有业务，可以将场景分为以下四种，分别是以下四种场景

### 起始组网
ABC三个对等机构需要沟通搭建一条链，开始时只需要一个账本，需要生成安装包，启动节点，初始化一个业务。操作步骤如下：

1. A B C三个机构共享自己的节点证书，节点信息（包括hostip，p2pip，端口号等），由某一机构统一收集（或都收集）
2. 假设A收集所有资料后，将证书按照cert_hostip_litsenport的格式放在meta目录下，并配置[mchain.ini](见配置文件)中的node信息，指定配置文件中的groupid
3. A机构执行build命令，指定生成安装包的目录，会在指定目录下生成多个名为node_hostip_litsenport.tar.gz如 node_127.0.0.1_30301.tar.gz的安装包（或就是一个文件夹）
4. A机构将生成的安装包分发给BC机构，并将自己的安装包推送至对应服务器，拷贝node.key至安装包的/conf文件夹下，启动节点，默认节点加入的群组为mchain.ini的groupid

考虑场景：是否每个机构都收集信息，生成所有包，但是只推送自己的（地位对等），该操作对generator的实现没有影响

### 新节点加入网络
新节点加入网络有两种情况，场景如下：
#### 新节点加入现有group
在本场景中，节点需要与所有原有节点进行网络连接，并且需要加入现有群组，以上述[起始组网]()为例，操作步骤如下：
假设D机构需要新加入节点到ABC的组网的group1中（ABC加入节点在网络中同理）
1. D机构收集ABC组网生成的config.ini 与 group.1.genesis，group.1.ini文件，统一放置与某一文件夹下，如./node_conf
2. D机构配置[mexpand.ini]中的节点信息（包括hostip，p2pip，端口号等），将证书按照cert_hostip_litsenport的格式放在meta目录下
3. D机构使用expand命令指定./node_conf路径和输出路径，在输出路径生成多个名为node_hostip_litsenport的文件夹
4. D机构将导入私钥，将安装包推送至指定服务器，启动节点
5. D机构请求ABC中的某一个机构将自己的节点注册如group1中，完成新节点入网操作

#### 新节点创建新group
在本场景中，节点只需要与链中的某几个节点进行网络连接，并且不需要加入原有群组,以上述[起始组网]()为例，假设EF机构需要与C机构组网，新建一个group，对于C机构而言，不需要再从新搭建一条链，直接服用[起始组网]中的节点，新建群组即可满足需求

操作步骤类似于[起始组网]：

1. C E F三个机构共享自己的节点证书，节点信息（包括hostip，p2pip，端口号等），由某一机构统一收集（或都收集）
2. 假设C收集所有资料后，将证书按照cert_hostip_litsenport的格式放在meta目录下，并配置[mchain.ini](见配置文件)中的node信息，指定配置文件中的groupid（注意，不能与C在group1中的相同）
3. C机构执行build命令，指定生成安装包的目录，会在指定目录下生成多个名为node_hostip_litsenport.tar.gz如 node_127.0.0.1_30301.tar.gz的安装包（或就是一个文件夹）
4. C机构将生成的安装包分发给EF机构，EF收到安装包之后，启动节点
5. C机构将新生成的group信息如group.2.genesis，group.2.ini文件，放置与原有节点的conf文件夹下，完成新节点创建和新群组建立操作

### 节点新建群组
在本场景中，链中的已有节点需要建立新群组，如何已经生成链接的节点之前没有建立网络链接，则交换config.ini文件，同步网络链接列表

假设节点均已建立为网络链接，先要建立新群组，如上述场景中ABCD要新建立group3，则需要进行的操作如下：

1. ABCD中交换节点证书，设A收集完成后，按照cert_hostip_litsenport的格式放在meta目录下（）
2. A配置[mgroup.ini]中的信息，（是否要在这里填写groupmember信息）
3. A执行create命令，生成group.i.genesis和group.i.ini，将group.i.genesis和group.i.ini交换给BCD
4. ABCD将生成group.i.genesis和group.i.ini拷贝到节点的conf/文件夹下，完成新群组的建立

### 复杂网络组网
针对于目前考虑的星型网络，海星网络，混合网络等都可以简化为上述三种形式，见[PPT]

# 实现方案

## 基础命令
基础命令为2.0组网命令，由着三种命令组合应对2.0中面临的各种组网模式
### --build 
生成安装包

nargs=1， 指定参数为安装包输出路径，用户需配置mchain.ini  ----可用于区块链生成后，创建新群组和新节点的场景

给定节点证书，和节点信息（端口号，ip），生成安装包，并加入一个群里，将打好的包生成到指定目录

操作范例

```
$ https://github.com/HaoXuan40404/generator.git
$ cd generator
$ cp node0/node.crt ./meta/cert_127.0.0.1_30303.crt
...
$ cp noden/node.crt ./meta/cert_192.168.1.1_30308.crt
$ vim ./conf/mchain.ini
$ ./generator --build ~/mydata
```
程序执行完成后，会在~/mydata文件夹下生成多个名为node_hostip_litsenport.tar.gz的安装包，推送到对应服务器解压后，拷贝私钥到conf下即可启动节点

### --expand
扩容节点并加入已有群组

nargs=2, 指定参数1.存放有原有群组信息的路径，2.生成安装包的路径  用户需配置mexpand.ini

给定原有group中节点的配置，和新节点的证书，生成安装包

```
$ https://github.com/HaoXuan40404/generator.git
$ cd generator
$ cp node0/node.crt ./meta/cert_127.0.0.1_30307.crt
$ cp /tmp/config.ini /tmp/group.1.genesis /tmp/group.1.ini ./expand
$ vim ./conf/mexpand.ini
$ ./generator --expand ./expand ~/mydata
```
程序执行完成后，会在~/mydata文件夹下生成名为node_127.0.0.1_30307.tar.gz的安装包，推送到对应服务器解压后，拷贝私钥到conf下即可启动节点

节点正常启动后，使用sdk将节点加入群组，完成扩容操作

**这里是否要考虑下只生成空白的安装包，如果要加入某个群组让他自己拷贝group的配置进去**

**这样设计的原因是如果要扩容一种能够和其他节点进行网络连接的新节点，那么这个节点从逻辑上也是要加入到现有群组的。如果扩容的节点不需要与（与其他节点）网络连接，使用build命令即可**

### --create
已有节点新建群组

nargs=1 指定参数为生成的group.i.genesis和group.i.ini的存放路径

给定节点的证书，配置mgroup.ini，生成新群组的group.i.genesis和group.i.ini

操作范例

```
$ https://github.com/HaoXuan40404/generator.git
$ cd generator
$ cp node0/node.crt ./meta/cert_127.0.0.1_30307.crt
...
$ cp noden/node.crt ./meta/cert_192.168.1.1_30308.crt
$ vim ./conf/group.ini
$ ./generator --create ~/mydata
```
程序执行完成后，会在~/mydata文件夹下生成mgroup.ini中配置的group.i.genesis和group.i.ini
### 其他后续命令
证书生成， 维护管理自己的包等

## 配置文件

### mchain.ini
```
# 生成包的配置
[node0]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
p2p_listen_port=30300
channel_listen_port=20200
jsonrpc_listen_port=8545

[node1]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
p2p_listen_port=30301
channel_listen_port=20201
jsonrpc_listen_port=8546

[node2]
p2p_ip=192.168.1.1
rpc_ip=127.0.0.1
p2p_listen_port=30300
channel_listen_port=20200
jsonrpc_listen_port=8545
# 生成的时候检测端口

[group]
# group id
group_id=1
```
### mexpand.ini
```
# expand命令 必须指定group.i.gensis  group.i.ini 和config.ini
;port config, in general, use the default values
[[node0]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
p2p_listen_port=30300
channel_listen_port=20200
jsonrpc_listen_port=8545

[node1]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
p2p_listen_port=30301
channel_listen_port=20201
jsonrpc_listen_port=8546
```
### mgroup.ini
```
[group]
; group : group index
group_id=2
member0=127.0.0.1:30303
member1=127.0.0.1:30304
member2=192.169.1.1:30303
```
## 所需运维介入操作
当完成扩容操作后，需要运维介入并修改设计连接节点的config.ini配置

分为3种场景
1. expand扩容，需要修改现有group所有节点的config.ini
2. build扩容，需要修改原有交集节点的config.ini
3. 原有节点之前不需要互联，后续需要网络连接，如上述场景中A和F一段时间后需要互联，则需要更新A和F节点的config.ini

如果原有节点的群组有新成员的加入，则都需要修改原有节点的config.ini（网络健壮性角度考虑）

# 现有项目所需改动

## 底层改动
读取groupid的逻辑，需要从group.genesis中读取，删除config.ini中的groupid

## build_chain.sh改动

node名称统一，生成的端口号统一，生成group.i.genesis时需要统一加入groupid

# 考虑问题

## 运营方

怎么样最简单，运维介入能最少，如果出了问题能最快解决，并且不影响在线业务

## 参与方

我的数据是否安全，我的隐私需求有没有被保护，我偷偷参加的，不想让别人知道，我也不太关注别人的群组，不想维护别的群组的信息
## 监管方

只要能让我看到业务的数据符合要求就行了，其他我不管

## 需求总结

1. 操作简单和安全性的权衡
2. 观察节点的介入是否需要修改业务节点的config信息
3. 新群组的加入最好不要影响已经再跑的业务，尽量不要让节点重启
4. 不同群组之间的节点没有连接的需求
5. 生成安装包时地位应该对等，谁都可以生成安装包

## 网络中存在多个同名group可能遇到的问题

考虑场景中，ABC维护了一个group1,CDE维护了group2，DE并不知道group1的存在，一段时间后，F加入group2，并且DEF又拉了一个名为group1的群组。这是链中存在了两个group1，正常情况下ABC的group1和DEF的group1没有交集，但假设F为监管，需要加入ABC的group1时会遇到group名相同的问题，导致节点异常


# 本工具优劣分析

## 优势

1. 所有操作中参与方均是对等的，机构可以协商各自生成自己的安装包，或者由某一机构生成所有的安装包进行分发，各机构参与度较高
2. 生成安装包不包含节点的私钥信息，保障机构节点的安全性
3. 机构间可以自由的新建群组，新建群组对外无感知，满足机构内的隐私诉求

## 劣势
1. 涉及新节点增加时，需要运维介入更新原有节点的config.ini

1.3证书系统保持不变
2.0 证书：
文件修改：

1. p12文件默认不要密码 目前不需要client.keystore 不需要keytools
2. node.crt需要合成 存放顺序为node.crt agency.crt ca.crt
3. 底层加载只需要ca.crt node.key 和合成好的node.crt 以及给运维的node.nodeid 其他统一

依赖项减少：

1. 2.0 支持LibreSSL
2. 不依赖java
3. --force最好去掉

todoList:

1. 拉静态 （目前build命令只拉最新的标准版）
2. 写文档
3. 国密证书 国密demo
4. python ci（目前只有circleci 其他的需要等repo public）
5. 监控脚本
6. 管理工具（ansible）
7. 重复代码检测
8. sdk配置
11. solidity changelog搬迁
12. 相同端口检测 （拿出第二个字段判断是否重复）