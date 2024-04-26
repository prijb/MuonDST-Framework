# MuonDST Framework

This code serves as a template for new Ntuplizers to work with CMSSW. Basic instructions for installation and standard modifications can be found below.
It presents an example where a ROOT tree if filled with plain Ntuples made from pat::Muon variables read from MiniAOD. It is configured to read Cosmic data from the NoBPTX dataset.

The Ntuplizer is an EDAnalyzer. More information about this class and its structure can be found in https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookWriteFrameworkModule.

## How to install

Recommended release for this framework is the latest CMSSW version released for trigger studies (as of today 26/04/2024, CMSSW_14_0_5). To install simply do:

```
cmsrel CMSSW_X_Y_Z
cd CMSSW_X_Y_Z/src
cmsenv
mkdir Analysis
cd Analysis
git clone git@github.com:CeliaFernandez/MuonDST-Framework.git
scram b -j 8
```

## Structure


## How to re-HLT a given sample

In MC (only tried here so far) e.g.:
```
hltGetConfiguration /users/elfontan/2024Scouting/CMSSW_14_0_0_GRun_V107/HLT/V5 --globaltag auto:phase1_2024_realistic --mc --unprescale --output minimal --max-events 100 --input /store/mc/Run3Winter24Digi/JPsiToMuMu_PT-0to100_pythia8-gun/GEN-SIM-RAW/KeepSi_133X_mcRun3_2024_realistic_v8-v2/2540000/005264ab-2a76-4f83-ac29-8e27a73cdc7c.root --eras Run3 --l1-emulator uGT --l1 L1Menu_Collisions2024_v1_1_0_xml > hltMC_JPsi.py
```

To study the scouting muon in the samples, some lines should be added to specify those to be kept in the output:



