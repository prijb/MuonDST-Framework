#!/bin/bash
cd /vols/cms/pb4918/HLTScouting/MuonPOG/MuonScoutingNano

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

# Activate the micromamba environment
micromamba activate coffea_env

# Export the user proxy
export X509_USER_PROXY=/vols/cms/pb4918/HLTScouting/MuonPOG/MuonScoutingNano/proxy/cms.proxy

# Run the Python script
python scripts/make_L1DoubleMuonEfficiency.py --infile $1 --outfile $2 --hlt all --useVtx --selectJpsi 
