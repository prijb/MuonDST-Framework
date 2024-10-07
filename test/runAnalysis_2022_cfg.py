import FWCore.ParameterSet.Config as cms
import os


process = cms.Process("demo")
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load('Configuration.StandardSequences.Services_cff')

# Debug printout and summary.
process.load("FWCore.MessageService.MessageLogger_cfi")

process.options = cms.untracked.PSet(
  wantSummary = cms.untracked.bool(True),
  # Set up multi-threaded run. Must be consistent with config.JobType.numCores in crab_cfg.py.
  numberOfThreads=cms.untracked.uint32(1)
)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag

# Select number of events to be processed
nEvents = 1000
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(nEvents) )

#
process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )

# Read events
listOfFiles = ['/store/data/Run2022D/ScoutingPFRun3/RAW/v1/000/357/538/00000/054a28d5-6cb6-430c-9fe8-d0d12762a5eb.root']
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( listOfFiles ),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(0)
  )
process.GlobalTag = GlobalTag(process.GlobalTag, '124X_dataRun3_Prompt_v10')

## Define the process to run 
## 
process.load("Analysis.MuonDST-Framework.analysis_cfi")

#process.p = cms.EndPath(process.ntuples)
process.p = cms.Path(process.gtStage2Digis+process.analysis2022)

