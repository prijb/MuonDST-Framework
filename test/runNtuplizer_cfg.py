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
  #numberOfThreads=cms.untracked.uint32(8)
)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag

# Select number of events to be processed
nEvents = 1000
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(nEvents) )

# Read events
listOfFiles = ['/store/data/Run2022D/NoBPTX/MINIAOD/PromptReco-v1/000/357/503/00000/ef047f11-b46d-4ae6-88c5-3f5ca19591be.root']
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( listOfFiles ),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(0)
  )
process.GlobalTag = GlobalTag(process.GlobalTag, '124X_mcRun3_2022_realistic_v5')

## Define the process to run 
## 
process.load("Analysis.standard-Ntuplizer.ntuples_cfi")

process.p = cms.EndPath(process.ntuples)

