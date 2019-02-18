#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)
node=$(basename ${SHELL_FOLDER})
fisco_bcos=${SHELL_FOLDER}/fisco-bcos
weth_pid=`ps aux|grep "${fisco_bcos}"|grep -v grep|awk '{print $2}'`
kill_cmd="kill ${weth_pid}"
if [ ! -z $weth_pid ];then
    echo " stop ${node} ..."
    eval ${kill_cmd}
else
    echo " ${node} is not running."
fi
