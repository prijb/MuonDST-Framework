#!/bin/bash

cp /tmp/x509up_u103471 x509up_u103471
export X509_USER_PROXY=x509up_u103471

dataset=$1
input=$2
json=$3

export DATASET=${dataset}
export INPUT=${input}
export JSON=${json}

mkdir logs_skim
condor_submit scripts/submit_skim_2024.sub 
