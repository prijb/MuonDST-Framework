# Script to resubmit jobs which might have failed due to file retrieval issues
import sys
import os 
import argparse 
import numpy as np

# Example: python3 scripts/make_resubmit.py --output_dir outputs/2025Monitoring/2025c_vtx_jpsi/ --num_jobs 138
parser = argparse.ArgumentParser(description="Check for missing files")
parser.add_argument("--output_dir", "-i", type=str, help="Input directory with files")
parser.add_argument("--num_jobs", "-n", type=int, help="Number of jobs")
parser.add_argument("--resubmit", "-r", action='store_true', help="Whether to resubmit the job or not")
parser.add_argument("--run_local", "-l", action='store_true', help="Whether to run locally or on condor")
args = parser.parse_args()

output_dir = args.output_dir
num_jobs = args.num_jobs
resubmit = args.resubmit
run_local = args.run_local

files = []
file_prefix = None
for file in os.listdir(output_dir):
    #file_num = file.split(".root")[0].split("_")[-1]
    file_start = file.split(".root")[0]
    file_prefix = file_start.split("_")[0]
    file_num = file_start.split("_")[-1]
    files.append(int(file_num))

files_expected = np.arange(0, num_jobs)
files_missing = np.setdiff1d(files_expected, files, assume_unique=False)
files_missing = [f"{file_prefix}_{i}.root" for i in files_missing]
print(f"{num_jobs - len(files_missing)}/{num_jobs} jobs completed, {len(files_missing)} missing")
print("Missing files:", files_missing)

# Make a text file of the missing files by finding the corresponding jobs in the args file
lines_new = []
with open("scripts/make_submit_args.txt", "r") as f:
    lines = f.readlines()
    nline = 0
    for line in lines:
        if nline > 10: break
        input_file_fullpath = line.split(",")[1]
        output_file_fullpath = line.split(",")[0]
        output_file = output_file_fullpath.split("/")[-1]
        if output_file in files_missing:
            lines_new.append(line)

with open("scripts/make_resubmit_args.txt", "w") as f:
    f.writelines(lines_new)

resubmit_text = """\
Universe = vanilla
Executable = scripts/make_wrapper.sh
Arguments = "'$(input_file)' '$(output_file)'"
Log = logs/resubmit/job_$(Cluster).log
Output = logs/resubmit/job_$(Cluster)_$(Process).out
Error = logs/resubmit/job_$(Cluster)_$(Process).err
request_cpus = 1
request_memory = 4GB
use_x509userproxy = true
+MaxRuntime = 7199
Queue output_file, input_file from scripts/make_resubmit_args.txt
"""

with open("scripts/make_resubmit.submit", "w") as f:
    f.write(resubmit_text)

if run_local:
    print("Running locally...")
    with open("scripts/make_resubmit_args.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            local_cmd = f"./scripts/make_wrapper.sh {line}"
            print(f"Running command: {local_cmd}")
            os.system(local_cmd)

if resubmit:
    print(f"Resubmitting {len(lines_new)} jobs...")
    os.system("rm logs/resubmit/*")
    os.system("condor_submit scripts/make_resubmit.submit")




