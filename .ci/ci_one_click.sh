#!/bin/bash

set -e

bash .ci/download_bin.sh
cp -r ./tmp_one_click ./tmp_one_click_expand
bash ./one_click_generator.sh -b ./tmp_one_click
bash ./tmp_one_click/agencyA/node/start_all.sh
bash ./tmp_one_click/agencyB/node/start_all.sh
ls ./tmp_one_click/agencyA
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
cp ./tmp_one_click/group.* ./tmp_one_click_expand
cp ./tmp_one_click/peers* ./tmp_one_click_expand
cp ./tmp_one_click/ca.* ./tmp_one_click_expand
bash ./one_click_generator.sh -e ./tmp_one_click_expand
ls ./tmp_one_click/agencyA
cd ./tmp_one_click/agencyA/generator-agency
bash .ci/download_bin.sh -c
mv ./meta/console ./console
ls ./console/
cat ./console/conf/ca.crt
cat ./console/conf/config.toml