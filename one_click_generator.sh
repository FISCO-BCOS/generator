#!/bin/bash
# "Copyright [2019] <FISCO BCOS>"
# @ function : one click to build chain (appliable for centos, ubuntu)
# @ Require  : openssl
# @ author   : asherli
# @ file     : one_click_generator.sh
# @ date     : 2019

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)

output_dir=$1
dir_name=()
EXIT_CODE=1

help() {
    echo "View at https://fisco-bcos-documentation.readthedocs.io/zh_CN/release-2.0.0/docs/enterprise_tools/enterprise_quick_start.html"
}

check_result() {
    ret=$?
    if [ $ret -ne 0 ]; then
        LOG_ERROR "FAILED execution of command: ${command}"
        # clear_cache
        exit 1
    else
        LOG_INFO "SUCCESS execution of command: ${command}"
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
    if [ -e "$1" ]; then
        echo "$1 DIR exists, please clean old DIR!"
        exit $EXIT_CODE
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
            if [ -d "${dir}/generator" ]; then
                LOG_ERROR "${dir}/generator existed, please delete it!"
                exit 1
            fi
            dir_name[i]=${dir}
            i=${i}+1
        fi
    done

}

run_install() {
    cd ${SHELL_FOLDER}/
    bash ./scripts/install.sh
}

init_chain() {
    cd ${SHELL_FOLDER}/
    ./generator --generate_chain_certificate ./dir_chain_ca
    check_result
    if [ ! -f "${SHELL_FOLDER}/meta/fisco-bcos" ]; then
        LOG_INFO "doanloading fisco-bcos..."
        ./generator --download_fisco ./meta
        check_result
    fi
}

init_agency_with_ke() {
    echo "no key"

}

init_agency() {
    for agency in ${dir_name[*]}; do
        cd ${SHELL_FOLDER}
        file_must_not_exists ${agency}/agency.crt
        file_must_not_exists ${agency}/agency.key
        git clone https://github.com/FISCO-BCOS/generator.git ${agency}/generator-agency
        cp ${SHELL_FOLDER}//meta/fisco-bcos ${agency}/generator-agency/meta/fisco-bcos
        ./generator --generate_agency_certificate ${agency} ./dir_chain_ca agency_cert
        check_result
        cp ${agency}/agency_cert/* ./${agency}/generator-agency/meta
        cp ${agency}/agency_cert/* ${SHELL_FOLDER}/meta/
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
        ./generator --generate_all_certificates ./node_send
        check_result
        cp ./node_send/cert* ${SHELL_FOLDER}/meta
        cat ./node_send/peers.txt >>${SHELL_FOLDER}/meta/peersALL.txt
        cd ${SHELL_FOLDER}
    done
    if [ -f "${SHELL_FOLDER}/meta/peers.txt" ]; then
        rm ${SHELL_FOLDER}/meta/peers.txt
    fi
    sort -n ${SHELL_FOLDER}/meta/peersALL.txt | uniq >${SHELL_FOLDER}/meta/peers.txt
}

init_genesis() {
    cd ${SHELL_FOLDER}
    i=0
    if [ -f "./conf/group_genesis.ini" ]; then
        rm ./conf/group_genesis.ini
    fi
    cat <<EOF >>"./conf/group_genesis.ini"
[group]
group_id=1

[nodes]
EOF
    while read -r line; do
        echo "node${i}=${line}" >>./conf/group_genesis.ini
        # echo "node${i}=${line}"
        i=$((i + 1))
    done <./meta/peers.txt

    ./generator --create_group_genesis ./group
    check_result
    for agency in ${dir_name[*]}; do
        cp ./group/group.1.genesis ${agency}/generator-agency/meta/
    done

}

generate_node() {
    cd ${SHELL_FOLDER}
    for agency in ${dir_name[*]}; do
        cd ${agency}/generator-agency/
        ./generator --build_install_package ${SHELL_FOLDER}/meta/peers.txt ./node
        check_result
        ./generator --get_sdk_file ./sdk
        check_result
        cp -rf ./node ${SHELL_FOLDER}/${agency}/node
        # cp -r ${SHELL_FOLDER}/console ${agency}/console
        cp -rf ./sdk/ ${SHELL_FOLDER}/${agency}/sdk
        cd ${SHELL_FOLDER}
    done
}

# download_console() {
#     cd ${SHELL_FOLDER}
#     ./generator --download_console ./
# }

main() {
    run_install
    init_chain
    check_node_ini ${output_dir}
    init_agency
    init_node_cert
    init_genesis
    # download_console
    generate_node
}

if [ -z "$1" ]; then
    LOG_ERROR "not input found!"
    help
else
    main $1
fi
