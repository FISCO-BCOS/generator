#!/bin/bash
# "Copyright [2019] <FISCO BCOS>"
# @ function : one click to build chain (appliable for centos, ubuntu)
# @ Require  : openssl
# @ author   : asherli
# @ file     : one_click_generator.sh
# @ date     : 2019

branch_name=$(git symbolic-ref --short -q HEAD)

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)

output_dir=$2
dir_name=()
group_id=
EXIT_CODE=1

help() {
    echo "View at https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0.0/docs/enterprise_tools/enterprise_quick_start.html"
}

check_result() {
    ret=$?
    if [ $ret -ne 0 ]; then
        LOG_ERROR "STATUS CHECK FAILED"
        exit 1
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

# check_rename() {
#     if [ -d "$1" ]; then
#         echo "$1 exists, Want to rename it?(y/n)"
#         read status
#         if [ "${status}" == "y" ]; then
#             LOG_INFO "input name at local path"
#             read name
#             mv $1 ${name}
#         else
#             LOG_ERROR "$1 exist, break!"
#             exit 1
#         fi
#     fi
# }

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
                exit 1
            fi
            LOG_INFO "try to use ${dir}/node_deployment.ini"
            dir_name[i]=${dir}
            i=${i}+1
            group_id=$(< ${dir}/node_deployment.ini grep group_id= | tr -cd '0-9')
        fi
    done

}

run_install() {
    cd ${SHELL_FOLDER}/
    bash ./scripts/install.sh
}

init_chain() {
    cd ${SHELL_FOLDER}/
    ./generator --generate_chain_certificate ./.dir_chain_ca
    check_result
    cp ./.dir_chain_ca/* ${output_dir}/
    if [ ! -f "${SHELL_FOLDER}/meta/fisco-bcos" ]; then
        LOG_INFO "doanloading fisco-bcos..."
        ./generator --download_fisco ./meta
        check_result
    fi
    rm -rf ./.dir_chain_ca
}

init_agency() {
    for agency in ${dir_name[*]}; do
        cd ${SHELL_FOLDER}
        if [ ! -d ${agency}/generator-agency ]; then
            git clone https://github.com/FISCO-BCOS/generator.git ${agency}/generator-agency -b ${branch_name}
            cp ${SHELL_FOLDER}/meta/fisco-bcos ${agency}/generator-agency/meta/fisco-bcos
        fi
        if [ -f "${agency}/agency_cert/agency.crt" ]; then
            if [ -f "${agency}/agency_cert/agency.crt" ]; then
                cp ${agency}/agency_cert/* ./${agency}/generator-agency/meta
            fi
        else
            dir_must_not_exists ${agency}/agency_cert/agency.crt
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
        cp -r ../node_deployment.ini ./conf/
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
}

build_init() {
    run_install
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
                exit 1
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
help)
    help
    ;;
*)
    help
    ;;
esac

check_result
echo -e "\033[32m install generator successful!\033[0m"
