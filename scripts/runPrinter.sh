#!/bin/bash

while ! [ -z "$1" ]; do
    FLAGS="$FLAGS $1"; shift;
done

pushd /afs/cern.ch/work/f/fernance/private/Scouting/2024Analysis/CMSSW_14_0_7/src/Analysis/MuonDST-Framework/
eval `scramv1 runtime -sh`
pushd

echo ${FLAGS}
cmsRun /afs/cern.ch/work/f/fernance/private/Scouting/2024Analysis/CMSSW_14_0_7/src/Analysis/MuonDST-Framework/test/runPrinter_2024_cfg.py ${FLAGS}
