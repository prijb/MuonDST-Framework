# Parent script which drives submission of make_L1DoubleMuonEfficiency.py across a whole dataset
# Example submission command: python3 scripts/make_L1DoubleMuonEfficiency_submit.py --input files/2024i_files_full.txt --output outputs/output_vtx_jpsi --redirector root://xrootd-cms.infn.it/ --opts useVtx selectJpsi
import os
import time
import argparse

#Get current directory
cwd = os.getcwd()
current_time = time.strftime("%Y%m%d_%H%M%S")
#current_time = "240725"

parser = argparse.ArgumentParser(description="Submit L1DoubleMuonEfficiency jobs")
parser.add_argument("--input", "-i", type=str, help="Input dataset filelist (text file)")
parser.add_argument("--output", "-o", type=str, help="Output directory for results")
parser.add_argument("--nfiles", "-n", default=-1, type=int, help="Number of files to process (default: -1 for all files)")
parser.add_argument('--hlt', type=str, default='all', help='HLT path to select for orthogonal trigger (default: all)')
parser.add_argument("--redirector", "-r", type=str, help="XRootD redirector (e.g., root://xrootd-cms.infn.it/)")
parser.add_argument("--opts", type=str, nargs="*", help="Additional store_true flags like --useVtx, --selectJpsi")
args = parser.parse_args()

input_txt_file = args.input
output_dir = args.output
nfiles = args.nfiles
hlt = args.hlt
redirector = args.redirector
opts = args.opts
script = "scripts/make_L1DoubleMuonEfficiency.py"
logdir = f"logs/{current_time}"

print("\nJob submission details")
print(f"Input file: {input_txt_file}")
print(f"Output directory: {output_dir}")
print(f"nfiles: {nfiles}")
print(f"HLT: {hlt}")
print(f"Redirector: {redirector}")
print(f"Options: {opts}")

print(f"Creating output directory: {output_dir}")
os.makedirs(output_dir, exist_ok=True)
print(f"Creating log directory: {logdir}")
os.makedirs(logdir, exist_ok=True)

# Read input file list
filelist = []
print(f"Reading {nfiles} files from {input_txt_file}...")
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

extra_opts = ""
if opts is not None:
  for opt in opts:
      extra_opts += f"--{opt} "
with open("scripts/make_L1DoubleMuonEfficiency_submit_args.txt", "w") as f:
    for i_file, file_path in enumerate(filelist):
        f.write(f"{file_path} {output_dir}/output_{i_file}.root\n")

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
python {script} --infile $1 --outfile $2 --hlt {hlt} {extra_opts}
"""

# Write and give execute permission
with open("scripts/make_L1DoubleMuonEfficiency_wrapper.sh", "w") as f:
    f.write(wrapper_file_content)
os.system("chmod +x scripts/make_L1DoubleMuonEfficiency_wrapper.sh")

# Create the HTCondor submit file
submit_file_content = f"""\
Universe = vanilla
Executable = scripts/make_L1DoubleMuonEfficiency_wrapper.sh
Arguments = $(input_file) $(output_file)
Log = {logdir}/job_$(Cluster).log
Output = {logdir}/job_$(Cluster)_$(Process).out
Error = {logdir}/job_$(Cluster)_$(Process).err
request_cpus = 1
request_memory = 4GB
use_x509userproxy = true
+MaxRuntime = 7199
Queue input_file, output_file from scripts/make_L1DoubleMuonEfficiency_submit_args.txt
"""

with open("scripts/make_L1DoubleMuonEfficiency_submit.submit", "w") as f:
    f.write(submit_file_content)

# Delete existing log files
os.system(f"rm {logdir}/*")

# Run the condor job
os.system("condor_submit scripts/make_L1DoubleMuonEfficiency_submit.submit")

print("Condor job submitted!")
