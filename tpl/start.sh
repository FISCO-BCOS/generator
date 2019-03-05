#!/bin/bash
SHELL_FOLDER=$(cd $(dirname $0);pwd)

fisco_bcos=${SHELL_FOLDER}/fisco-bcos
cd ${SHELL_FOLDER}

function check_port()
{
    type nc >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "ERROR - nc is not installed."
        return
    fi

    nc -z 127.0.0.1 $1 >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "$1 is listening."
    else
        echo "$1 is not listening."
    fi
}

function check_port_use()
{
    type nc >/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "ERROR - nc is not installed."
        return 0 
    fi

    nc -z 127.0.0.1 $1 >/dev/null 2>&1
    if [ $? -eq 0 ];then
        # echo "port $1 has been using."
        return 0
    else
        return 1
    fi
}

node=$(basename ${SHELL_FOLDER})
channelPort=`cat ${SHELL_FOLDER}/config.ini | grep channel_listen_port | awk '{print $3}' | tr -cd "[0-9]"`
rpcport=`cat ${SHELL_FOLDER}/config.ini | grep jsonrpc_listen_port | awk '{print $3}' | tr -cd "[0-9]"`
p2pport=`cat ${SHELL_FOLDER}/config.ini | grep -w listen_port | awk '{print $3}' | tr -cd "[0-9]"`
ulimit -c unlimited 2>/dev/null
node_pid=`ps aux|grep "${fisco_bcos}"|grep -v grep|awk '{print $2}'`
if [ ! -z $node_pid ];then
    echo " ${node} is running, pid is $node_pid."
else 
    # port check
    check_port_use $channelPort 
    if [ $? -eq 0 ];then
        echo " ${node} channel port $channelPort already in use."
        exit 0
    fi
    check_port_use $rpcport
    if [ $? -eq 0 ];then
        echo " ${node} rpc port $rpcport already in use."
        exit 0
    fi
    check_port_use $p2pport
    if [ $? -eq 0 ];then
        echo " ${node} p2p port $p2pport already in use."
        exit 0
    fi
    
    if [ ! -f "$fisco_bcos" ]; then
        echo "$fisco_bcos not existed!"
    else
        chmod u+x ${fisco_bcos}
        version=`${fisco_bcos} -v | grep Version | awk '{print $4}'`
        echo ${version}
        echo ${version:0:1}
        if [[ ${version:0:1} -ne "2" ]];then
            echo "fisco bcos not support, now version is:"
            ${fisco_bcos} -v
        fi    
        echo " start ${node} ..."
        nohup  ${fisco_bcos} -c config.ini
        node_pid=`ps aux|grep "${fisco_bcos}"|grep -v grep|awk '{print $2}'`
        if [ ! -z ${node_pid} ];then
            echo " ${node} start successfully"
        else
            echo " ${node} start failed"
            cat nohup.out
        fi
    fi
fi