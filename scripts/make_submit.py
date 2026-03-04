# Generic wrapper script with option to read multiple files in one job
import os
import sys
import argparse

"""
Examples:
python3 scripts/make_submit.py --input filelists/filelist_hltphysics_baseline_gfal.txt --output outputs/test_gfal --nfiles 8 --nfiles_per_job 3 --script scripts/make_dummy.py
python3 scripts/make_submit.py --input filelists/filelist_hltphysics_baseline_das.txt --output outputs/test_das --nfiles 8 --nfiles_per_job 3 --script scripts/make_dummy.py --redirector root://xrootd-cms.infn.it/
"""
parser = argparse.ArgumentParser(description="Submit wrapper for jobs")
parser.add_argument("--input", "-i", type=str, help="Input dataset filelist (text file)")
parser.add_argument("--output", "-o", type=str, help="Output directory for results")
parser.add_argument("--nfiles", "-n", default=-1, type=int, help="Number of files to process (default: -1 for all files)")
parser.add_argument("--nfiles_per_job", "-nj", default=1, type=int, help="Number of files to process per job (default: 1)")
parser.add_argument("--redirector", "-r", type=str, help="XRootD redirector (e.g., root://xrootd-cms.infn.it/, root://cms-xrd-global.cern.ch/)")
parser.add_argument('--script', default="scripts/make_L1DoubleMuonEfficiency.py", type=str, help='Script to run on each file')
parser.add_argument("--opts", type=str, help="Additional options enclosed in one string")
args = parser.parse_args()

input_txt_file = args.input
output_dir = args.output
nfiles = args.nfiles
nfiles_per_job = args.nfiles_per_job
redirector = args.redirector
opts = args.opts
script = args.script
log_dir = f"logs/preprocess"
cwd = os.getcwd()

if opts is None:
    opts = ""

print("\nJob submission details")
print(f"Script: {script}")
print(f"Input file: {input_txt_file}")
print(f"Output directory: {output_dir}")
print(f"nfiles: {nfiles}, nfiles per job {nfiles_per_job}")
print(f"Redirector: {redirector}")
print(f"Additional options: {opts}")

print(f"\nCreating output directory: {output_dir}")
os.makedirs(output_dir, exist_ok=True)
print(f"Creating log directory: {log_dir}")
os.makedirs(log_dir, exist_ok=True)

# Read input file list
filelist = []
print(f"\nReading {nfiles} files from {input_txt_file}...")
i_file = 0
with open(input_txt_file, 'r') as f:
    for line in f:
        if i_file == nfiles: break
        file_path = line.strip()
        if file_path:  # Skip empty lines
            if redirector is not None:
                filename_i = f"{redirector}{file_path}"
            else:
                filename_i = file_path
            filelist.append(filename_i)
            i_file += 1

nbatches = i_file//nfiles_per_job
nfiles_last = i_file%nfiles_per_job

print(f"Setting up {nbatches} jobs with {nfiles_last} files in the job after that")

# Args string has input files at the end due it being a list
with open("scripts/make_submit_args.txt", "w") as f:
    for i_job in range(nbatches):
        filelist_job = ""
        for i_file_in_job in range(nfiles_per_job):
            if i_file_in_job == 0:
                filelist_job = f"{filelist[(i_job * nfiles_per_job) + i_file_in_job]}"
            else:
                filelist_job += f" {filelist[(i_job * nfiles_per_job) + i_file_in_job]}"

        f.write(f'{output_dir}/output_{i_job}.root,{filelist_job}\n')

    # Add the last job
    if nfiles_last > 0:
        filelist_job = ""
        for i_file_in_job in range(nfiles_last):
            if i_file_in_job == 0:
                filelist_job = f"{filelist[(nbatches * nfiles_per_job) + i_file_in_job]}"
            else:
                filelist_job += f" {filelist[(nbatches * nfiles_per_job) + i_file_in_job]}"

        f.write(f'{output_dir}/output_{nbatches}.root,{filelist_job}\n')

# Create the wrapper file for the condor job
wrapper_file_content = f"""#!/bin/bash
cd {cwd}

# CMS loads
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/grid.cern.ch/alma9-ui-current/etc/profile.d/setup-alma9-test.sh

# Micromamba loads
export MAMBA_EXE='/home/hep/pb4918/.local/bin/micromamba';
export MAMBA_ROOT_PREFIX='/home/hep/pb4918/micromamba';
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias micromamba="$MAMBA_EXE"  # Fallback on help from micromamba activate
fi
unset __mamba_setup
eval "$(micromamba shell hook --shell bash)"

# Activate the micromamba environment
micromamba activate coffea_env

# Export the user proxy
export X509_USER_PROXY={cwd}/proxy/cms.proxy

# Run the Python script
python {script} --infile $1 --outfile $2 {opts}
"""

# Write and give execute permission
with open("scripts/make_wrapper.sh", "w") as f:
    f.write(wrapper_file_content)
os.system("chmod +x scripts/make_wrapper.sh")

# Create the HTCondor submit file
submit_file_content = f"""\
Universe = vanilla
Executable = scripts/make_wrapper.sh
Arguments = "'$(input_file)' '$(output_file)'"
Log = {log_dir}/job_$(Cluster).log
Output = {log_dir}/job_$(Cluster)_$(Process).out
Error = {log_dir}/job_$(Cluster)_$(Process).err
request_cpus = 1
request_memory = 4GB
use_x509userproxy = true
+MaxRuntime = 7199
Queue output_file, input_file from scripts/make_submit_args.txt
"""

with open("scripts/make_submit.submit", "w") as f:
    f.write(submit_file_content)

# Delete existing log files
os.system(f"rm {log_dir}/*")

# Run the condor job
os.system("condor_submit scripts/make_submit.submit")
print("Condor job submitted!")