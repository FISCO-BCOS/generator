#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

cd ${SHELL_FOLDER}/../
NODE_FOLDER=$(pwd)
fisco_bcos=${NODE_FOLDER}/fisco-bcos
node=$(basename ${NODE_FOLDER})
node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo "${node} is trying to load new groups. Check log for more information."
    touch config.ini.append_group
    sleep 1
    DATA_FOLDER=${NODE_FOLDER}/data
    for dir in $(ls "${DATA_FOLDER}")
    do
        if [[ -d "${DATA_FOLDER}/${dir}" ]]; then
            if [[ -n "$(echo "${dir}" | grep -E "^group\d+$")" ]] || [[ -n "$(echo "${dir}" | grep -P "^group\d+$")" ]]; then
                STATUS_FILE=${DATA_FOLDER}/${dir}/.group_status
                if [ ! -f "${STATUS_FILE}" ]; then
                    echo "STOPPED" > "${STATUS_FILE}"
                fi
            fi
        fi
    done
    exit 0
else 
    echo "${node} is not running, use start.sh to start all group directlly."
fi
