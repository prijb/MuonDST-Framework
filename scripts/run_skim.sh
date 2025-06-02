#!/bin/bash

while ! [ -z "$1" ]; do
    FLAGS="$FLAGS $1"; shift;
done

source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-el9-gcc11-opt/setup.sh

cp /afs/cern.ch/work/f/fernance/private/Scouting/2025Analysis/CMSSW_15_0_5/src/MuonDST-Framework/*.json *
cp -r /afs/cern.ch/work/f/fernance/private/Scouting/2025Analysis/CMSSW_15_0_5/src/MuonDST-Framework/scripts .
cp -r /afs/cern.ch/work/f/fernance/private/Scouting/2025Analysis/CMSSW_15_0_5/src/Analysis/MuonDST-Framework/macros .
echo ${FLAGS}
python3 scripts/skim.py ${FLAGS}
rm *.json
rm -rf scripts
rm -rf macros
