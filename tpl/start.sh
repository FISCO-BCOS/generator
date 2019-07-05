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
    nohup ${fisco_bcos} -c config.ini >>nohup.out 2>&1 &
    sleep 1.5
fi
try_times=4
i=0
while [ $i -lt ${try_times} ]
do
    node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
    success_flag=$(tail -n20  nohup.out | grep running)
    if [[ ! -z ${node_pid} && ! -z "${success_flag}" ]];then
        echo -e "\033[32m ${node} start successfully\033[0m"
        exit 0
    fi
    sleep 0.5
    ((i=i+1))
done
echo -e "\033[31m  Exceed waiting time. Please try again to start ${node} \033[0m"
tail -n20  nohup.out
exit 1
