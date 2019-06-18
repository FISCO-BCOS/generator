#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

dirs=($(ls -l ${SHELL_FOLDER} | awk '/^d/ {print $NF}'))
for directory in ${dirs[*]} 
do  
    if [[ -f "${SHELL_FOLDER}/${directory}/config.ini" && -f "${SHELL_FOLDER}/${directory}/start.sh" ]];then  
        echo "try to start ${directory}"
        bash ${SHELL_FOLDER}/${directory}/start.sh &
    fi  
done  
wait
