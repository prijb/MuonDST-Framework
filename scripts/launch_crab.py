from CRABClient.UserUtilities import config #, getUsernameFromSiteDB
from CRABAPI.RawCommand import crabCommand
import sys
import os

# System input variables
pset = sys.argv[1]
dataset = sys.argv[2]
requestName = sys.argv[3]
era = sys.argv[4]

if '2024' in era:
    lumiMask = 'Collisions24_13p6TeV_378981_381309_DCSOnly_TkPx.json' 
    lumiMask = 'Collisions24_13p6TeV_378981_381594_DCSOnly_TkPx.json' 
elif '2023D' in era:
    lumiMask = 'Cert_Collisions2023_eraD_369803_370790_Golden.json' 

# Environment variables
base = os.environ["CMSSW_BASE"]
here = os.environ.get("PWD")

## Config file
config = config()
# General
config.General.workArea = here
config.General.requestName = requestName
config.General.transferLogs = False
config.General.transferOutputs = True
config.General.instance = 'prod'
# JobType
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = pset
config.JobType.maxMemoryMB = 2500 # May need to be decreased
config.JobType.maxJobRuntimeMin = 3000 # May need to be decreased
config.JobType.outputFiles = ['output.root']
# Data
config.Data.inputDataset = dataset
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 4
config.Data.publication = False # Unless specified
config.Data.outLFNDirBase = '/store/user/fernance/DST-Muons/'+requestName
config.Data.outputDatasetTag = requestName
config.Data.lumiMask = lumiMask
#config.Data.partialDataset = True # Unless necessary...
# Site
config.Site.storageSite = "T2_US_UCSD"

# Launch
print(config)
crabCommand('submit', config = config, dryrun = False)

