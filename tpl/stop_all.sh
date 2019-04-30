#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

for directory in $(ls ${SHELL_FOLDER})
do  
    if [[ -d "${SHELL_FOLDER}/${directory}" && -f "${SHELL_FOLDER}/${directory}/stop.sh" ]];then  
        echo "try to stop ${directory}"
        bash ${SHELL_FOLDER}/${directory}/stop.sh &
    fi  
done
sleep 3
