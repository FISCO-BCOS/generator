# FISCO BCOS GENERATOR 容器镜像

镜像制作过程中需要从 github 下载内容，如遇网络问题导致失败，请重试。第一次制作的耗时很长，请耐心等待。

## x86_64 平台

```
docker build -f Dockerfile-amd64 -t fisco-bcos-generator .
```

## aarch64 平台

```
docker build -f Dockerfile-aarch64 -t fisco-bcos-generator .
```

## 制作成功后，可使用 docker compose 启动一个持久容器

```
docker-compose up -d || docker compose up -d
```

## 进入容器执行 generator 相关操作

```
docker exec -it fisco-bcos-generator bash
```