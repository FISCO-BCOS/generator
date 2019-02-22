![](./images/FISCO_BCOS_Logo.svg)

**Fisco generator** 是针对多机构组网，适用于多机构部署维护多群组联盟链的企业区块链部署工具。

    - 在使用本工具时，所有机构间只需要共享节点的证书，各机构自己生成维护节点的私钥，并保证节点私钥不出内网，确保机构间节点安全性;
    - 同时提供了多种联盟链多群组间的部署方式，可以降低机构间生成与维护区块链的复杂度；
    - 基于本工具，多机构间可以通过交换数字证书，对等、安全地部署自己的节点。节点生成完成后导入私钥，启动属于本机构的节点。

# 基本操作

文档见[fisco bcos企业部署工具](https://fisco-bcos-documentation.readthedocs.io/zh_CN/feature-2.0.0/docs/enterprise/index.html)

## -h/--help

help命令
## --demo

```bash
./generator --demo
```

此操作会在执行目前的所有操作

1. 按照./conf/mchain.ini中的配置在./meta下生成证书
2. 按照./conf/mchain.ini的配置在./data下生成安装包
3. 拷贝./meta下的私钥至./data的安装包（还做了替换config.ini的操作）
4. 按照./conf/expand.ini的配置在./expand下生成扩容安装包
5. 按照./conf/mgroup.ini的配置在./data下生成group2的相关配置

操作完成后，用户可以:

1. 在./data下运行start_all.sh启动所有节点，并查看节点配置
2. 在./expand下查看扩容生成的节点
3. 在./data下查看group2的相关信息

## --build
```
./generator --build ./data
```
此操作会根据meta目录下的证书和conf/mchain.ini的配置，在data目录下生成不含私钥的安装包

目前需要把config.ini中的group_config=conf/ 修改成类似group_config.1=conf/group.1.genesis才可以启动

启动前需要拷贝私钥至对应文件夹下

## --expand
```
./generator --expand ./data ./expand
```
此操作会根据meta目录下的证书和conf/mexpand.ini的配置，读取./data下的config.ini，group信息，在expand下生成安装包

注意demo生成的证书不包含mexpand.ini中的证书，需要手动生成或者拷贝

## --create
```
./generator --create ./data
```
此操作会根据meta下的证书，在data下生成group的相关信息

# 证书生成操作

## 生成根证书
```
./generator --chainca ./test_cert
```
会在./test_cert生成根证书

## 生成机构证书
```
./generator --agency ./test_cert ./test_cert fisco
```
会在./test_cert下生成名为fisco的机构文件夹和相关证书

## 生成节点证书
```
./generator --nodeca ./test_cert ./test_cert/fisco node0
```
会在./test_cert下生成名为node0的节点文件夹和相关证书
