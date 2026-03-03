#!/bin/bash
# Make the proxy directory if it doesn't exist
PROXY_DIR_NAME="proxy"
if [ ! -d "${PROXY_DIR_NAME}" ]; then
    mkdir ${PROXY_DIR_NAME}
fi

# Make some other directories (inputs, logs, outputs)
if [ ! -d "filelists" ]; then
    mkdir filelists
fi
if [ ! -d "logs" ]; then
    mkdir logs
fi
if [ ! -d "outputs" ]; then
    mkdir outputs
fi
if [ ! -d "plots" ]; then
    mkdir plots
fi

# CMS loads
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/grid.cern.ch/alma9-ui-current/etc/profile.d/setup-alma9-test.sh

# Micromamba loads
export MAMBA_EXE='/home/hep/pb4918/.local/bin/micromamba';
export MAMBA_ROOT_PREFIX='/home/hep/pb4918/micromamba';
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias micromamba="$MAMBA_EXE"  # Fallback on help from micromamba activate
fi
unset __mamba_setup
eval "$(micromamba shell hook --shell bash)"
micromamba activate coffea_env

# Proxy export
if [ -z ${X509_USER_PROXY+x} ]; then
    echo "Setting up proxy"
#    voms-proxy-init --rfc --voms cms --valid 192:00
    voms-proxy-init --rfc --voms cms --valid 192:00 --out ${PROXY_DIR_NAME}/cms.proxy
else
    echo "Proxy already set up"
fi
export X509_USER_PROXY=${PROXY_DIR_NAME}/cms.proxy

