#!/bin/bash

WORKDIR=$1
DATASET=$2
FIRST=$3
LAST=$4
OUTPUT=$5

pushd $WORKDIR
eval `scramv1 runtime -sh`
pushd

cp $WORKDIR/test/runMCEfficiency_cfg.py .
cmsRun runMCEfficiency_cfg.py inputDataset=$DATASET minFile=$FIRST maxFile=$LAST output=$OUTPUT
rm runMCEfficiency_cfg.py
