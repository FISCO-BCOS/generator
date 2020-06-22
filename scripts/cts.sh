#!/bin/bash

set -e

EXIT_CODE=1
# mypass=""

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)

usage() {
printf "%s\n" \
"usage command gen_rsa_req type reqdir|
              gen_secp_req type reqdir|
              gen_chain_cert chaindir|
              gen_agency_cert chaindir agencydir|
              sign_agency_cert chaindir reqfile|
              gen_node_cert agencydir nodedir|
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

gen_chain_cert() {
    path="$1"
    name=$(getname "$path")
    echo "$path --- $name"
    dir_must_not_exists "$path"
    check_name chain "$name"

    chaindir=$path
    mkdir -p $chaindir
    openssl ecparam -out "$chaindir/secp256k1.param" -name secp256k1 2> /dev/null
    openssl genpkey -paramfile "$chaindir/secp256k1.param" -out "$chaindir/ca.key" 2> /dev/null
    openssl req -new -x509 -days 3650 -subj "/CN=$name/O=fisco-bcos/OU=chain" -key "$chaindir/ca.key" -out "$chaindir/ca.crt"
    rm -f "$chaindir/secp256k1.param"

    if [ $? -eq 0 ]; then
        echo "build chain ca succussful!"
    else
        echo "please input at least Common Name!"
    fi
}

gen_agency_cert() {
    chain="$1"
    agencypath="$2"
    name=$(getname "$agencypath")

    dir_must_exists "$chain"
    file_must_exists "$chain/ca.key"
    check_name agency "$name"
    agencydir=$agencypath
    dir_must_not_exists "$agencydir"
    mkdir -p $agencydir

    openssl ecparam -out "$agencydir/secp256k1.param" -name secp256k1 2> /dev/null
    openssl genpkey -paramfile "$agencydir/secp256k1.param" -out "$agencydir/agency.key" 2> /dev/null
    openssl req -new -sha256 -subj "/CN=$name/O=fisco-bcos/OU=agency" -key "$agencydir/agency.key" -config "${SHELL_FOLDER}/cert.cnf" -out "$agencydir/agency.csr" 2> /dev/null
    openssl x509 -req -days 3650 -sha256 -CA "$chain/ca.crt" -CAkey "$chain/ca.key" -CAcreateserial\
        -in "$agencydir/agency.csr" -out "$agencydir/agency.crt"  -extensions v4_req -extfile "${SHELL_FOLDER}/cert.cnf" 2> /dev/null
    # cat "$chain/ca.crt" >> "$agencydir/agency.crt"
    cp $chain/ca.crt $agencydir/
    rm -f "$agencydir/agency.csr" "$agencydir/secp256k1.param"

    echo "build $name agency cert successful!"
}

gen_cert_secp256k1() {
    capath="$1"
    certpath="$2"
    name="$3"
    type="$4"
    openssl ecparam -out $certpath/${type}.param -name secp256k1
    while :
    do
        openssl genpkey -paramfile $certpath/${type}.param -out $certpath/${type}.key
        privateKey=$(openssl ec -in $certpath/${type}.key -text 2> /dev/null| sed -n '3,5p' | sed 's/://g'| tr "\n" " "|sed 's/ //g')
        openssl ec -in $certpath/${type}.key -text 2> /dev/null| sed -n '3,5p' | sed 's/://g'| tr "\n" " "|sed 's/ //g'
        len=${#privateKey}
        head2=${privateKey:0:2}
        if [ "64" != "${len}" ] || [ "00" == "$head2" ];then
            rm $certpath/${type}.key

            continue;
        fi
        break;
    done
    openssl pkey -in $certpath/${type}.key -pubout -out $certpath/${type}.pubkey
    openssl req -new -sha256 -subj "/CN=${name}/O=fisco-bcos/OU=${type}" -key $certpath/${type}.key -config ${SHELL_FOLDER}/cert.cnf -out $certpath/${type}.csr
    openssl x509 -req -days 3650 -sha256 -in $certpath/${type}.csr -CAkey $capath/agency.key -CA $capath/agency.crt\
        -out $certpath/${type}.crt -CAcreateserial -extensions v3_req -extfile ${SHELL_FOLDER}/cert.cnf
    openssl ec -in $certpath/${type}.key -outform DER | tail -c +8 | head -c 32 | xxd -p -c 32 | cat >$certpath/${type}.private
    rm -f $certpath/${type}.csr
}

gen_node_cert() {
    if [ "" == "$(openssl ecparam -list_curves 2>&1 | grep secp256k1)" ]; then
        echo "openssl don't support secp256k1, please upgrade openssl!"
        exit $EXIT_CODE
    fi

    agpath="$1"
    agency=$(getname "$agpath")
    ndpath="$2"
    node=$(getname "$ndpath")
    dir_must_exists "$agpath"
    file_must_exists "$agpath/agency.key"
    check_name agency "$agency"
    dir_must_not_exists "$ndpath"
    check_name node "$node"

    mkdir -p $ndpath

    gen_cert_secp256k1 "$agpath" "$ndpath" "$node" node
    #nodeid is pubkey
    openssl ec -in $ndpath/node.key -text -noout | sed -n '7,11p' | tr -d ": \n" | awk '{print substr($0,3);}' | cat >$ndpath/node.nodeid
    openssl x509 -serial -noout -in $ndpath/node.crt | awk -F= '{print $2}' | cat >$ndpath/node.serial
    cp $agpath/ca.crt $agpath/agency.crt $ndpath

    cd $ndpath
    nodeid=$(< node.nodeid head)
    serial=$(< node.serial head)
    cat >node.json <<EOF
{
 "id":"$nodeid",
 "name":"$node",
 "agency":"$agency",
 "caHash":"$serial"
}
EOF
    cat >node.ca <<EOF
{
 "serial":"$serial",
 "pubkey":"$nodeid",
 "name":"$node"
}
EOF

    echo "build $node node cert successful!"
}

case "$1" in
gen_rsa_req)
    gen_rsa_req "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_secp_req)
    gen_secp_req "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_chain_cert)
    gen_chain_cert "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_agency_cert)
    gen_agency_cert "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
sign_agency_cert)
    sign_agency_cert "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_node_cert)
    gen_node_cert "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
help)
    usage
    ;;
*)
    usage
esac
