#!/bin/bash
#
# Install this as "brnet" somewhere on your $PATH.  You will need the
# pip and venv modules for your python3 in order to use it.  This will
# create a virtualenv for brnet and source it before use, which will
# keep your system python environment clean.  If you want your virtualenv
# somewhere other than /usr/local/share/venv/brnet, put that into the
# $BRNET_VENV environment variable.
#
venv="${BRNET_VENV:=/usr/local/share/venv/brnet}"
if [ ! -d "${venv}" ]; then
    python3 -m venv ${venv}
fi
if [ ! -d "${venv}" ]; then
    echo "No virtualenv at ${venv}; giving up" 1>&2
    exit 1
fi
source ${venv}/bin/activate || exit 2
if [ "$(which brnet)" != "${venv}/bin/brnet" ]; then
    python3 -m pip install brnet
fi
if [ "$(which brnet)" != "${venv}/bin/brnet" ]; then
    cwd=$(pwd)
    mkdir -p "${venv}/src"
    cd "${venv}/src"
    if [ -d brnet ]; then
        cd brnet
        git checkout main
        git pull
    else
        git clone https://github.com/athornton/brnet
        cd brnet
    fi
    python3 -m pip install -e .
    cd "${cwd}"
fi
if [ "$(which brnet)" != "${venv}/bin/brnet" ]; then
    echo "No brnet in virtualenv; giving up" 1>&2
    exit 3
fi

brnet $*
