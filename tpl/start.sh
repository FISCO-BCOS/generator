#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

fisco_bcos=${SHELL_FOLDER}/fisco-bcos
cd ${SHELL_FOLDER}

node=$(basename ${SHELL_FOLDER})
node_pid=$(ps aux|grep "${fisco_bcos}"|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo " ${node} is running, pid is $node_pid."
    exit 0
else 
    nohup ${fisco_bcos} -c config.ini&
fi
node_pid=$(ps aux|grep "${fisco_bcos}"|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo " ${node} start successfully"
else
    echo " ${node} start failed"
    cat ${node}/nohup.out
fi