# 2024 samples generation

This a private production made from existing TSG campaign targetting 2024 preparation and EXO requests for HAHM models.
Since at the production of the 2024 preparation campaign the NoVtx reconstruction wasn't there, I had to modify some things by hand.
Also, I have problems with L1 emulation for CICADA, not affecting these results but it's what I could do better at this point.
I used ```CMSSW_14_0_18``` to be close to data taking release but maybe a more recent version is needed.

**Gen command**:
```
Configuration/GenProduction/python/EXO-Run3Summer22EEwmLHEGS-01411-fragment.py --python_filename EXO-Run3Summer2024wmLHEGS-01411_1_cfg.py --eventcontent RAWSIM,LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --fileout file:EXO-Run3Summer2024wmLHEGS-01411.root --conditions 140X_mcRun3_2024_realistic_v14 --beamspot DBrealistic --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed=int(12345) --step LHE,GEN,SIM --geometry DB:Extended --era Run3_2023 --no_exec --mc -n 10
```

**DIIRAW-HLT**:
```
cmsDriver.py  --python_filename digi_hlt_cfg.py --eventcontent RAWSIM --pileup 2023_LHC_Simulation_12p5h_9h_hybrid2p23 --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --fileout file:EXO-digi-hlt.root --pileup_input "dbs:/MinBias_TuneCP5_13p6TeV-pythia8/Run3Winter24GS-133X_mcRun3_2024_realistic_v7-v1/GEN-SIM" --conditions 140X_mcRun3_2024_realistic_v14 --step DIGI,L1,DIGI2RAW,HLT --geometry DB:Extended --filein file:EXO-Run3Summer2024wmLHEGS-01411.root --era Run3_2023 --no_exec --mc 10
```
