# MuonDST Framework

This code serves as a template for new Ntuplizers to work with CMSSW. Basic instructions for installation and standard modifications can be found below.
It presents an example where a ROOT tree if filled with plain Ntuples made from pat::Muon variables read from MiniAOD. It is configured to read Cosmic data from the NoBPTX dataset.

The Ntuplizer is an EDAnalyzer. More information about this class and its structure can be found in https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookWriteFrameworkModule.

## How to install

Recommended release for this framework is the latest CMSSW version released for trigger studies (as of today 18/11/2024, CMSSW_14_0_17). To install simply do:

```
cmsrel CMSSW_X_Y_Z
cd CMSSW_X_Y_Z/src
cmsenv
mkdir Analysis
cd Analysis
git clone git@github.com:CeliaFernandez/MuonDST-Framework.git
scram b -j 8
```

## Plugins

### Efficiencies in MC simulation

Managed by the ```efficiencyMC``` plugin declared in ```plugins/efficiencyMC.cc```.

Gets a set of efficiencies wrt the generated muons in the sample, for now assuming that their mother particle is a Dark Photon $Z_{D}$ (```pdgId=1023```). Testing dataset is:
```
/HTo2ZdTo2mu2x_MZd-6_ctau-10mm-pythia8/fernance-private-RunIII2024Summer24-HLTnoPU-de85c6dd9fb422b173a50ba3383d69ce/USER
```
(See details of this sample in Productions section)

How to run locally (just for testing):
```
cmsRun runMCEfficiency_cfg.py inputDataset=/HTo2ZdTo2mu2x_MZd-6_ctau-10mm-pythia8/fernance-private-RunIII2024Summer24-HLTnoPU-de85c6dd9fb422b173a50ba3383d69ce/USER minFile=0 maxFile=1 output=output
```

How to run with condor (within ```MuonDST-Framework/test/condor/```):
```
# sh runMCEfficiency_onCondor.sh [DATASET] [OUTPUT_PATH]
sh runMCEfficiency_onCondor.sh /HTo2ZdTo2mu2x_MZd-6_ctau-10mm-pythia8/fernance-private-RunIII2024Summer24-HLTnoPU-de85c6dd9fb422b173a50ba3383d69ce/USER /eos/user/f/fernance/DST-Muons/Reconstruction-studies/HZdZd/v1
```


## How to re-HLT a given sample

In MC (only tried here so far) e.g.:
```
hltGetConfiguration /users/elfontan/2024Scouting/CMSSW_14_0_0_GRun_V107/HLT/V5 --globaltag auto:phase1_2024_realistic --mc --unprescale --output minimal --max-events 100 --input /store/mc/Run3Winter24Digi/JPsiToMuMu_PT-0to100_pythia8-gun/GEN-SIM-RAW/KeepSi_133X_mcRun3_2024_realistic_v8-v2/2540000/005264ab-2a76-4f83-ac29-8e27a73cdc7c.root --eras Run3 --l1-emulator uGT --l1 L1Menu_Collisions2024_v1_1_0_xml > hltMC_JPsi.py
```

To study the scouting muon in the samples, some lines should be added to specify those to be kept in the output.


## How to run in crab a given work (reHLT or not)

Should be done with the ```launch_crab.py``` script:
```
python3 scripts/launch_crab.py [path to cfg] [dataset] [reference name]
```

An example:
```
python3 scripts/launch_crab.py python/reHLT/hltMC_GRun_V107_ROIplusDR_noDQM.py /JPsiToMuMu_PT-0to100_pythia8-gun/Run3Winter24Digi-KeepSi_133X_mcRun3_2024_realistic_v8-v2/GEN-SIM-RAW JPsiROI-prod
```

