#!/bin/bash

set -e
echo "======= ci_check ============"
pip install -r requirements.txt
mkdir -p log
bash .ci/download_bin.sh
cd ..
cp -r ./generator ~/generator-A
cp -r ./generator ~/generator-B
cp -r ./generator ~/generator-C
cd ./generator
./generator --generate_chain_certificate ./dir_chain_ca
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyA
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyB
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyC
cp ./dir_chain_ca/ca.crt ./dir_agency_ca/agencyA/agency.crt ./dir_agency_ca/agencyA/agency.key ~/generator-A/meta/
cp ./dir_chain_ca/ca.crt ./dir_agency_ca/agencyB/agency.crt ./dir_agency_ca/agencyB/agency.key ~/generator-B/meta/
cp ./dir_chain_ca/ca.crt ./dir_agency_ca/agencyC/agency.crt ./dir_agency_ca/agencyC/agency.key ~/generator-C/meta/
cd ~/generator-B
sed -i 's/p2p_listen_port=30300/p2p_listen_port=30302/g' ./conf/node_deployment.ini
sed -i 's/p2p_listen_port=30301/p2p_listen_port=30303/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20200/channel_listen_port=20202/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20201/channel_listen_port=20203/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8545/jsonrpc_listen_port=8547/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8546/jsonrpc_listen_port=8548/g' ./conf/node_deployment.ini
./generator --generate_all_certificates ./agencyB_send
cp -r ./agencyB_send ~/generator-A/
echo "" >> ~/generator-C/peerB.txt
echo "\n" >> ~/generator-C/peerB.txt
echo "\r" >> ~/generator-C/peerB.txt
cat ./agencyB_send/peers.txt >> ~/generator-C/peerB.txt
echo "=======this is pre peersB.txt======"
cat ~/generator-C/peerB.txt
pwd
cd ~/generator-B
ls ./meta
cat ./meta/ca.crt
cat ./meta/cert_127.0.0.1_30302.crt
bash ./scripts/check_certificates.sh -t ./meta/ca.crt
bash ./scripts/check_certificates.sh -v ./meta/ca.crt ./meta/cert_127.0.0.1_30302.crt
cd ~/generator-C
sed -i 's/p2p_listen_port=30300/p2p_listen_port=30304/g' ./conf/node_deployment.ini
sed -i 's/p2p_listen_port=30301/p2p_listen_port=30305/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20200/channel_listen_port=20204/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20201/channel_listen_port=20205/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8545/jsonrpc_listen_port=8549/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8546/jsonrpc_listen_port=8550/g' ./conf/node_deployment.ini
./generator --generate_all_certificates ./agencyC_send
cp -r ./agencyC_send ~/generator-A/
cp -r ./agencyC_send/peers.txt ~/generator-B/peerC.txt
cd ~/generator-A
./generator --generate_all_certificates ./agencyA_send
cp -r ./agencyA_send/peers.txt ~/generator-B/peersA.txt
cp -r ./agencyA_send/peers.txt ~/generator-C/peersA.txt
cd ~/generator-A
cp ./agencyB_send/* ./meta/
cp ./agencyC_send/* ./meta/
./generator --create_group_genesis ./group
cat ./meta/group.1.genesis
cp ./meta/group.1.genesis ~/generator-B/meta
cp ./meta/group.1.genesis ~/generator-C/meta
cd ~/generator-A
cat ./agencyB_send/peers.txt >> ./peers.txt
cat ./agencyC_send/peers.txt >> ./peers.txt
./generator --build_install_package ./peers.txt ./nodeA
cat ./nodeA/node_127.0.0.1_30300/conf/node.nodeid
bash ./nodeA/start_all.sh
cd ~/generator-B
cat ./peersA.txt >> ./peersC.txt
./generator --build_install_package ./peersC.txt ./nodeB
bash ./nodeB/start_all.sh
cd ~/generator-C
cat ./peersA.txt >> ./peersB.txt
echo "" >> ~/generator-C/peerB.txt
echo "\n" >> ~/generator-C/peerB.txt
echo "\r" >> ~/generator-C/peerB.txt
echo "=======this is peersB.txt======"
cat peersB.txt
./generator --build_install_package ./peersB.txt ./nodeC
echo "=======this is nodeC's config.ini======"
cat ./nodeC/node_127.0.0.1_30304/config.ini
cat ./nodeC/node_127.0.0.1_30305/config.ini
bash ./nodeC/start_all.sh
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
tx_result=$(cat ./code.txt | grep result | grep -v grep)
echo $tx_result
if [ -z "$tx_result" ]
then
    echo "transaction failed"
    return 1
fi
echo "send transaction succeed"
cd ~/generator-A
sed -i 's/group_id=1/group_id=2/g' ./conf/group_genesis.ini
sed -i 's/127.0.0.1:30302/127.0.0.1:30304/g' ./conf/group_genesis.ini
sed -i 's/127.0.0.1:30303/127.0.0.1:30305/g' ./conf/group_genesis.ini
./generator --create_group_genesis ./data
./generator --add_group ./data/group.2.genesis ./nodeA
./generator --add_group ./data/group.2.genesis ~/generator-C/nodeC
bash ./nodeA/stop_all.sh
bash ./nodeA/start_all.sh
bash ~/generator-C/nodeC/stop_all.sh
ls ~/generator-C/nodeC/node_127.0.0.1_30305/conf
bash ~/generator-C/nodeC/start_all.sh
ps aux| grep fisco-bcos |grep -v grep
ps aux| grep fisco-bcos |grep -v grep
result=$(ps aux| grep fisco-bcos |grep -v grep)
if [ -z "$result" ]
then
    echo "start build nodes failed"
    return 1
fi
echo "start succeed"
curl -X POST --data '{"jsonrpc":"2.0","method":"sendRawTransaction","params":[2, "0xf8d3a003922ee720bb7445e3a914d8ab8f507d1a647296d563100e49548d83fd98865c8411e1a3008411e1a3008201f894d6c8a04b8826b0a37c6d4aa0eaa8644d8e35b79f80a466c9913900000000000000000000000000000000000000000000000000000000000000040102a466c9913900000000000000000000000000000000000000000000000000000000000000041ba08e0d3fae10412c584c977721aeda88df932b2a019f084feda1e0a42d199ea979a016c387f79eb85078be5db40abe1670b8b480a12c7eab719bedee212b7972f775"],"id":83}' http://127.0.0.1:8550 > code.txt
cat ./code.txt
echo "transaction get code is "
tx_result=$(cat ./code.txt | grep result | grep -v grep)
echo $tx_result
if [ -z "$tx_result" ]
then
    echo "transaction failed"
    return 1
fi
echo "send transaction succeed"
cd ~/generator-A
bash .ci/download_bin.sh -c
cat ./meta/console/conf/config.toml
# sudo apt-get install openjdk-8-jdk
cd ./meta/console/
ls
ls ./conf
cat ./conf/sdk.crt
cat ./conf/node.crt
nohup java -Djdk.tls.namedGroups="secp256k1" -cp "apps/*:conf/:lib/*:classes/:accounts/" console.Console $@ > myout1.file 2>&1 &
cat myout1.file
ps -ef | grep java
# download the 1.2.0 console
cd ../..
rm -rf ./meta/console
./generator --download_console meta --console_version 1.2.0
cat ./meta/console/conf/applicationContext.xml
cd ./meta/console/
nohup java -Djdk.tls.namedGroups="secp256k1" -cp "apps/*:conf/:lib/*:classes/:accounts/" console.ConsoleClient $@ > myout.file 2>&1 &
# getPeers
# deploy HelloWorld.sol
# q