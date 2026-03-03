# Script tom make filelist from an input directory (either using CRAB or from a directory)
import os 
import argparse
import numpy as np

# Sort files by file number for clarity
def sort_files(filelist_unsorted): 
    file_indices = np.array([int(f.split(".root")[-2].split("_")[-1]) for f  in filelist_unsorted])
    file_indices_sort_order = np.argsort(file_indices)

    filelist_sorted = []
    for i in file_indices_sort_order:
        filelist_sorted.append(filelist_unsorted[i])

    return filelist_sorted

"""
Use cases
Local: python3 scripts/make_filelist.py --input /vols/cms/pb4918/StoreNTuple/Scouting/2022FNanotron --output filelists/filelist_local.txt
Gfal: python3 scripts/make_filelist.py --input /store/user/ppradeep/Data/EphemeralHLTPhysics0/GRun_16_0_0_V30_baseline_ScoutingNano/260301_020955/000 --prefix root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms/ --gfal --output filelists/filelist_gfal.txt
DAS: python3 scripts/make_filelist.py --input /EphemeralHLTPhysics0/ppradeep-GRun_16_0_0_V30_baseline_ScoutingNano-00000000000000000000000000000000/USERs --das --dasprod prod/phys03 --output filelists/filelist_das.txt
"""
parser = argparse.ArgumentParser(description="Get filelist from dataset")
parser.add_argument("--input", "-i", type=str, help="Input dataset")
parser.add_argument("--prefix", "-p", type=str, help="Prefix used for dataset")
parser.add_argument("--gfal", "-g", action="store_true", help="Use gfal to list files")
parser.add_argument("--das", "-d", action="store_true", help="Use dasgoclient to list files")
parser.add_argument("--dasprod", "-dp", type=str, default="prod/global", help="Use dasgoclient to list files")
parser.add_argument("--dasaux", "-da", type=str, help="Additional filters (like run selection)")
parser.add_argument("--output", "-o", type=str, help="Output filelist")
args = parser.parse_args()

dataset_input = args.input
output = args.output
use_gfal = args.gfal
use_das = args.das
dasprod = args.dasprod
dasaux = args.dasaux
if args.dasaux is None:
    dasaux = ""
current_dir = os.getcwd()

# Exception handling
if use_gfal and use_das:
    raise RuntimeError("Using both DAS and gfal. Please pick one")

prefix = ""
if args.prefix is not None:
    prefix = args.prefix
    dataset_input = f"{prefix}{args.input}"

filelist = None

if use_gfal:
    print(f"Using gfal to find files in dataset {dataset_input}")
    filelist = os.popen(f"gfal-ls {dataset_input}").read().strip().split("\n")
    filelist = [f"{dataset_input}/{file}" for file in filelist if ".root" in file]
    filelist = sort_files(filelist)
elif use_das:
    print(f"Using dasgoclient to find files in dataset {dataset_input}")
    filelist = os.popen(f'dasgoclient -query="file dataset={dataset_input} instance={dasprod} {dasaux}"').read().strip().split("\n")
    filelist = [f"{file}" for file in filelist if ".root" in file]
    filelist = sort_files(filelist)
else:
    print(f"Using local storage for files in dataset {dataset_input}")
    filelist = os.popen(f"ls {dataset_input}").read().strip().split("\n")
    filelist = [f"{dataset_input}/{file}" for file in filelist if ".root" in file]
    filelist = sort_files(filelist)

# Write the filelist
with open(output, "w") as f_out:
    for f in filelist:
        f_out.write(f"{f}\n")
