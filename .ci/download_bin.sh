#!/bin/bash

try_download_gmfisco() {
    echo "download fisco in travis ci!"
    ./generator --download_fisco ./meta -g
    while [ ! -f "./meta/fisco-bcos" ]
    do
    ./generator --download_fisco ./meta -g
    done
}

try_download_fisco() {
    echo "download fisco in travis ci!"
    ./generator --download_fisco ./meta
    while [ ! -f "./meta/fisco-bcos" ]
    do
    ./generator --download_fisco ./meta
    done
}

try_download_console() {
    echo "download fisco in travis ci!"
    ./generator --download_console ./meta
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