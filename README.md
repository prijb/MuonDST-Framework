# MuonDST Framework (coffea)

This code serves as a reference for Muon Scouting studies using ScoutingNano. The scripts in this repository provide the following features
* Filelist construction from datasets
* Preprocessing scripts using Coffea Processors with Dask functionality
* Wrappers for submitting jobs on HTCondor using a given filelist
* Resubmission of missing/failed jobs 
* Plotting scripts on preprocessed output

ScoutingNano content documentation: https://cms-hlt-scouting-dev-pinkaew.docs.cern.ch/ScoutingNanoDoc/

## Installation

The installation of the dependencies in this repository assume the presence of micromamba. Once micromamba is installed, the packages can be installed using ```environment.yml``` as below
```
micromamba env create -n coffea_env -f environment.yml
```

Then run ```setup.sh``` to create auxillary directories, create a proxy and set environment variables
```
source setup.sh
```

## Filelist Construction

Filelists can be made using the ```scripts/make_filelist.py``` script for datasets located locally, via GFAL or via DAS example with example use cases below

Local
```
python3 scripts/make_filelist.py --input /vols/cms/pb4918/StoreNTuple/Scouting/2022F --output filelists/filelist_local.txt
```

GFAL
```
python3 scripts/make_filelist.py --input /store/user/ppradeep/Data/EphemeralHLTPhysics0/GRun_16_0_0_V30_baseline_ScoutingNano/260301_020955/000 --prefix root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms/ --gfal --output filelists/filelist_gfal.txt
```

DAS (with option to specify the production instance)
```
python3 scripts/make_filelist.py --input /EphemeralHLTPhysics0/ppradeep-GRun_16_0_0_V30_baseline_ScoutingNano-00000000000000000000000000000000/USERs --das --dasprod prod/phys03 --output filelists/filelist_das.txt
```

## Preprocessing

The preprocessing scripts require a list of input files (can be a singleton), and an output file location. Scripts use Coffea processors and Dask runners to produce histograms over this input list. The Dask runner features (like chunk size, schema, and xrootd timeout intervals) are modified in the `processor.Runner` declaration.

A simple example of one such script can be found in `scripts/make_dummy.py` which is run as follows
```
python3 scripts/make_dummy.py --infile "file1.root file2.root file3.root ..." --outfile outputs/output.root
``` 

### Dask Execution

Each of the scripts also has the feature of using Dask to submit condor jobs and aggregate outputs. This is done by adding the ```--daskcondor``` flag to your script and specifying the cluster you are active on using ```--daskcluster```. 

This implementation is currently compatible only with the CERN lxplus (```--daskcluster lxplus```) and Imperial College lx batch (```--daskcluster lxic```) system.

## Wrappers

One can also batch the above preprocessing scripts directly through HTCondor. ```make_submit.py``` fulfills this purpose by taking an input filelist (text file) and an output directory along with additional arguments

Jobs are submitted via the following template
```
python3 scripts/make_submit.py --input <path/filelist.txt> --output <output_directory> --script <scripts/script.py> --nfiles <nfiles> --nfiles_per_job <nfiles_per_job> --redirector <redirector> --opts <"opts">
```
where
* script: The script that the wrapper uses
* nfiles: Number of files from filelist to run on (default -1: all files)
* nfiles_per_job: Number of files to run on in each job (default 1: 1 file per job)
* redirector: Any redirectors to add to the filenames specfied in the filelist. Necessary for filelists produced from DAS. Example: root://xrootd-cms.infn.it/
* opts: One string which contains all the additional flags and arguments for your preprocessing script. Example: --opts "--hltpath DST_PFScouting_DoubleMuonVtx --prescalel1 --useVtx"

## Resubmission

In case of incomplete/missing jobs from the above wrapper script, one can use `scripts/make_resubmit.py` to search for incomplete jobs and resubmit as follows
```
python3 scripts/make_resubmit.py --output_dir <output_directory> --num_jobs <num_jobs> --resubmit
```
where
* output_directory: The directory where outputs from your wrapper job are suppossed to be in
* num_jobs: Number of jobs submitted (nfiles//nfiles_per_job + 1)
* resubmit: Flag to resubmit the job. Disable to double check if job counting is done correctly.

Note: Since this script uses the `scripts/make_submit_args.txt` file produced by `scripts/make_submit.py`, resubmission can only be done for the last execution of `scripts/make_submit.py`. Resubmission is done using separate `scripts/make_resubmit_args.txt` and `scripts/make_resubmit.submit` scripts