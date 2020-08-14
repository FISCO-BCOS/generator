#!/bin/bash

set -e

SHELL_FOLDER=$(
    cd $(dirname $0)
    pwd
)

export TASSL_CMD="${HOME}"/.fisco/tassl
export EXIT_CODE=1

# TASSL env
check_and_install_tassl()
{
    if [ ! -d "${HOME}/.fisco" ]; then
        echo "${HOME}/.fisco does not exist, make directory for it!"
        mkdir "${HOME}/.fisco"
    fi
    if [ ! -f "${HOME}/.fisco/tassl" ];then
        curl -LO https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/FISCO-BCOS/FISCO-BCOS/tools/tassl-1.0.2/tassl.tar.gz
        echo "Downloading tassl binary ..."
        tar zxvf tassl.tar.gz
        chmod u+x tassl
        mv "./tassl" "${HOME}/.fisco/tassl"
    fi
}

check_and_install_tassl

check_env() {
    version=$(openssl version 2>&1 | grep 1.0.2)
    [ -z "$version" ] && {
        echo "please install openssl 1.0.2k-fips!"
        #echo "please install openssl 1.0.2 series!"
        #echo "download openssl from https://www.openssl.org."
        echo "use \"openssl version\" command to check."
        exit $EXIT_CODE
    }
}

usage() {
printf "%s\n" \
"usage command gen_chain_cert chaindir|
              gen_agency_cert chaindir agencydir|
              gen_node_cert agencydir nodedir|
              gen_sdk_cert agencydir sdkdir|
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
    echo $name
    echo $value
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
    if [  -d "$1" ]; then
        echo "$1 DIR exists, please clean old DIR!"
        exit $EXIT_CODE
    fi
}

generate_gmsm2_param()
{
    local output=$1
    cat << EOF > ${output}
-----BEGIN EC PARAMETERS-----
BggqgRzPVQGCLQ==
-----END EC PARAMETERS-----

EOF
}

gen_chain_cert() {
    path="$2"
    name=$(getname "$path")
    echo "$path --- $name"
    dir_must_not_exists "$path"
    check_name chain "$name"

    chaindir=$path
    mkdir -p $chaindir

	$TASSL_CMD genpkey -paramfile ${SHELL_FOLDER}/gmsm2.param -out $chaindir/gmca.key
	$TASSL_CMD req -config ${SHELL_FOLDER}/gmcert.cnf -x509 -days 3650 -subj "/CN=$name/O=fisco-bcos/OU=chain" -key $chaindir/gmca.key -extensions v3_ca -out $chaindir/gmca.crt

    ls $chaindir

    echo "build chain ca succussful!"
}

gen_agency_cert() {
    chain="$2"
    agencypath="$3"
    name=$(getname "$agencypath")

    dir_must_exists "$chain"
    file_must_exists "$chain/gmca.key"
    check_name agency "$name"
    agencydir=$agencypath
    dir_must_not_exists "$agencydir"
    mkdir -p $agencydir

    $TASSL_CMD genpkey -paramfile ${SHELL_FOLDER}/gmsm2.param -out $agencydir/gmagency.key
    $TASSL_CMD req -new -subj "/CN=$name/O=fisco-bcos/OU=agency" -key $agencydir/gmagency.key -config ${SHELL_FOLDER}/gmcert.cnf -out $agencydir/gmagency.csr
    $TASSL_CMD x509 -req -CA $chain/gmca.crt -CAkey $chain/gmca.key -days 3650 -CAcreateserial -in $agencydir/gmagency.csr -out $agencydir/gmagency.crt -extfile ${SHELL_FOLDER}/gmcert.cnf -extensions v3_agency_root

    cp $chain/gmca.crt $agencydir/
    rm -f $agencydir/gmagency.csr

    echo "build $name agency cert successful!"
}

gen_node_cert_with_extensions_gm() {
    capath="$1"
    certpath="$2"
    name="$3"
    type="$4"
    extensions="$5"
    while :
    do
        $TASSL_CMD genpkey -paramfile ${SHELL_FOLDER}/gmsm2.param -out $certpath/gm${type}.key
        privateKey=$(${TASSL_CMD} ec -in "$certpath/gm${type}.key" -text 2> /dev/null| sed -n '3,5p' | sed 's/://g'| tr "\n" " "|sed 's/ //g')
        len=${#privateKey}
        head2=${privateKey:0:2}
        if [ "64" != "${len}" ] || [ "00" == "$head2" ];then
            rm $certpath/gm${type}.key
            continue;
        fi
        break;
    done
    $TASSL_CMD req -new -subj "/CN=${name}/O=fisco-bcos/OU=${type}" -key $certpath/gm${type}.key -config ${SHELL_FOLDER}/gmcert.cnf -out $certpath/gm${type}.csr
    $TASSL_CMD x509 -req -CA $capath/gmagency.crt -CAkey $capath/gmagency.key -days 3650 -CAcreateserial -in $certpath/gm${type}.csr -out $certpath/gm${type}.crt -extfile ${SHELL_FOLDER}/gmcert.cnf -extensions $extensions

    rm -f $certpath/gm${type}.csr
}

gen_node_cert() {
    if [ "" = "$(openssl ecparam -list_curves 2>&1 | grep secp256k1)" ]; then
        echo "openssl don't support secp256k1, please upgrade openssl!"
        exit $EXIT_CODE
    fi

    agpath="$2"
    agency=$(getname "$agpath")
    ndpath="$3"
    node=$(getname "$ndpath")
    dir_must_exists "$agpath"
    file_must_exists "$agpath/gmagency.key"
    check_name agency "$agency"

    mkdir -p $ndpath
    dir_must_exists "$ndpath"
    check_name node "$node"

    mkdir -p $ndpath
    gen_node_cert_with_extensions_gm "$agpath" "$ndpath" "$node" node v3_req
    gen_node_cert_with_extensions_gm "$agpath" "$ndpath" "$node" ennode v3enc_req
    #nodeid is pubkey
    $TASSL_CMD ec -in $ndpath/gmnode.key -text -noout | sed -n '7,11p' | sed 's/://g' | tr "\n" " " | sed 's/ //g' | awk '{print substr($0,3);}'  | cat > $ndpath/gmnode.nodeid

    #serial
    if [ "" != "$($TASSL_CMD version | grep 1.0.2)" ];
    then
        $TASSL_CMD x509  -text -in $ndpath/gmnode.crt | sed -n '5p' |  sed 's/://g' | tr "\n" " " | sed 's/ //g' | sed 's/[a-z]/\u&/g' | cat > $ndpath/gmnode.serial
    else
        $TASSL_CMD x509  -text -in $ndpath/gmnode.crt | sed -n '4p' |  sed 's/ //g' | sed 's/.*(0x//g' | sed 's/)//g' |sed 's/[a-z]/\u&/g' | cat > $ndpath/gmnode.serial
    fi


    cp $agpath/gmca.crt $agpath/gmagency.crt $ndpath

    cd $ndpath

    echo "build $node node cert successful!"
}



case "$1" in
gen_chain_cert)
    gen_chain_cert "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_agency_cert)
    gen_agency_cert "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
gen_node_cert)
    gen_node_cert "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9"
    ;;
download_tassl)
    check_and_install_tassl
    ;;
help)
    usage
    ;;
*)
    usage
esac
