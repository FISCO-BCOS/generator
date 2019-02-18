```
=============================================================================================
Welcome to FISCO BCOS 2.0!
 ________  ______   ______    ______    ______         _______    ______    ______    ______
|        \|      \ /      \  /      \  /      \       |       \  /      \  /      \  /      \
| $$$$$$$$ \$$$$$$|  $$$$$$\|  $$$$$$\|  $$$$$$\      | $$$$$$$\|  $$$$$$\|  $$$$$$\|  $$$$$$\
| $$__      | $$  | $$___\$$| $$   \$$| $$  | $$      | $$__/ $$| $$   \$$| $$  | $$| $$___\$$
| $$  \     | $$   \$$    \ | $$      | $$  | $$      | $$    $$| $$      | $$  | $$ \$$    \
| $$$$$     | $$   _\$$$$$$\| $$   __ | $$  | $$      | $$$$$$$\| $$   __ | $$  | $$ _\$$$$$$\
| $$       _| $$_ |  \__| $$| $$__/  \| $$__/ $$      | $$__/ $$| $$__/  \| $$__/ $$|  \__| $$
| $$      |   $$ \ \$$    $$ \$$    $$ \$$    $$      | $$    $$ \$$    $$ \$$    $$ \$$    $$
 \$$       \$$$$$$  \$$$$$$   \$$$$$$   \$$$$$$        \$$$$$$$   \$$$$$$   \$$$$$$   \$$$$$$

=============================================================================================
```

# 基本操作
相关使用见[fisco bcos企业部署工具](https://fisco-bcos-documentation.readthedocs.io/zh_CN/feature-2.0.0/docs/enterprise/index.html)

目前demo都只有非国密的，国密的证书生成尚未加入
## -h/--help
help命令
## --demo
```
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
