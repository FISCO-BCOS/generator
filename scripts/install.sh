#!/bin/bash
# "Copyright [2019] <fisco generator>"
# @ function : one-click install shell script(appliable for centos, ubuntu)
# @ Require  : yum ,apt and python are ready
#              and execute this shell script later
# @ author   : asherli
# @ file     : install.sh
# @ date     : 2019

SHELL_FOLDER=$(cd $(dirname $0);pwd)
project_dir="${SHELL_FOLDER}/.."
use_cores=1
test_mode=0
Ubuntu_Platform=0
Centos_Platform=1
Macos_Platform=2

# check sudo permission
function sudo_permission_check() 
{
    # sudo echo -n " "

    # if [ $? -ne 0 ]; then
    if ! sudo echo -n " "
    then
        echo "no sudo permission, please add youself in the sudoers"; exit 1;
    fi
}

clear_cache()
{ 
    cd ${project_dir}
    execute_cmd "rm -rf deps/src/*stamp"
}

LOG_ERROR()
{
    content=${1}
    echo -e "\033[31m${content}\033[0m"
}

LOG_INFO()
{
    content=${1}
    echo -e "\033[32m${content}\033[0m"
}

execute_cmd()
{
    command="${1}"
    #LOG_INFO "RUN: ${command}"
    eval ${command}
    ret=$?
    if [ $ret -ne 0 ];then
        LOG_ERROR "FAILED execution of command: ${command}"
        # clear_cache
        exit 1
    else
        LOG_INFO "SUCCESS execution of command: ${command}"
    fi
}

# get platform: now support debain/ubuntu, fedora/centos, oracle
get_platform()
{
    uname -v > /dev/null 2>&1 || { echo >&2 "ERROR - Require 'uname' to identify the platform."; exit 1; }
    case $(uname -s) in
    Darwin)
        LOG_ERROR "Not Support mac OS Yet!"
        exit 1;;
    FreeBSD)
        LOG_ERROR "Not Support FreeBSD Yet!"
        exit 1;;
    Linux)
        if [ -f "/etc/arch-release" ];then
            LOG_ERROR "Not Support arch-linux Yet!"
        elif [ -f "/etc/os-release" ];then
            DISTRO_NAME=$(. /etc/os-release; echo $NAME)
            case $DISTRO_NAME in
            Debian*|Ubuntu)
                LOG_INFO "Debian*|Ubuntu Platform"
                return ${Ubuntu_Platform};; #ubuntu type
            Fedora|CentOS*)
                LOG_INFO "Fedora|CentOS* Platform"
                return ${Centos_Platform};; #centos type
            Oracle*)
                LOG_INFO "Oracle Platform"
                return ${Centos_Platform};; #oracle type
            esac
        else
            LOG_ERROR "Unsupported Platform"
        fi
    esac
}

install_all_deps()
{
    get_platform
    platform=`echo $?`
    # platform=$(get_platform)
    if [ ${platform} -eq ${Ubuntu_Platform} ];then
        sudo apt-get install python-pip
        sudo apt-get -y install curl
        sudo apt-get -y install openssl
        sudo apt-get -y install nc
    elif [ ${platform} -eq ${Centos_Platform} ];then
        sudo yum install python-pip
        sudo yum -y install openssl
        sudo yum -y install nc
        sudo yum -y install curl
    else
        LOG_ERROR "Unsupported Platform"
        exit 1
    fi
}

install_all()
{
    sudo_permission_check
	install_all_deps
    pip install configparser --user
    py_version=$($python_env -V 2>&1 | awk {'print $2'} | awk -F. {' print $1"."$2"."$3 '})
    py_pip=$(pip -V 2>&1 | awk {'print $2'} | awk -F. {' print $1"."$2"."$3 '})

    # params check
    if [ -z "${py_version}" ];then
        alarm " not invalid python path, path is ${python_env}."; exit 1;
    fi
}

install_all