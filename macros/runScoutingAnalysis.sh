#!/bin/bash

tag=$1
l1seed=$2
indir=$3
steps=$4

export TAG=${tag}
export L1SEED=${l1seed}
export INDIR=${indir}
export STEPS=${steps}
export SIZE=100000000

condor_submit submitScoutingAnalysis.sub 
