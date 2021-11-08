#!/bin/bash

dirpath="$(cd "$(dirname "$0")" && pwd)"
listen_ip="0.0.0.0"
output_dir="cert"
cdn_link_header="https://osp-1257653870.cos.ap-guangzhou.myqcloud.com/FISCO-BCOS"

# for cert generation
ca_cert_dir="${dirpath}"
sm_cert_conf='sm_cert.cnf'
days=36500
rsa_key_length=2048
sm_mode='false'
macOS=""
x86_64_arch="true"
sm2_params="sm_sm2.param"
OPENSSL_CMD="${HOME}/.fisco/tassl"
file_dir="./"
command=""

LOG_WARN() {
    local content=${1}
    echo -e "\033[31m[ERROR] ${content}\033[0m"
}

LOG_INFO() {
    local content=${1}
    echo -e "\033[32m[INFO] ${content}\033[0m"
}

LOG_FALT() {
    local content=${1}
    echo -e "\033[31m[FALT] ${content}\033[0m"
    exit 1
}

dir_must_exists() {
    if [ ! -d "$1" ]; then
        LOG_FALT "$1 DIR does not exist, please check!"
    fi
}

file_must_not_exists() {
    if [ -f "$1" ]; then
        LOG_FALT "$1 file already exist, please check!"
    fi
}

file_must_exists() {
    if [ ! -f "$1" ]; then
        LOG_FALT "$1 file does not exist, please check!"
    fi
}

check_env() {
    if [ "$(uname)" == "Darwin" ];then
        export PATH="/usr/local/opt/openssl/bin:$PATH"
        macOS="macOS"
    fi
    [ ! -z "$(openssl version | grep 1.0.2)" ] || [ ! -z "$(openssl version | grep 1.1)" ] || {
        echo "please install openssl!"
        #echo "download openssl from https://www.openssl.org."
        echo "use \"openssl version\" command to check."
        exit 1
    }

    if [ "$(uname -m)" != "x86_64" ];then
        x86_64_arch="false"
    fi
}

check_name() {
    local name="$1"
    local value="$2"
    [[ "$value" =~ ^[a-zA-Z0-9._-]+$ ]] || {
        LOG_FALT "$name name [$value] invalid, it should match regex: ^[a-zA-Z0-9._-]+\$"
    }
}

generate_sm_sm2_param() {
    local output=$1
    cat <<EOF >"${output}"
-----BEGIN EC PARAMETERS-----
BggqgRzPVQGCLQ==
-----END EC PARAMETERS-----

EOF
}

generate_sm_cert_conf() {
    local output=$1
    cat <<EOF >"${output}"
HOME			= .
RANDFILE		= $ENV::HOME/.rnd
oid_section		= new_oids

[ new_oids ]
tsa_policy1 = 1.2.3.4.1
tsa_policy2 = 1.2.3.4.5.6
tsa_policy3 = 1.2.3.4.5.7

####################################################################
[ ca ]
default_ca	= CA_default		# The default ca section

####################################################################
[ CA_default ]

dir		= ./demoCA		# Where everything is kept
certs		= $dir/certs		# Where the issued certs are kept
crl_dir		= $dir/crl		# Where the issued crl are kept
database	= $dir/index.txt	# database index file.
#unique_subject	= no			# Set to 'no' to allow creation of
					# several ctificates with same subject.
new_certs_dir	= $dir/newcerts		# default place for new certs.

certificate	= $dir/cacert.pem 	# The CA certificate
serial		= $dir/serial 		# The current serial number
crlnumber	= $dir/crlnumber	# the current crl number
					# must be commented out to leave a V1 CRL
crl		= $dir/crl.pem 		# The current CRL
private_key	= $dir/private/cakey.pem # The private key
RANDFILE	= $dir/private/.rand	# private random number file

x509_extensions	= usr_cert		# The extensions to add to the cert

name_opt 	= ca_default		# Subject Name options
cert_opt 	= ca_default		# Certificate field options

default_days	= 365			# how long to certify for
default_crl_days= 30			# how long before next CRL
default_md	= default		# use public key default MD
preserve	= no			# keep passed DN ordering

policy		= policy_match

[ policy_match ]
countryName		= match
stateOrProvinceName	= match
organizationName	= match
organizationalUnitName	= optional
commonName		= supplied
emailAddress		= optional

[ policy_anything ]
countryName		= optional
stateOrProvinceName	= optional
localityName		= optional
organizationName	= optional
organizationalUnitName	= optional
commonName		= supplied
emailAddress		= optional

####################################################################
[ req ]
default_bits		= 2048
default_md		= sm3
default_keyfile 	= privkey.pem
distinguished_name	= req_distinguished_name
x509_extensions	= v3_ca	# The extensions to add to the self signed cert

string_mask = utf8only

# req_extensions = v3_req # The extensions to add to a certificate request

[ req_distinguished_name ]
countryName = CN
countryName_default = CN
stateOrProvinceName = State or Province Name (full name)
stateOrProvinceName_default =GuangDong
localityName = Locality Name (eg, city)
localityName_default = ShenZhen
organizationalUnitName = Organizational Unit Name (eg, section)
organizationalUnitName_default = fisco
commonName =  Organizational  commonName (eg, fisco)
commonName_default =  fisco
commonName_max = 64

[ usr_cert ]
basicConstraints=CA:FALSE
nsComment			= "OpenSSL Generated Certificate"

subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer

[ v3_req ]

# Extensions to add to a certificate request

basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature

[ v3enc_req ]

# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = keyAgreement, keyEncipherment, dataEncipherment

[ v3_agency_root ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints = CA:true
keyUsage = cRLSign, keyCertSign

[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints = CA:true
keyUsage = cRLSign, keyCertSign

EOF
}

generate_cert_conf() {
    local output=$1
    cat <<EOF >"${output}"
[ca]
default_ca=default_ca
[default_ca]
default_days = 3650
default_md = sha256

[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
[req_distinguished_name]
countryName = CN
countryName_default = CN
stateOrProvinceName = State or Province Name (full name)
stateOrProvinceName_default =GuangDong
localityName = Locality Name (eg, city)
localityName_default = ShenZhen
organizationalUnitName = Organizational Unit Name (eg, section)
organizationalUnitName_default = FISCO-BCOS
commonName =  Organizational  commonName (eg, FISCO-BCOS)
commonName_default = FISCO-BCOS
commonName_max = 64

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

[ v4_req ]
basicConstraints = CA:TRUE

EOF
}

gen_chain_cert() {

    if [ ! -f "${cert_conf}" ]; then
        generate_cert_conf "${cert_conf}"
    fi

    local chaindir="${1}"

    file_must_not_exists "${chaindir}"/ca.key
    file_must_not_exists "${chaindir}"/ca.crt
    file_must_exists "${cert_conf}"

    mkdir -p "$chaindir"
    dir_must_exists "$chaindir"

    openssl genrsa -out "${chaindir}"/ca.key "${rsa_key_length}" 2> /dev/null
    openssl req -new -x509 -days "${days}" -subj "/CN=FISCO-BCOS/O=FISCO-BCOS/OU=chain" -key "${chaindir}"/ca.key -out "${chaindir}"/ca.crt 2>/dev/null
    mv "${cert_conf}" "${chaindir}"

    LOG_INFO "Build ca cert successfully!"
}

gen_rsa_node_cert() {
    local capath="${1}"
    local ndpath="${2}"
    local type="${3}"

    file_must_exists "$capath/ca.key"
    file_must_exists "$capath/ca.crt"
    # check_name node "$node"

    file_must_not_exists "$ndpath"/"${type}".key
    file_must_not_exists "$ndpath"/"${type}".crt

    mkdir -p "${ndpath}"
    dir_must_exists "${ndpath}"

    openssl genrsa -out "${ndpath}"/"${type}".key "${rsa_key_length}" 2> /dev/null
    openssl req -new -sha256 -subj "/CN=FISCO-BCOS/O=fisco-bcos/OU=agency" -key "$ndpath"/"${type}".key -config "$capath"/cert.cnf -out "$ndpath"/"${type}".csr
    openssl x509 -req -days "${days}" -sha256 -CA "${capath}"/ca.crt -CAkey "$capath"/ca.key -CAcreateserial \
        -in "$ndpath"/"${type}".csr -out "$ndpath"/"${type}".crt -extensions v4_req -extfile "$capath"/cert.cnf 2>/dev/null

    openssl pkcs8 -topk8 -in "$ndpath"/"$type".key -out "$ndpath"/pkcs8_node.key -nocrypt
    cp "$capath"/ca.crt "$capath"/cert.cnf "$ndpath"/

    rm -f "$ndpath"/"${type}".csr
    rm -f "$ndpath"/"${type}".key

    mv "$ndpath"/pkcs8_node.key "$ndpath"/"${type}".key

    LOG_INFO "Build node cert successful!"
}

gen_sm_chain_cert() {
    local chaindir="${1}"
    name=$(basename "$chaindir")
    check_name chain "$name"

    if [ ! -f "${sm_cert_conf}" ]; then
        generate_sm_cert_conf 'sm_cert.cnf'
    else
        cp -f "${sm_cert_conf}" .
    fi

    generate_sm_sm2_param "${sm2_params}"

    mkdir -p "$chaindir"
    dir_must_exists "$chaindir"

    "$OPENSSL_CMD" genpkey -paramfile "${sm2_params}" -out "$chaindir/sm_ca.key"
    "$OPENSSL_CMD" req -config sm_cert.cnf -x509 -days "${days}" -subj "/CN=FISCO-BCOS/O=FISCO-BCOS/OU=chain" -key "$chaindir/sm_ca.key" -extensions v3_ca -out "$chaindir/sm_ca.crt"
    cp "${sm_cert_conf}" "${chaindir}"
    cp "${sm2_params}" "${chaindir}"
}

gen_sm_node_cert_with_ext() {
    local capath="$1"
    local certpath="$2"
    local type="$3"
    local extensions="$4"

    file_must_exists "$capath/sm_ca.key"
    file_must_exists "$capath/sm_ca.crt"

    file_must_not_exists "$ndpath/sm_${type}.crt"
    file_must_not_exists "$ndpath/sm_${type}.key"

    "$OPENSSL_CMD" genpkey -paramfile "$capath/${sm2_params}" -out "$certpath/sm_${type}.key"
    "$OPENSSL_CMD" req -new -subj "/CN=FISCO-BCOS/O=fisco-bcos/OU=${type}" -key "$certpath/sm_${type}.key" -config "$capath/sm_cert.cnf" -out "$certpath/sm_${type}.csr"

    echo "not use $(basename "$capath") to sign $(basename $certpath) ${type}" >>"${logfile}"
    "$OPENSSL_CMD" x509 -sm3 -req -CA "$capath/sm_ca.crt" -CAkey "$capath/sm_ca.key" -days "${days}" -CAcreateserial -in "$certpath/sm_${type}.csr" -out "$certpath/sm_${type}.crt" -extfile "$capath/sm_cert.cnf" -extensions "$extensions"

    rm -f "$certpath/sm_${type}.csr"
}

gen_sm_node_cert() {
    local capath="${1}"
    local ndpath="${2}"
    local type="${3}"

    file_must_exists "$capath/sm_ca.key"
    file_must_exists "$capath/sm_ca.crt"

    mkdir -p "$ndpath"
    dir_must_exists "$ndpath"
    local node=$(basename "$ndpath")
    check_name node "$node"

    gen_sm_node_cert_with_ext "$capath" "$ndpath" ${type} v3_req
    gen_sm_node_cert_with_ext "$capath" "$ndpath" "en${type}" v3enc_req
    #nodeid is pubkey
    $OPENSSL_CMD ec -in "$ndpath/sm_${type}.key" -text -noout 2> /dev/null | sed -n '7,11p' | sed 's/://g' | tr "\n" " " | sed 's/ //g' | awk '{print substr($0,3);}' | cat > "$ndpath/sm_${type}.nodeid"

    cp "$capath/sm_ca.crt" "$ndpath"
}

help() {
    echo $1
    cat <<EOF
Usage:
    -l <IP list>                        [Required] "ip1:nodeNum1,ip2:nodeNum2" e.g:"192.168.0.1:2,192.168.0.2:3"
    -o <output dir>                     [Optional] output directory, default ./nodes
    -p <start Port>                     [Optional] Default 30300,20200 means p2p port start from 30300, rpc port start from 20200
    -s <SM model>                       [Optional] SM SSL connection or not, default no
    -r <leader_period>                  [Optional] leader_period, default 1
    -b <block_tx_count_limit>           [Optional] block_tx_count_limit, default 1000
    -c <consensus_timeout>              [Optional] consensus_timeout, default 3000
    -g <gas_limit>                      [Optional] gas_limit default 300000000
    -n <consensus_type>                 [Optional] consensus_type default pbft
    -h Help
e.g
    bash $0 -p 30300,20200 -l 127.0.0.1:4 -o nodes -e ./mini-consensus
    bash $0 -p 30300,20200 -l 127.0.0.1:4 -o nodes -e ./mini-consensus -s
EOF

    exit 0
}

generate_single_node_cert() {
    local sm_mode="$1"
    local ca_cert_path="${2}"
    local node_cert_path="${3}"
    local type="${4}"

    mkdir -p ${node_cert_path}
    if [[ "${sm_mode}" == "false" ]]; then
        gen_rsa_node_cert "${ca_cert_path}" "${node_cert_path}" "${type}" 2>&1
    else
        gen_sm_node_cert "${ca_cert_path}" "${node_cert_path}" "${type}" 2>&1
    fi
}

generate_chain_cert(){
    local sm_mode="$1"
    local chain_cert_path="$2"
    mkdir -p "${chain_cert_path}"
    if [[ "${sm_mode}" == "false" ]]; then
        gen_chain_cert "${chain_cert_path}" 2>&1
    else
        gen_sm_chain_cert "${chain_cert_path}" 2>&1
    fi
}

generate_node_account()
{
    local output_path="${1}"
    if [ ! -d "${output_path}" ];then
        mkdir -p ${output_path}
    fi
    if [ ! -f /tmp/secp256k1.param ];then
        ${OPENSSL_CMD} ecparam -out /tmp/secp256k1.param -name secp256k1
    fi
    ${OPENSSL_CMD} genpkey -paramfile /tmp/secp256k1.param -out ${output_path}/node.pem
    # generate nodeid
    ${OPENSSL_CMD} ec -text -noout -in "${output_path}/node.pem" 2> /dev/null | sed -n '7,11p' | tr -d ": \n" | awk '{print substr($0,3);}' | cat >"$output_path"/node.nodeid
}

generate_sm_node_account()
{
    local output_path="${1}"
    if [ ! -d "${output_path}" ];then
        mkdir -p ${output_path}
    fi
    if [ ! -f ${sm2_params} ];then
        generate_sm_sm2_param ${sm2_params}
    fi
    ${OPENSSL_CMD} genpkey -paramfile ${sm2_params} -out ${output_path}/node.pem 2>/dev/null
    $OPENSSL_CMD ec -in "$output_path/node.pem" -text -noout 2> /dev/null | sed -n '7,11p' | sed 's/://g' | tr "\n" " " | sed 's/ //g' | awk '{print substr($0,3);}'  | cat > "$output_path/node.nodeid"
}

exit_with_clean()
{
    local content=${1}
    echo -e "\033[31m[ERROR] ${content}\033[0m"
    if [ -d "${output_dir}" ];then
        rm -rf ${output_dir}
    fi
    exit 1
}

check_and_install_tassl(){
if [ -n "${sm_mode}" ]; then
    if [ ! -f "${OPENSSL_CMD}" ];then
        local tassl_link_perfix="${cdn_link_header}/FISCO-BCOS/tools/tassl-1.0.2"
        LOG_INFO "Downloading tassl binary from ${tassl_link_perfix}..."
        if [[ -n "${macOS}" ]];then
            curl -#LO "${tassl_link_perfix}/tassl_mac.tar.gz"
            mv tassl_mac.tar.gz tassl.tar.gz
        else
            if [[ "$(uname -p)" == "aarch64" ]];then
                curl -#LO "${tassl_link_perfix}/tassl-aarch64.tar.gz"
                mv tassl-aarch64.tar.gz tassl.tar.gz
            elif [[ "$(uname -p)" == "x86_64" ]];then
                curl -#LO "${tassl_link_perfix}/tassl.tar.gz"
            else
                LOG_ERROR "Unsupported platform"
                exit 1
            fi
        fi
        tar zxvf tassl.tar.gz && rm tassl.tar.gz
        chmod u+x tassl
        mkdir -p "${HOME}"/.fisco
        mv tassl "${HOME}"/.fisco/tassl
    fi
fi
}

help() {
    echo $1
    cat <<EOF
Usage:
    -c <commands>                       [Required] the operation command, support generate_all_cert/generate_ca_cert/generate_node_cert/generate_sdk_cert and generate_private_key now
    -o <output dir>                     [Optional] output directory, default ./nodes
    -s <SM model>                       [Optional] SM SSL connection or not, default no
    -h Help
EOF
    exit 0
}

parse_params() {
    while getopts "o:d:c:sh" option; do
        case $option in
        c) command="$OPTARG";;
        d) 
            ca_cert_path="$OPTARG"
            dir_must_exists "${ca_cert_path}"
            ;;
        
        o)
            output_dir="$OPTARG"
            mkdir -p "$output_dir"
            dir_must_exists "${output_dir}"
            ;;
        s) sm_mode="true" ;;
        h) help ;;
        *) help ;;
        esac
    done
}

generate_all_cert(){
    LOG_INFO "generate all cert"
    ca_dir="${output_dir}/ca"
    cert_dir="${output_dir}/ssl"
    sdk_dir="${output_dir}/sdk"
    mkdir -p "$ca_dir"
    mkdir -p "$cert_dir"
    mkdir -p "$sdk_dir"
    generate_chain_cert "${sm_mode}" "${ca_dir}"
    generate_single_node_cert "${sm_mode}" "${ca_dir}" "${cert_dir}" "ssl"
    generate_single_node_cert "${sm_mode}" "${ca_dir}" "${sdk_dir}" "sdk"
    LOG_INFO "generate all cert success"
}

generate_ca_cert()
{
    LOG_INFO "generate ca cert"
    ca_dir="${output_dir}/ca"
    mkdir -p "$ca_dir"
    generate_chain_cert "${sm_mode}" "${ca_dir}"
    LOG_INFO "generate ca cert success"
}

generate_node_cert()
{
    LOG_INFO "generate node cert"
    cert_dir="${output_dir}/ssl"
    mkdir -p "$cert_dir"
    generate_single_node_cert "${sm_mode}" "${ca_cert_path}" "${cert_dir}" "ssl"
    LOG_INFO "generate node cert success"
}

generate_sdk_cert()
{
    LOG_INFO "generate sdk cert"
    sdk_dir="${output_dir}/sdk"
    mkdir -p "$sdk_dir"
    generate_single_node_cert "${sm_mode}" "${ca_cert_path}" "${sdk_dir}" "sdk"
    LOG_INFO "generate node cert success"
}

generate_cert_node_private_key()
{
    LOG_INFO "Generate node private key"
    if [[ "${sm_mode}" == "false" ]]; then
        generate_node_account "${output_dir}"
    else
        generate_sm_node_account "${output_dir}"
    fi
    LOG_INFO "Generate node private key success"
}

main() {
    parse_params "$@"
    # FIXME: use openssl 1.1 to generate gm certificates
    check_env
    check_and_install_tassl
    cert_conf="${output_dir}/cert.cnf"
    if [[ "${command}" == "generate_all_cert" ]]; then
        generate_all_cert
    elif [[ "${command}" == "generate_ca_cert" ]]; then
        generate_ca_cert
    elif [[ "${command}" == "generate_node_cert" ]]; then
        generate_node_cert
    elif [[ "${command}" == "generate_sdk_cert" ]]; then
        generate_sdk_cert
    elif [[ "${command}" == "generate_private_key" ]]; then
        generate_cert_node_private_key
    fi
}

main "$@"
