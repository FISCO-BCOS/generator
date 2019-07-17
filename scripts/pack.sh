#!/bin/bash

dirpath="$(cd "$(dirname "$0")" && pwd)"
cd $dirpath

function help() {
        echo "Usage:"
        echo "    -c                  clear node dir not belong to this server "
        echo "    -d  <PATH>          work dir, default  \${dirpath}/../ , working with -p,-c option "
        echo "    -p                  pack and compress all install package "
        echo "    -i  <IP>            the install package for IP server , working with -c option "
        echo "    -h                  help "
        echo "Example:"
        echo "    bash pack.sh -p -d /data/nodeA "
        echo "    bash pack.sh -c -i 127.0.0.1 "
        exit 0
}

function pack()
{
    local workdir=$1
    # ${dir} is not exist.
    if [ ! -d ${workdir} ];then
        echo " ${workdir} not exist."
        return
    fi

    # fisco-bcos not exist.
    local fiscopath=$(ls -lt ${workdir}/*/fisco-bcos | awk '{print $9}' | head -1)
    if [ -z "${fiscopath}" ] || [ ! -f "${fiscopath}" ];then
        echo " fisco-bcos not exist, please check the workdir."
        return
    fi

    pkgname=$(basename $(readlink -f ${workdir}))
    # pack without fisco-bcos for save space
    tar --exclude=fisco-bcos -cf ${workdir}/${pkgname}.tar ${workdir}/*
    # add fisco-bcos to ${pkgname}.tar
    tar -rf ${workdir}/${pkgname}.tar ${fiscopath}
    # compress ${pkgname}.tar
    gzip ${workdir}/${pkgname}.tar
}

function clean()
{
    local workdir=$1
    local ip=$2

    local fiscopath=$(ls ${workdir}/node*/fisco-bcos 2> /dev/null | head -1)

    if [ ! -f ${fiscopath} ];then
        echo " fisco-bcos not exist. "
        return
    fi

    node_count=0
    # check if exist node dir belong to the IP server
    for configfile in ${workdir}/node*/config.ini
    do
        if [ ! -f ${configfile} ];then
            continue
        fi
        nodedir=$(dirname ${configfile})
        node=$(basename ${nodedir})
        if [[ ${node} =~ ${ip} ]];then
            ((node_count+=1))
        fi
    done

    if [ ${node_count} -eq 0 ];then
        echo " no node belong to ${ip} server, please check ip parameter."
        return
    fi

    # copy fisco-bcos first
    for configfile in  ${workdir}/node*/config.ini
    do
        if [ ! -f ${configfile} ];then
            continue
        fi
        nodedir=$(dirname ${configfile})
        cp ${fiscopath} ${nodedir} 2> /dev/null
    done

    # copy fisco-bcos first
    for configfile in  ${workdir}/node*/config.ini
    do
        if [ ! -f ${configfile} ];then
            continue
        fi
        nodedir=$(dirname ${configfile})
        node=$(basename ${nodedir})
        if [[ ${node} =~ ${ip} ]];then
            continue
        fi
        
        echo " remove ${node}, server is ${ip}"
        rm -rf ${nodedir}
    done
}

opr=""
work_dir=${dirpath}/..
while getopts "d:i:pch" option; do
        case $option in
            d) work_dir=$OPTARG ;;
            i) ip=$OPTARG ;;
            p) opr="pack" ;;
            c) opr="clean" ;;
            *) help ;;
        esac
done

if [ "${opr}" = "pack" ];then
    pack ${work_dir}
elif [ "${opr}" = "clean" ];then
    [ -z "$ip" ] && {
        help
    }
    clean ${work_dir} ${ip}
else
    help
fi
