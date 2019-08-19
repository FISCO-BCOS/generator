#!/bin/bash
# "Copyright [2019] <FISCO BCOS>"
# @ function : one click to build chain (appliable for centos, ubuntu)
# @ Require  : openssl
# @ author   : asherli
# @ file     : one_click_generator.sh
# @ date     : 2019

set -e

# branch_name=$(git symbolic-ref --short -q HEAD)

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)

output_dir=$2
dir_name=()
group_id=
EXIT_CODE=1

help() {
    echo "bash one_click_generator.sh -b ./tmp_onc_click"
    echo "bash one_click_generator.sh -e ./tmp_onc_click_expand"
    echo "bash one_click_generator.sh -clean"
    echo "View at https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0/docs/enterprise_tools/enterprise_quick_start.html"
}

check_result() {
    ret=$?
    if [ $ret -ne 0 ]; then
        LOG_ERROR "STATUS CHECK FAILED"
        exit $EXIT_CODE
    fi
}

LOG_ERROR() {
    content=${1}
    echo -e "\033[31m${content}\033[0m"
}

LOG_INFO() {
    content=${1}
    echo -e "\033[32m${content}\033[0m"
}

run_install() {
    bash ${SHELL_FOLDER}/scripts/install.sh
    ./generator --download_fisco ./meta
}

file_must_exists() {
    if [ ! -f "$1" ]; then
        echo "$1 file does not exist, please check!"
        exit $EXIT_CODE
    fi
}

file_must_not_exists() {
    if [ -f "$1" ]; then
        echo "$1 file exist, please clean old file!"
        exit $EXIT_CODE
    fi
}

dir_must_exists() {
    if [ ! -d "$1" ]; then
        echo "$1 DIR does not exist, please check!"
        exit $EXIT_CODE
    fi
}

dir_must_not_exists() {
    if [ -d "$1" ]; then
        echo "$1 DIR exists, please clean old DIR!"
        exit $EXIT_CODE
    fi
}

delete_dir() {
    if [ -d "$1" ]; then
        echo "$1 exists, delete it?(y/n)"
        read -r status
        if [ "${status}" == "y" ]; then
            echo "delete $1..."
            rm -rf $1
        else
            LOG_ERROR "$1 exist, please delete or rename it!"
            exit $EXIT_CODE
        fi
    fi
}

delete_file() {
    if [ -f "$1" ]; then
        echo "$1 exists, delete it?(y/n)"
        read -r status
        if [ "${status}" == "y" ]; then
            echo "delete $1..."
            rm $1
        else
            LOG_ERROR "$1 exist, please delete or rename it!"
            exit $EXIT_CODE
        fi
    fi
}

check_generator_status () {
    file_must_not_exists ${SHELL_FOLDER}/meta/ca.*
    file_must_not_exists ${SHELL_FOLDER}/meta/agency.*
    file_must_not_exists ${SHELL_FOLDER}/meta/cert_*
    dir_must_not_exists ${SHELL_FOLDER}/meta/node_*
    if [ ! -d "${SHELL_FOLDER}/tpl/generator-bak" ]; then
        LOG_INFO "copy generator..."
        cp -r ${SHELL_FOLDER} ~/.genrator
        mv ~/.genrator ${SHELL_FOLDER}/tpl/generator-bak
        check_result
        cd ${SHELL_FOLDER}
    fi
    if [ ! -f "${SHELL_FOLDER}/meta/fisco-bcos" ]; then
        LOG_INFO "downloading fisco-bcos..."
        ./generator --download_fisco ./meta
        check_result
    fi
}

get_time_stamp() {
    current=$(date "+%Y-%m-%d %H:%M:%S")
    timeStamp=$(date -d "$current" +%s)
    echo ${timeStamp}
}

check_rename() {
    if [ -d "$1" ]; then
        echo "$1 exists, rename it to $1_$(get_time_stamp)"
        mv $1 $1_$(get_time_stamp)
    fi
}

check_node_ini() {
    i=0
    for dir in ${output_dir}/*; do
        [[ -e ${dir} ]] || break
        if [ -d ${dir} ]; then
            if [ ! -f "${dir}/node_deployment.ini" ]; then
                LOG_ERROR "${dir}/node_deployment.ini not exist!"
                exit $EXIT_CODE
            fi
            if [ -d "${dir}/generator-agency" ]; then
                LOG_ERROR "${dir}/generator-agency exist!"
                exit $EXIT_CODE
            fi
            LOG_INFO "try to use ${dir}/node_deployment.ini"
            dir_name[i]=${dir}
            i=${i}+1
            group_id=$(< ${dir}/node_deployment.ini grep group_id= | tr -cd '0-9')
        fi
    done

}


init_chain() {
    cd ${SHELL_FOLDER}/
    ./generator --generate_chain_certificate ./.dir_chain_ca
    check_result
    cp ./.dir_chain_ca/* ${output_dir}/
    rm -rf ./.dir_chain_ca
}

init_agency() {
    for agency in ${dir_name[*]}; do
        cd ${SHELL_FOLDER}
        if [ ! -d ${agency}/generator-agency ]; then
            cp -r ${SHELL_FOLDER}/tpl/generator-bak ${agency}/generator-agency
            cp ${SHELL_FOLDER}/meta/fisco-bcos ${agency}/generator-agency/meta/fisco-bcos
        fi
        if [ -f "${agency}/agency_cert/agency.crt" ]; then
            if [ -f "${agency}/agency_cert/agency.crt" ]; then
                cp ${agency}/agency_cert/* ./${agency}/generator-agency/meta
            fi
        else
            file_must_not_exists ${agency}/agency_cert/agency.crt
            ./generator --generate_agency_certificate ${agency} ${output_dir}/ agency_cert
            check_result
            cp ${agency}/agency_cert/* ./${agency}/generator-agency/meta
            # cp ${agency}/agency_cert/* ${SHELL_FOLDER}/meta/
        fi
    done
}

init_node_cert() {
    if [ -f "${SHELL_FOLDER}/meta/peersALL.txt" ]; then
        rm ${SHELL_FOLDER}/meta/peersALL.txt
    fi
    for agency in ${dir_name[*]}; do
        cd ${agency}/generator-agency
        cp ../node_deployment.ini ./conf/
        LOG_INFO "${agency} generate node now..."
        check_rename ./node_send
        ./generator --generate_all_certificates ./node_send
        check_result
        cp ./node_send/cert* ${SHELL_FOLDER}/meta
        cat ./node_send/peers.txt >>${SHELL_FOLDER}/meta/peersALL.txt
        cd ${SHELL_FOLDER}
    done
    if [ -f "${SHELL_FOLDER}/meta/peers.txt" ]; then
        rm ${SHELL_FOLDER}/meta/peers.txt
    fi
    if [ -f "${output_dir}/peers.txt" ]; then
        cat ${output_dir}/peers.txt >>${SHELL_FOLDER}/meta/peersALL.txt
    fi
    sort -n ${SHELL_FOLDER}/meta/peersALL.txt | uniq >${SHELL_FOLDER}/meta/peers.txt
    cp ${SHELL_FOLDER}/meta/peers.txt ${output_dir}/
}

init_genesis() {
    cd ${SHELL_FOLDER}
    i=0
    if [ -f "./conf/group_genesis.ini" ]; then
        rm ./conf/group_genesis.ini
    fi
    cat <<EOF >>"./conf/group_genesis.ini"
[group]
group_id=${group_id}

[nodes]
EOF
    while read -r line; do
        echo "node${i}=${line}" >>./conf/group_genesis.ini
        # echo "node${i}=${line}"
        i=$((i + 1))
    done <./meta/peers.txt

    ./generator --create_group_genesis ./.group
    cp ./.group/group.*.genesis ${output_dir}/
    check_result
    for agency in ${dir_name[*]}; do
        cp ./.group/group.*.genesis ${SHELL_FOLDER}/${agency}/generator-agency/meta/
    done
    rm -rf ./.group
    rm ${SHELL_FOLDER}/meta/cert_*
    rm ${SHELL_FOLDER}/meta/group.*
    rm -rf ${SHELL_FOLDER}/meta/node_*
}

generate_node() {
    cd ${SHELL_FOLDER}
    for agency in ${dir_name[*]}; do
        cd ${agency}/generator-agency/
        check_rename ./node
        ./generator --build_install_package ${SHELL_FOLDER}/meta/peers.txt ./node
        check_result
        check_rename ./sdk
        ./generator --get_sdk_file ./sdk
        check_result
        check_rename ${SHELL_FOLDER}/${agency}/node
        check_rename ${SHELL_FOLDER}/${agency}/sdk
        mv ./node ${SHELL_FOLDER}/${agency}/node
        mv ./sdk/ ${SHELL_FOLDER}/${agency}/sdk
        cd ${SHELL_FOLDER}
    done
    if [ -f "${SHELL_FOLDER}/meta/peers*" ]; then
        rm ${SHELL_FOLDER}/meta/peers*
    fi
    if [ -f "${SHELL_FOLDER}/meta/cert_*" ]; then
        rm ${SHELL_FOLDER}/meta/cert_*
    fi
}

build_init() {
    # run_install
    check_generator_status
    init_chain
    check_node_ini
    init_agency
    init_node_cert
    init_genesis
    generate_node
}

chain_must_exist() {
    file_must_exists ${output_dir}/ca.crt
    file_must_exists ${output_dir}/ca.key
    file_must_exists ${output_dir}/peers.txt
}

copy_genesis() {
    for agency in ${dir_name[*]}; do
        cp ${output_dir}/group.${group_id}.genesis ${SHELL_FOLDER}/${agency}/generator-agency/meta/
    done
}

add_peers_expand_node() {
    cat ${output_dir}/peers.txt >>${SHELL_FOLDER}/meta/peers.txt
    sort -n ${SHELL_FOLDER}/meta/peers.txt | uniq
}

expand_init() {
    check_generator_status
    chain_must_exist
    expand_node_ini
    init_agency
    init_node_cert
    copy_genesis
    add_peers_expand_node
    generate_node
}

expand_node_ini() {
    i=0
    for dir in ${output_dir}/*; do
        [[ -e ${dir} ]] || break
        if [ -d ${dir} ]; then
            if [ ! -f "${dir}/node_deployment.ini" ]; then
                LOG_ERROR "${dir}/node_deployment.ini not exist!"
                exit $EXIT_CODE
            fi
            if [ -d "${dir}/generator-agency" ]; then
                LOG_ERROR "${dir}/generator-agency exist!"
                exit $EXIT_CODE
            fi
            # group_id=$(cat ${dir}/node_deployment.ini | grep group_id= | tr '\r' ' ' | sed s/ //g | sed s/group_id=//g)
            group_id=$(< ${dir}/node_deployment.ini grep group_id= | tr -cd '0-9')
            file_must_exists ${output_dir}/group.${group_id}.genesis
            LOG_INFO "Need group.${group_id}.genesis in ${output_dir}"
            LOG_INFO "try to use ${dir}/node_deployment.ini"
            dir_name[i]=${dir}
            i=${i}+1
        fi
    done
}

clean_data() {
    # clean dictionary in meta
    delete_dir ${SHELL_FOLDER}/meta/node_*
    delete_file ${SHELL_FOLDER}/meta/*.crt
    delete_file ${SHELL_FOLDER}/meta/*.key
    
}

if [ -z "$1" ]; then
    LOG_ERROR "not input found!"
    help
fi

case "$1" in
-b)
    build_init $2
    ;;
-build)
    build_init $2
    ;;
-e)
    expand_init $2
    ;;
-expand)
    expand_init $2
    ;;
-clean)
    clean_data
    ;;
clean)
    clean_data
    ;;
help)
    help
    ;;
*)
    help
    ;;
esac

check_result
echo -e "\033[32m run one_click_generator successful!\033[0m"
