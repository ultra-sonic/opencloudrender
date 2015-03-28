#!/usr/bin/env bash
#if [ -z "$CGRU_LOCATION" ]; then
#    echo "CGRU_LOCATION not set - exiting in 3 secs!"
#    sleep 3
#    exit 1
#fi

#pushd $CGRU_LOCATION
#source ./setup.sh
#popd

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

#minimal afanasy setup
export CGRU_LOCATION=$DIR/../cgru
export AF_ROOT=${CGRU_LOCATION}/afanasy
export PYTHONPATH=${CGRU_LOCATION}/lib/python:${AF_ROOT}/python:$PYTHONPATH
#afanasy done

$DIR/ocrSubmitUI.py