#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

fisco_bcos=${SHELL_FOLDER}/../fisco-bcos
cd ${SHELL_FOLDER}
node=$(basename ${SHELL_FOLDER})
node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo "${node} is trying to reset certificate whitelist. Check log for more information."
    touch config.ini.reset_certificate_whitelist
    exit 0
else 
    echo "${node} is not running, use start.sh to start and enable whitelist directlly."
fi
