#!/bin/bash

cp /tmp/x509up_u103471 x509up_u103471
export X509_USER_PROXY=x509up_u103471

indir=$1

export INDIR=${indir}

mkdir logs_L1DoubleMuonEfficiency
#rm logs_L1SingleMuonEfficiency/*
condor_submit condor/submit_L1DoubleMuonEfficiency.sub 
