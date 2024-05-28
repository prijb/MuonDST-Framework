from CRABClient.UserUtilities import config #, getUsernameFromSiteDB
from CRABAPI.RawCommand import crabCommand
import sys
import os

# System input variables
pset = sys.argv[1]
dataset = sys.argv[2]
requestName = sys.argv[3]

# Environment variables
base = os.environ["CMSSW_BASE"]
here = os.environ.get("PWD")

## Config file
config = config()
# General
config.General.workArea = here
config.General.requestName = requestName
config.General.transferLogs = True
config.General.transferOutputs = True
config.General.instance = 'prod'
# JobType
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = pset
config.JobType.maxMemoryMB = 4000 # May need to be decreased
# Data
config.Data.inputDataset = dataset
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 10
config.Data.publication = False # Unless specified
config.Data.outLFNDirBase = '/store/user/fernance/DST-Muons/Datasets'
config.Data.outputDatasetTag = 'V107-2024prep'
config.Data.partialDataset = True # Unless necessary...
# Site
config.Site.storageSite = "T3_CH_CERNBOX"

# Launch
print(config)
crabCommand('submit', config = config, dryrun = False)

