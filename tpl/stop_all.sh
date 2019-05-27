#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

dirs=($(ls -l ${SHELL_FOLDER} | awk '/^d/ {print $NF}'))
for directory in ${dirs[*]}  
do  
    if [[ -d "${SHELL_FOLDER}/${directory}" && -f "${SHELL_FOLDER}/${directory}/stop.sh" ]];then  
        echo "try to stop ${directory}"
        bash ${SHELL_FOLDER}/${directory}/stop.sh &
    fi  
done  
wait