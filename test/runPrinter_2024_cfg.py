import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import os

options = VarParsing('analysis')
options.register('nmin',
                 0, # Default value
                 VarParsing.multiplicity.singleton, # Singleton means only one value
                 VarParsing.varType.int, # Type of the argument
                 "Number min")

options.register('nmax',
                 10, # Default value
                 VarParsing.multiplicity.singleton, # Singleton means only one value
                 VarParsing.varType.int, # Type of the argument
                 "Number max")
options.parseArguments()

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
nEvents = -1
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(nEvents) )

#
process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )

# Read events
def list_root_files(directory):
    root_files = []
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".root"):
                root_files.append('file:'+os.path.abspath(os.path.join(subdir, file)))
    return root_files

inputdir = '/eos/cms/store/data/Run2024D/ScoutingPFRun3/HLTSCOUT/v1/000/380/945/00000/'
listOfFiles = ['file:' + os.path.join(inputdir, f) for f in os.listdir(inputdir) if '.root' in f][:10]
listOfFiles = ['/store/data/Run2024F/ScoutingPFRun3/HLTSCOUT/v1/000/382/014/00000/c512f0f0-24f7-4a25-8352-803eef581bd4.root']
listOfFiles = list_root_files('/eos/cms/tier0/store/data/Run2024G/ScoutingPFMonitor/RAW/v1/000')
#listOfFiles = ['/store/mc/Run3Winter24Digi/JPsiToMuMu_PT-0to100_pythia8-gun/GEN-SIM-RAW/KeepSi_133X_mcRun3_2024_realistic_v8-v2/2550000/762c1253-c13b-4301-bf2f-fec9bca27bd7.root']
print(len(listOfFiles))
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( listOfFiles[options.nmin:options.nmax] ),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(0)
  )
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v4')

## Define the process to run 
## 
process.load("Analysis.MuonDST-Framework.printer_cfi")

process.printer2024.nameOfOutput = cms.string('/eos/user/f/fernance/DST-Muons/PrinterG/outout_%i.root'%(options.nmin))

#process.p = cms.EndPath(process.ntuples)
process.p = cms.Path(process.gtStage2Digis+process.printer2024)

