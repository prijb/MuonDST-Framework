# Dummy script to test things like multiple file reading 
import argparse
import os
import sys
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from collections import defaultdict
import uproot
import awkward as ak
import hist
from hist import Hist
import coffea
from coffea import processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, ScoutingNanoAODSchema
from coffea.nanoevents.methods import candidate
from coffea.dataset_tools import (
    apply_to_fileset,
    max_chunks,
    preprocess,
)

import dask
from dask.distributed import Client, LocalCluster
import socket

# Dask port check
def check_port(port):
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", port))
        available = True
    except Exception:
        available = False
    sock.close()
    return available


class DummyProcessor(processor.ProcessorABC):
    def __init__(self):
        self.hlt = "PFScouting_DoubleMuonVtx"
    
    def process(self, events):
        # Cutflows are also just histograms
        cutflow_axis = hist.axis.StrCategory([], growth=True, name="cutflow", label="Cutflow")
        h_cutflow = hist.Hist(cutflow_axis, hist.axis.Regular(1, 0, 1, name="cutflow_count", label="Count"), storage="weight", label="Counts")
        h_cutflow.fill(cutflow="num_events", cutflow_count=ak.ones_like(events["event"])*0)

        return {
            "cutflow": h_cutflow
        }

    def postprocess(self, accumulator):
        pass

def main():
    # Example submission: python3 scripts/make_dummy.py --infile root://xrootd-cms.infn.it//store/data/Run2025C/ScoutingPFRun3/NANOAOD/PromptReco-v1/000/392/642/00000/1e348c1e-1b35-4c93-88bd-1b9da0aa7e51.root root://xrootd-cms.infn.it//store/data/Run2025C/ScoutingPFRun3/NANOAOD/PromptReco-v1/000/392/642/00000/4c54c306-d204-4d86-bdfb-2df563d9667f.root --outfile outputs/test/output_test.root 
    parser = argparse.ArgumentParser("Dummy script that just returns a histogram with the total number of events in the dataset")
    parser.add_argument("--infile", type=str, nargs="+", help="Input files")
    parser.add_argument("--outfile", type=str, default="output_coffea.root", help="Output file (default: output_coffea.root)")
    parser.add_argument("--daskcondor", action="store_true", help="Use dask for processing (Do not use if individual job is on condor)")
    parser.add_argument("--daskcluster", type=str, choices=['lxplus', 'lxic'], default='lxic', help="Cluster type to use for dask (default: lxic)")
    args = parser.parse_args()

    cwd = os.getcwd()
    infile = args.infile 
    outfile = args.outfile
    dask_condor = args.daskcondor
    dask_cluster = args.daskcluster

    # Input is a text file 
    if (len(infile) == 0) and (".txt" in infile[0]):
        print(f"{infile} is a text file, searching for files to add to filelist")
        infile_txt = infile[0]
        infile = []
        with open(infile_txt, 'r') as f:
            for line in f:
                file_path = line.strip()
                if file_path:  # Skip empty lines
                    if args.redirector is not None:
                        filename_i = f"{args.redirector}{file_path}"
                    else:
                        filename_i = file_path
                    infile.append(filename_i)

    print(f"Processing files: {infile}")
    fileset = {"2025": infile}

    # Default client
    client = Client()

    # If using dask over condor
    if dask_condor:
        print(f"\nUsing dask itself for condor scheduling")
        os.makedirs(f"{cwd}/dask_logs", exist_ok=True)

        # Environment related settings
        env_extra = [
            f"cd {cwd}",
            "source /home/hep/pb4918/cms_source.sh",
            "source /home/hep/pb4918/mambainit.sh",
            "micromamba activate coffea_env",
            f"export X509_USER_PROXY=proxy",
        ]

        if dask_cluster == 'lxplus':
            print("Using lxplus Dask cluster")

            if not check_port(60000):
                raise RuntimeError(
                    f"Port '60000' is now occupied on this node. Try another one."
                )

            from dask_lxplus import CernCluster
            cluster =  CernCluster(
                cores=1,
                memory='3GB',
                disk='10GB',
                death_timeout = '60',
                lcg = False,
                nanny = False,
                container_runtime = "none",
                log_directory = "/eos/user/p/ppradeep/HLTScouting/MuonPOG/CMSSW_15_0_8/src/MuonDST-Framework/logs",
                scheduler_options={
                    'port': 8786,
                    'host': socket.gethostname(),
                    },
                job_extra={
                    '+JobFlavour': '"longlunch"',
                    },
                extra = ['--worker-port 10000:10100'],
                python=sys.executable,
                worker_command="distributed.cli.dask_worker",
                job_script_prologue=env_extra,
            )
            cluster.adapt(minimum=6, maximum=250)
            print(cluster.job_script())
            client = Client(cluster)
            client.wait_for_workers(1)

        elif dask_cluster == 'iclx':
            print("Using iclx Dask cluster")

            if not check_port(8786):
                raise RuntimeError(
                    f"Port '8786' is now occupied on this node. Try another one."
                )

            from dask_iclx import ICCluster
            cluster = ICCluster(
                cores = 1,
                memory = '3000MB',
                disk = '10GB',
                death_timeout = '60',
                lcg = False,
                nanny = False,
                container_runtime = 'none',
                log_directory = f'{cwd}/dask_logs',
                scheduler_options = {
                    'port': 60000,
                    'host': socket.gethostname(),
                    'dashboard_address': ':8787',
                },
                job_extra = {
                    "+MaxRuntime": "7199",
                },
                name="ClusterName",
                job_script_prologue=env_extra,
            ) 
            cluster.adapt(minimum=6, maximum=250)
            print(cluster.job_script())
            client = Client(cluster)
            client.wait_for_workers(1)

        else:
            print(f"Unknown exception: --daskcondor enabled yet invalid cluster choice")

    print(f"Dask Client: {client}")


    processor_instance = DummyProcessor()
    executor = processor.DaskExecutor(client=client, retries=10)
    run = processor.Runner(
        executor=executor,
        schema=ScoutingNanoAODSchema,
        xrootdtimeout=300,
        chunksize=500000,
    )
    output = run(
        fileset,
        treename="Events",
        processor_instance=processor_instance,
    )

    print(output)

    # All the keys in the output are histograms
    print(f"\nSaving output to {outfile}")
    with uproot.recreate(outfile) as f:
        for key, hist in output.items():
            f[key] = hist

if __name__ == "__main__":
    main()