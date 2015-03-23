#!/usr/bin/env bash
if [ -z "$CGRU_LOCATION" ]; then
    echo "CGRU_LOCATION not set - exiting in 3 secs!"
    sleep 3
    exit 1
fi

pushd $CGRU_LOCATION
source ./setup.sh
popd

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
$DIR/ocrSubmitUI.py