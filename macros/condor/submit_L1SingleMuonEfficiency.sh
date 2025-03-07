#!/bin/bash

cp /tmp/x509up_u103471 x509up_u103471
export X509_USER_PROXY=x509up_u103471

tag="TTAG"
indir="IINDIR"
hlt="HHLT"

export TAG=${tag}
export INDIR=${indir}
export HLT=${hlt}

mkdir logs_L1SingleMuonEfficiency
#rm logs_L1SingleMuonEfficiency/*
condor_submit condor/submit_L1SingleMuonEfficiency.sub 
