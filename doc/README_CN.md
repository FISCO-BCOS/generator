![](https://github.com/FISCO-BCOS/FISCO-BCOS/raw/master/docs/images/FISCO_BCOS_Logo.svg?sanitize=true)

[English](../README.md) / 中文

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/be1e9f1c699e4275a97d202cec9ae1e0)](https://www.codacy.com/app/fisco/generator?utm_source=github.com&utm_medium=referral&utm_content=FISCO-BCOS/generator&utm_campaign=Badge_Grade) [![CodeFactor](https://www.codefactor.io/repository/github/fisco-bcos/generator/badge)](https://www.codefactor.io/repository/github/fisco-bcos/generator)
[![CircleCI](https://circleci.com/gh/FISCO-BCOS/generator.svg?style=shield)](https://circleci.com/gh/FISCO-BCOS/generator) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Build Status](https://travis-ci.org/FISCO-BCOS/generator.svg?branch=master)](https://travis-ci.org/FISCO-BCOS/generator)
---

**FISCO BCOS generator** 是针对多机构组网，适用于多机构部署，维护多群组联盟链的企业区块链部署工具。**此版本只支持**[FISCO BCOS 2.0](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/)。

-   本工具降低了机构间生成与维护区块链的复杂度，提供了多种常用的部署方式。
-   本工具考虑了机构间节点安全性需求，所有机构间仅需要共享节点的证书，同时对应节点的私钥由各机构自己维护，不需要向机构外节点透露。
-   本工具考虑了机构间节点的对等性需求，多机构间可以通过交换数字证书对等安全地部署自己的节点。

文档见[FISCO BCOS 企业部署工具](https://fisco-bcos-documentation.readthedocs.io/zh_CN/latest/docs/enterprise_tools/index.html)。

## 贡献代码
欢迎参与FISCO BCOS的社区建设：
- 点亮我们的小星星(点击项目左上方Star按钮)。
- 提交代码(Pull requests)，参考我们的[代码贡献流程](CONTRIBUTING_CN.md)。
- [提问和提交BUG](https://github.com/FISCO-BCOS/generator/issues)。

## 加入我们的社区

FISCO BCOS开源社区是国内活跃的开源社区，社区长期为机构和个人开发者提供各类支持与帮助。已有来自各行业的数千名技术爱好者在研究和使用FISCO BCOS。如您对FISCO BCOS开源技术及应用感兴趣，欢迎加入社区获得更多支持与帮助。

![](https://media.githubusercontent.com/media/FISCO-BCOS/LargeFiles/master/images/QR_image.png)

## License

![license](https://img.shields.io/badge/license-Apache%20v2-blue.svg)

generator的开源协议为[Apache License 2.0](http://www.apache.org/licenses/). 详情参考[LICENSE](../LICENSE)。