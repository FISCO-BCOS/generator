#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

fisco_bcos=${SHELL_FOLDER}/fisco-bcos
cd ${SHELL_FOLDER}

node=$(basename ${SHELL_FOLDER})
node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo " ${node} is running, pid is $node_pid."
    exit 0
else 
    nohup ${fisco_bcos} -c config.ini 2>>nohup.out &
    sleep 2
fi
node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo -e "\033[32m ${node} start successfully\033[0m"
else
    echo -e "\033[31m ${node} start failed\033[0m"
    cat nohup.out
    exit 1
fi