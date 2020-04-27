#!/bin/bash

set -e

bash .ci/download_bin.sh
./generator --generate_chain_certificate ./dir_chain_ca
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyA
cp ./dir_chain_ca/ca.crt ./dir_agency_ca/agencyA/agency.crt ./dir_agency_ca/agencyA/agency.key  ./meta
cat > ./conf/node_deployment.ini << EOF
[group]
group_id=1

[node0]
; Host IP for the communication among peers.
; Please use your ssh login IP.
p2p_ip=127.0.0.1
; Listening IP for the communication between SDK clients.
; This IP is the same as p2p_ip for the physical host.
; But for virtual host e.g., VPS servers, it is usually different from p2p_ip.
; You can check accessible addresses of your network card.
; Please see https://tecadmin.net/check-ip-address-ubuntu-18-04-desktop/
; for more instructions.
rpc_ip=127.0.0.1
channel_ip=0.0.0.0
p2p_listen_port=30300
channel_listen_port=20200
jsonrpc_listen_port=8545

[node1]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
channel_ip=0.0.0.0
p2p_listen_port=30301
channel_listen_port=20201
jsonrpc_listen_port=8546

[node2]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
channel_ip=0.0.0.0
p2p_listen_port=30302
channel_listen_port=20202
jsonrpc_listen_port=8547

[node3]
p2p_ip=127.0.0.1
rpc_ip=127.0.0.1
channel_ip=0.0.0.0
p2p_listen_port=30303
channel_listen_port=20203
jsonrpc_listen_port=8548
EOF

./generator --generate_all_certificates ./cert_test

pwd
ls ./meta

cp ./meta/node_127.0.0.1_30300/node.nodeid  ./meta/node_127.0.0.1_30300.nodeid
cp ./meta/node_127.0.0.1_30301/node.nodeid  ./meta/node_127.0.0.1_30301.nodeid
cp ./meta/node_127.0.0.1_30302/node.nodeid  ./meta/node_127.0.0.1_30302.nodeid
cp ./meta/node_127.0.0.1_30303/node.nodeid  ./meta/node_127.0.0.1_30303.nodeid

./generator --create_group_genesis_with_nodeid ./group
./generator --build_package_only ./test_package_only ./peers_error_file.txt

./generator --add_group ./group/group.1.genesis ./test_package_only

cp ./meta/node_127.0.0.1_30300/* ./test_package_only/node_127.0.0.1_30300/conf/
cp ./meta/node_127.0.0.1_30301/* ./test_package_only/node_127.0.0.1_30301/conf/
cp ./meta/node_127.0.0.1_30302/* ./test_package_only/node_127.0.0.1_30302/conf/
cp ./meta/node_127.0.0.1_30303/* ./test_package_only/node_127.0.0.1_30303/conf/


bash ./test_package_only/start_all.sh
ps aux| grep fisco-bcos |grep -v grep
result=$(ps aux| grep fisco-bcos |grep -v grep)
if [ -z "$result" ]
then
    echo "start build nodes failed"
    return 1
fi
echo "start succeed"
curl -X POST --data '{"jsonrpc":"2.0","method":"sendRawTransaction","params":[1, "0xf8d3a003922ee720bb7445e3a914d8ab8f507d1a647296d563100e49548d83fd98865c8411e1a3008411e1a3008201f894d6c8a04b8826b0a37c6d4aa0eaa8644d8e35b79f80a466c9913900000000000000000000000000000000000000000000000000000000000000040101a466c9913900000000000000000000000000000000000000000000000000000000000000041ba08e0d3fae10412c584c977721aeda88df932b2a019f084feda1e0a42d199ea979a016c387f79eb85078be5db40abe1670b8b480a12c7eab719bedee212b7972f775"],"id":83}' http://127.0.0.1:8545 > code.txt
cat ./code.txt
echo "transaction get code is "
tx_result=$(grep result < ./code.txt | grep -v grep)
if [ -z "$tx_result" ]
then
    echo "transaction failed"
    return 1
fi
echo "send transaction succeed"
