#!/bin/bash

try_download_gmfisco() {
    echo "download fisco in travis ci!"
    while [ ! -f "./meta/fisco-bcos" ]
    do
    ./generator --download_fisco ./meta -g
    # bash <(curl -s https://raw.githubusercontent.com/FISCO-BCOS/FISCO-BCOS/master/tools/ci/download_bin.sh) -b dev -g
    # mv ./bin/fisco-bcos ./meta/fisco-bcos
    done
}

try_download_fisco() {
    echo "download fisco in travis ci!"
    while [ ! -f "./meta/fisco-bcos" ]
    do
    ./generator --download_fisco ./meta
    # bash <(curl -s https://raw.githubusercontent.com/FISCO-BCOS/FISCO-BCOS/master/tools/ci/download_bin.sh) -b dev
    # mv ./bin/fisco-bcos ./meta/fisco-bcos
    done
}

try_download_console() {
    echo "download fisco in travis ci!"
    while [ ! -d "./meta/console" ]
    do
    ./generator --download_console ./meta
    done
}

case "$1" in
-g)
    try_download_gmfisco
    ;;
-c)
    try_download_console
    ;;
*)
try_download_fisco
    help
    ;;
esac