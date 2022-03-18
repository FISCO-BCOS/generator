#!/bin/bash
set -e

rsa_key_length=2048
days=36500

EXIT_CODE=1
# mypass=""

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)

usage() {
printf "%s\n" \
"usage command gen_chain_cert chaindir|
              gen_node_cert chaindir nodedir|
              help"
}

getname() {
    local name="$1"
    if [ -z "$name" ]; then
        return 0
    fi
    [[ "$name" =~ ^.*/$ ]] && {
        name="${name%/*}"
    }
    name="${name##*/}"
    echo "$name"
}

check_name() {
    local name="$1"
    local value="$2"
    [[ "$value" =~ ^[a-zA-Z0-9._-]+$ ]] || {
        echo "$name name [$value] invalid, it should match regex: ^[a-zA-Z0-9._-]+\$"
        exit $EXIT_CODE
    }
}

file_must_exists() {
    if [ ! -f "$1" ]; then
        echo "$1 file does not exist, please check!"
        exit $EXIT_CODE
    fi
}

file_must_not_exists() {
    if [ -f "$1" ]; then
        echo "$1 file exist, please check!"
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

dir_must_not_exists() {
    if [ -e "$1" ]; then
        echo "$1 DIR exists, please clean old DIR!"
        exit $EXIT_CODE
    fi
}


gen_chain_cert() {
    local chaindir="${1}"
    local name=$(getname "$chaindir")
    check_name node "$name"

    file_must_not_exists "${chaindir}"/ca.key
    file_must_not_exists "${chaindir}"/ca.crt
    # file_must_exists "${cert_conf}"

    mkdir -p "$chaindir"
    dir_must_exists "${chaindir}"

    openssl genrsa -out "${chaindir}"/ca.key "${rsa_key_length}" 2>/dev/null
    openssl req -new -x509 -days "${days}" -subj "/CN=${name}/O=fisco-bcos/OU=chain" -key "${chaindir}"/ca.key -out "${chaindir}"/ca.crt  2>/dev/null

    echo "generate rsa ca cert successful!"
}

gen_node_cert() {
    local capath="${1}"
    local ndpath="${2}"
    local type="${3}"
    local name=$(getname "$ndpath")

    file_must_exists "$capath/ca.key"
    file_must_exists "$capath/ca.crt"
    check_name node "$name"
    check_name type "$type"

    file_must_not_exists "$ndpath"/"${type}".key
    file_must_not_exists "$ndpath"/"${type}".crt

    mkdir -p "${ndpath}"
    dir_must_exists "${ndpath}"

    openssl genrsa -out "${ndpath}"/"${type}".key "${rsa_key_length}" 2>/dev/null
    openssl req -new -sha256 -subj "/CN=${name}/O=fisco-bcos/OU=agency" -key "$ndpath"/"${type}".key -out "$ndpath"/"${type}".csr
    openssl x509 -req -days "${days}" -sha256 -CA "${capath}"/ca.crt -CAkey "$capath"/ca.key -CAcreateserial \
        -in "$ndpath"/"${type}".csr -out "$ndpath"/"${type}".crt -extensions v4_req 2>/dev/null

    openssl pkcs8 -topk8 -in "$ndpath"/"${type}".key -out "$ndpath"/pkcs8_node.key -nocrypt

    rm -f "$ndpath"/"$type".csr
    rm -f "$ndpath"/"$type".key

    mv "$ndpath"/pkcs8_node.key "$ndpath"/"$type".key
    cp "$capath/ca.crt" "$ndpath"

    echo "generate ${ndpath} node rsa cert successful!"
}

case "$1" in
gen_chain_cert)
    gen_chain_cert "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_node_cert)
    gen_node_cert "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
help)
    usage
    exit 0
    ;;
*)
    exit 1
esac
