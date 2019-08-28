#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

LOG_ERROR() {
    content=${1}
    echo -e "\033[31m[ERROR] ${content}\033[0m"
}

LOG_INFO() {
    content=${1}
    echo -e "\033[32m[INFO] ${content}\033[0m"
}

check_cal_line()
{
    line=$1;
    if [[ $line =~ cal.[0-9]*=[0-9A-Fa-f]{128,128}$ ]]; then
        echo "true";
    else
        echo "false";
    fi
}

check_cal_lines() 
{
    # print Illegal line
    config_file=$1
    error="false"
    for line in $(grep -v "^[ ]*[;]" $config_file | grep "cal\."); do
        if [[ "true" != $(check_cal_line $line) ]]; then
            LOG_ERROR "Illigal whitelist line: $line"
            error="true"
        fi
    done 

    if [[ "true" == $error ]]; then
        LOG_ERROR "[certificate_whitelist] reload error for illigal lines"
        exit 1
    fi
}

check_duplicate_key()
{
    config_file=$1;  
    dup_key=$(grep -v '^[ ]*[;]' $config_file |grep "cal\."|awk -F"=" '{print $1}'|awk '{print $1}' |sort |uniq -d)

    if [[ "" != $dup_key ]]; then
        LOG_ERROR "[certificate_whitelist] has duplicate keys:"
        LOG_ERROR "$dup_key"
        exit 1
    fi
}

check_whitelist()
{
    config_file=$1
    check_cal_lines $config_file
    check_duplicate_key $config_file
}

check_whitelist ${SHELL_FOLDER}/../config.ini

cd ${SHELL_FOLDER}/../
NODE_FOLDER=$(pwd)
fisco_bcos=${NODE_FOLDER}/fisco-bcos
node=$(basename ${NODE_FOLDER})
node_pid=$(ps aux|grep ${fisco_bcos}|grep -v grep|awk '{print $2}')
if [ ! -z ${node_pid} ];then
    echo "${node} is trying to reset certificate whitelist. Check log for more information."
    touch config.ini.reset_certificate_whitelist
    exit 0
else 
    echo "${node} is not running, use start.sh to start and enable whitelist directlly."
fi
