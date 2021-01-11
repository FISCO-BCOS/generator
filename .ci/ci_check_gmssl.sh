#!/bin/bash

set -e

bash .ci/download_bin.sh -g
cd ..
cp -r ./generator ~/generator-A
cp -r ./generator ~/generator-B
cp -r ./generator ~/generator-C
cd ./generator
./generator --generate_chain_certificate ./dir_chain_ca -g
ls ./dir_chain_ca
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyA -g
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyB -g
./generator --generate_agency_certificate ./dir_agency_ca ./dir_chain_ca agencyC -g
cp ./dir_chain_ca/gmca.crt ./dir_agency_ca/agencyA/gmagency.crt ./dir_agency_ca/agencyA/gmagency.key ~/generator-A/meta/
cp ./dir_chain_ca/gmca.crt ./dir_agency_ca/agencyB/gmagency.crt ./dir_agency_ca/agencyB/gmagency.key ~/generator-B/meta/
cp ./dir_chain_ca/gmca.crt ./dir_agency_ca/agencyC/gmagency.crt ./dir_agency_ca/agencyC/gmagency.key ~/generator-C/meta/
cd ~/generator-B
sed -i 's/p2p_listen_port=30300/p2p_listen_port=30302/g' ./conf/node_deployment.ini
sed -i 's/p2p_listen_port=30301/p2p_listen_port=30303/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20200/channel_listen_port=20202/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20201/channel_listen_port=20203/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8545/jsonrpc_listen_port=8547/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8546/jsonrpc_listen_port=8548/g' ./conf/node_deployment.ini
./generator --generate_all_certificates ./agencyB_send -g -G
cp -r ./agencyB_send ~/generator-A/
cp -r ./agencyB_send/peers.txt ~/generator-C/peerB.txt
cd ~/generator-C
sed -i 's/p2p_listen_port=30300/p2p_listen_port=30304/g' ./conf/node_deployment.ini
sed -i 's/p2p_listen_port=30301/p2p_listen_port=30305/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20200/channel_listen_port=20204/g' ./conf/node_deployment.ini
sed -i 's/channel_listen_port=20201/channel_listen_port=20205/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8545/jsonrpc_listen_port=8549/g' ./conf/node_deployment.ini
sed -i 's/jsonrpc_listen_port=8546/jsonrpc_listen_port=8550/g' ./conf/node_deployment.ini
./generator --generate_all_certificates ./agencyC_send -g -G
cp -r ./agencyC_send ~/generator-A/
cp -r ./agencyC_send/peers.txt ~/generator-B/peerC.txt
cd ~/generator-A
./generator --generate_all_certificates ./agencyA_send -g -G
cp -r ./agencyA_send/peers.txt ~/generator-B/peersA.txt
cp -r ./agencyA_send/peers.txt ~/generator-C/peersA.txt
cd ~/generator-A
cp ./agencyB_send/* ./meta/
cp ./agencyC_send/* ./meta/
./generator --create_group_genesis ./group -g
cp ./meta/group.1.genesis ~/generator-B/meta
cp ./meta/group.1.genesis ~/generator-C/meta
cd ~/generator-A
cat ./agencyB_send/peers.txt >> ./peers.txt
cat ./agencyC_send/peers.txt >> ./peers.txt
ls ./meta
cat ./meta/gmcert_127.0.0.1_30300.crt
cat ./meta/gmagency.crt
ls ./meta/node_127.0.0.1_30300
./generator --build_install_package ./peers.txt ./nodeA -g -G
bash ./nodeA/start_all.sh
cat ./nodeA/node_127.0.0.1_30300/config.ini
cd ~/generator-B
cat ./peersA.txt >> ./peersC.txt
./generator --build_install_package ./peersC.txt ./nodeB -g -G
bash ./nodeB/start_all.sh
cd ~/generator-C
cat ./peersA.txt >> ./peersB.txt
./generator --build_install_package ./peersB.txt ./nodeC -g -G
bash ./nodeC/start_all.sh
ps aux| grep fisco-bcos |grep -v grep
result=$(ps aux| grep fisco-bcos |grep -v grep)
if [ -z "$result" ]
then
    echo "start build nodes failed"
    return 1
fi
echo "start succeed"
# tail -f ~/generator-A/nodeA/node_127.0.0.1_30300/log/log* | grep ++++
curl -X POST --data '{"jsonrpc":"2.0","method":"sendRawTransaction","params":[1, "0xf90114a003eebc46c9c0e3b84799097c5a6ccd6657a9295c11270407707366d0750fcd598411e1a30084b2d05e008201f594bab78cea98af2320ad4ee81bba8a7473e0c8c48d80a48fff0fc400000000000000000000000000000000000000000000000000000000000000040101a48fff0fc40000000000000000000000000000000000000000000000000000000000000004b8408234c544a9f3ce3b401a92cc7175602ce2a1e29b1ec135381c7d2a9e8f78f3edc9c06ee55252857c9a4560cb39e9d70d40f4331cace4d2b3121b967fa7a829f0a00f16d87c5065ad5c3b110ef0b97fe9a67b62443cb8ddde60d4e001a64429dc6ea03d2569e0449e9a900c236541afb9d8a8d5e1a36844439c7076f6e75ed624256f"],"id":83}' http://127.0.0.1:8545 > code.txt
cat ./code.txt
echo "transaction get code is "
tx_result=$(grep result < ./code.txt | grep -v grep)
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
./generator --create_group_genesis ./data -g
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
curl -X POST --data '{"jsonrpc":"2.0","method":"sendRawTransaction","params":[2, "0xf904a29f4c2e8b955ef35c8289f1726e32caf2c32073555422576b08c27bcd194f73aa0a8402faf0808201f58080b903ed608060405234801561001057600080fd5b506040805190810160405280600d81526020017f48656c6c6f2c20576f726c6421000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b6102d7806101166000396000f30060806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063299f7f9d146100515780633590b49f146100e1575b600080fd5b34801561005d57600080fd5b5061006661014a565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156100a657808201518184015260208101905061008b565b50505050905090810190601f1680156100d35780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156100ed57600080fd5b50610148600480360381019080803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091929192905050506101ec565b005b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156101e25780601f106101b7576101008083540402835291602001916101e2565b820191906000526020600020905b8154815290600101906020018083116101c557829003601f168201915b5050505050905090565b8060009080519060200190610202929190610206565b5050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061024757805160ff1916838001178555610275565b82800160010185558215610275579182015b82811115610274578251825591602001919060010190610259565b5b5090506102829190610286565b5090565b6102a891905b808211156102a457600081600090555060010161028c565b5090565b905600a165627a7a72305820cd976bae667bddab3f7d7a18439756272f142a40fc32f3ce2c5571490fffe8220029010280b84016e4e9765819bce5a1b8561f2d8f433f16c54d4ea69ef91d7a5836514f1c0dbf16eac056a5bc4273748ec45a5f8397879110502393d71daa10b2ab0bc63edb19a07d3bfd5c79d288fd19aa1e1c748eab8a402769b27ac705497cb8041a3361b295a024463ef1f1f974e595624d50facddcc5872989189f05d074e2257a0e060556be"],"id":83}' http://127.0.0.1:8550 > code.txt
echo "transaction get code is "
tx_result=$(grep result < ./code.txt| grep -v grep)
if [ -z "$tx_result" ]
then
    echo "transaction failed"
    return 1
fi
echo "send transaction succeed"