#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

for directory in $(ls ${SHELL_FOLDER})
do  
    if [[ -d "${SHELL_FOLDER}/${directory}" && -f "${SHELL_FOLDER}/${directory}/start.sh" ]];then  
        echo "start ${directory}" && bash ${SHELL_FOLDER}/${directory}/start.sh
    fi  
done 
sleep 2
