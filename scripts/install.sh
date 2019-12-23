#!/bin/bash
# "Copyright [2019] <fisco generator>"
# @ function : one-click install shell script(appliable for centos, ubuntu)
# @ Require  : yum ,apt and python are ready
#              and execute this shell script later
# @ author   : asherli
# @ file     : install.sh
# @ date     : 2019

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)
project_dir="${SHELL_FOLDER}/.."
# use_cores=1
# test_mode=0
Ubuntu_Platform=0
Centos_Platform=1
# Macos_Platform=2


# check sudo permission
sudo_permission_check() {
    if ! sudo echo -n " "; then
        echo "no sudo permission, please add yourself in the sudoers"
        exit 1
    fi
}

clear_cache() {
    cd ${project_dir}
    execute_cmd "rm -rf deps/src/*stamp"
}

LOG_ERROR() {
    content=${1}
    echo -e "\033[31m${content}\033[0m"
}

LOG_INFO() {
    content=${1}
    echo -e "\033[32m${content}\033[0m"
}

execute_cmd() {
    command="${1}"
    #LOG_INFO "RUN: ${command}"
    eval ${command}
    ret=$?
    if [ $ret -ne 0 ]; then
        LOG_ERROR "FAILED execution of command: ${command}"
        # clear_cache
        exit 1
    else
        LOG_INFO "SUCCESS execution of command: ${command}"
    fi
}

# get platform: now support debain/ubuntu, fedora/centos, oracle
get_platform() {
    uname -v >/dev/null 2>&1 || {
        echo >&2 "ERROR - Require 'uname' to identify the platform."
        exit 1
    }
    case $(uname -s) in
    Darwin)
        LOG_ERROR "Not Support mac OS Yet!"
        exit 1
        ;;
    FreeBSD)
        LOG_ERROR "Not Support FreeBSD Yet!"
        exit 1
        ;;
    Linux)
        if [ -f "/etc/arch-release" ]; then
            LOG_ERROR "Not Support arch-linux Yet!"
        elif [ -f "/etc/os-release" ]; then
            DISTRO_NAME=$(
                . /etc/os-release
                echo $NAME
            )
            case $DISTRO_NAME in
            Debian* | Ubuntu)
                LOG_INFO "Debian*|Ubuntu Platform"
                return ${Ubuntu_Platform}
                ;; #ubuntu type
            Fedora | CentOS*)
                LOG_INFO "Fedora|CentOS* Platform"
                return ${Centos_Platform}
                ;; #centos type
            Oracle*)
                LOG_INFO "Oracle Platform"
                return ${Centos_Platform}
                ;; #oracle type
            esac
        else
            LOG_ERROR "Unsupported Platform"
            exit 1
        fi
        ;;
    esac
}

install_all_deps() {
    get_platform
    platform=$(echo $?)
    # platform=$(get_platform)
    if [ ${platform} -eq ${Ubuntu_Platform} ]; then
        sudo apt-get -y install python-pip curl openssl
        # sudo apt-get -y install nc
    elif [ ${platform} -eq ${Centos_Platform} ]; then
        sudo yum install -y python-pip openssl curl which
    else
        LOG_ERROR "Unsupported Platform"
        exit 1
    fi
}

install_deps() {
    # sudo_permission_check
    install_all_deps
}

install_all() {
    sudo_permission_check
    install_deps
    # pip install configparser --user
    export LC_ALL=C && pip install --user -r requirements.txt
    # export LC_ALL=C && pip install -r requirements.txt
    python_env=$(which python)
    py_version=$($python_env -V 2>&1 | awk {'print $2'} | awk -F. {' print $1 '})

    py_pip=$(pip -V 2>&1 | awk 'END {print $6}' | sed 's/)$//' | awk -F. '{print $1}')

    # params check
    if [[ -z "${py_version}" ]]; then
        LOG_ERROR " not invalid python path, path is ${python_env}."
        exit 1
    fi

    if [[ "${py_version}" != "${py_pip}" ]]; then
        LOG_ERROR "python and pip is not same version"
        LOG_ERROR "python -V, get version => ${py_version}"
        ${python_env} -V
        LOG_ERROR "pip -V, get version => ${py_pip}"
        ${py_pip} -V

        exit 1
    fi

    if [[ "${py_pip}" == "3" ]]; then
        echo "try to use python3"
        if [[ -f "./generator" ]]; then
            sed -i "s?#!/usr/bin/python?#!${python_env}?" ./generator
        elif [[ -f "../generator" ]]; then
            sed -i "s?#!/usr/bin/python?#!${python_env}?" ./generator
        else
            LOG_ERROR "Cann't find generator!"
            exit 1
        fi
    fi

    if [ ${platform} -eq ${Ubuntu_Platform} ]; then
        ubuntu_version=$(< /etc/os-release grep VERSION_ID )
        case ${ubuntu_version} in
        *10*)
            if [[ "${py_pip}" != "3" ]]; then
                echo "Ubuntu 18.10 should use python3!"
                exit 1
            fi
            ;;
        esac
    fi
}

if [ "$1" == "deps" ]; then
    install_deps
    exit 0
else
    install_all
fi

result=$(./generator --help | grep generate_all_certificates)
if [[ -z "${result}" ]]; then
    LOG_ERROR " start failed!"
    echo ${result}
    exit 1
fi
echo -e "\033[32m install generator successful!\033[0m"
