import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import os

## In line command options
options = VarParsing.VarParsing('analysis')
options.register('inputDataset',
                 '',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Input dataset")
options.register('minFile',
                 0,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Minimum file to process")
options.register('maxFile',
                 10,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Maximum file to process")
options.register('output',
                 './',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Output path")
options.parseArguments()

## Process
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
nEvents = -1
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(nEvents) )

# Read events
#
#listOfFiles = ['file:outputScoutingPF.root']
#
#inputdir = '/eos/user/f/fernance/DST-Muons/Datasets/JPsiToMuMu_PT-0to100_pythia8-gun/V107-2024prep/240429_193512/0000/'
#listOfFiles = ['file:' + os.path.join(inputdir, f) for f in os.listdir(inputdir) if '.root' in f]
#
if 'file:' not in options.inputDataset:
    if options.inputDataset!='':
        listOfFiles = (os.popen("""dasgoclient -query="file dataset=%s instance=prod/phys03" """%(options.inputDataset)).read()).split('\n')
    listOfFiles = listOfFiles[options.minFile:options.maxFile]
else:
    listOfFiles = [options.inputDataset]
print("List of files to read (%i):"%len(listOfFiles))
print(listOfFiles)
#listOfFiles = (os.popen("""dasgoclient -query="file dataset=/HTo2ZdTo2mu2x_MZd-6_ctau-10mm-pythia8/fernance-private-RunIII2024Summer24-HLTnoPU-de85c6dd9fb422b173a50ba3383d69ce/USER instance=prod/phys03" """).read()).split('\n')
#listOfFiles = ['/store/user/fernance/GENHLT_Scouting/HTo2ZdTo2mu2x_MZd-6_ctau-10mm-pythia8/private-RunIII2024Summer24-HLTnoPU/241020_202318/0000/EXO-digi-hlt_48.root']
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( listOfFiles ),
    bypassVersionCheck = cms.untracked.bool(True),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(0)
  )
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase1_2024_realistic')

## Define the process to run 
## 
process.load("Analysis.MuonDST-Framework.efficiency_cfi")

process.efficiencyMC.nameOfOutput = cms.string("%s/output_%iTo%i.root"%(options.output,options.minFile,options.maxFile))

process.p = cms.EndPath(process.efficiencyMC)

