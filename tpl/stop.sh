#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

fisco_bcos=${SHELL_FOLDER}/fisco-bcos
node=$(basename ${SHELL_FOLDER})
node_pid=$(ps aux|grep ${fisco_bcos} |grep -v grep|awk '{print $2}')
try_times=5
i=0
while [ $i -lt ${try_times} ]
do
    if [ -z ${node_pid} ];then
        echo " ${node} isn't running."
        exit 0
    fi
    [ ! -z ${node_pid} ] && kill ${node_pid} 2> /dev/null
    sleep 0.6
    node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
    if [ -z ${node_pid} ];then
        echo -e "\033[32m stop ${node} success.\033[0m"
        exit 0
    fi
    ((i=i+1))
done
echo " stop ${node} failed, exceed maximum number of retries."

