# Coffea/Awkward version of L1DoubleMuonEfficiency
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

import dask_awkward as dak
import hist.dask as hda

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

class L1DoubleMuonEfficiencyProcessor(processor.ProcessorABC):
    def __init__(self, hlt='all', useVtx=False, selectJpsi=False):
        self.hlt = hlt
        self.useVtx = useVtx
        self.selectJpsi = selectJpsi
        self.muon_collection_key = "ScoutingMuonVtx" if useVtx else "ScoutingMuonNoVtx"
        self.l1_triggers_to_measure = [
            "DoubleMu_15_7", 
            "DoubleMu8_SQ",
            "DoubleMu4p5er2p0_SQ_OS_Mass_Min7", "DoubleMu4p5_SQ_OS_dR_Max1p2", 
            "DoubleMu4er2p0_SQ_OS_dR_Max1p6",
            "DoubleMu0_Upt6_IP_Min1_Upt4", "DoubleMu0_Upt6_SQ_er2p0",
            "DoubleMu0_Upt7_SQ_er2p0", "DoubleMu0_Upt8_SQ_er2p0",
        ]
        self.hlt_triggers_to_measure = ["PFScouting_DoubleMuon"]
        

    def process(self, events):
        # Initialize outputs
        muon_collection_key = self.muon_collection_key

        # Trigger efficiency histograms
        trigger_axis = hist.axis.StrCategory([], growth=True, name="trigger", label="Trigger")
        #pt_axis = hist.axis.Regular(100, 0, 50, name="pt", label="Probe $p_T$ (GeV)")
        pt_axis = hist.axis.Variable([0, 1, 2, 3, 4, 5, 7, 9, 11, 13, 15, 20, 30, 40, 50], name="pt", label="Probe $p_T$ (GeV)")
        mass_axis = hist.axis.Regular(30, 2.8, 3.4, name="mass", label="Dimuon Mass (GeV)")
        h_trigger_pt_den = hda.hist.Hist(trigger_axis, pt_axis, storage="weight", label="Counts")
        h_trigger_pt_num = hda.hist.Hist(trigger_axis, pt_axis, storage="weight", label="Counts")
        h_trigger_mass_den = hda.hist.Hist(trigger_axis, mass_axis, storage="weight", label="Counts")
        h_trigger_mass_num = hda.hist.Hist(trigger_axis, mass_axis, storage="weight", label="Counts")

        # Cutflows are also just histograms
        cutflow_axis = hist.axis.StrCategory([], growth=True, name="cutflow", label="Cutflow")
        h_cutflow = hda.hist.Hist(cutflow_axis, hist.axis.Regular(1, 0, 1, name="cutflow_count", label="Count"), storage="weight", label="Counts")
        h_cutflow.fill(cutflow="num_events", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuon"])*0)

        # HLT selection
        if self.hlt == 'all':
            events = events[
                events["DST"]["PFScouting_DoubleEG"] | 
                events["DST"]["PFScouting_JetHT"] |
                events["DST"]["PFScouting_ZeroBias"]
            ]
        else:
            events = events[events["DST"][self.hlt]]
        h_cutflow.fill(cutflow="num_events_orthogonal", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuon"])*0)

        # Pre-filter to have exactly 2 OS muons 
        events = events[ak.num(events[muon_collection_key]) >= 2]
        events = events[events[muon_collection_key, "charge"][:, 0] * events[muon_collection_key, "charge"][:, 1] < 0]

        # Tag and probe muons
        tag_muon_mask = events[muon_collection_key, "pt"][:, 0] > events[muon_collection_key, "pt"][:, 1]

        tag_record = {}
        probe_record = {}

        vars = ["pt", "eta", "phi", "trk_dxy", "trk_dxyError", "trk_chi2", "trk_ndof", "charge"]
        for var in vars:
            tag_record[var] = events[muon_collection_key, var][:, 0]*tag_muon_mask + events[muon_collection_key, var][:, 1]*(~tag_muon_mask)
            probe_record[var] = events[muon_collection_key, var][:, 0]*(~tag_muon_mask) + events[muon_collection_key, var][:, 1]*(tag_muon_mask)
        tag_record["trk_absdxy"] = np.abs(tag_record["trk_dxy"])
        probe_record["trk_absdxy"] = np.abs(probe_record["trk_dxy"])
        tag_record["mass"] = ak.ones_like(tag_record["pt"]) * 0.105658
        probe_record["mass"] = ak.ones_like(probe_record["pt"]) * 0.
        tag_record["trk_chi2_over_ndof"] = tag_record["trk_chi2"] / tag_record["trk_ndof"]
        probe_record["trk_chi2_over_ndof"] = probe_record["trk_chi2"] / probe_record["trk_ndof"]

        tag = ak.zip(tag_record, with_name="PtEtaPhiMCandidate", behavior=candidate.behavior)
        probe = ak.zip(probe_record, with_name="PtEtaPhiMCandidate", behavior=candidate.behavior)
        dimuon = tag + probe

        # Apply pT, eta, chi2 and dR cuts
        pt_cut = (tag.pt > 2.0) & (probe.pt > 2.0)
        eta_cut = (np.abs(tag.eta) < 2.4) & (np.abs(probe.eta) < 2.4)
        chi2_cut = (tag.trk_chi2_over_ndof < 3.0) & (probe.trk_chi2_over_ndof < 3.0)
        dr = tag.delta_r(probe)
        dr_cut = (dr > 0.1)
        overall_cut = pt_cut & eta_cut & chi2_cut & dr_cut
        tag = tag[overall_cut]
        probe = probe[overall_cut]
        dimuon = dimuon[overall_cut]
        events = events[overall_cut]
        h_cutflow.fill(cutflow="num_events_prefilter", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuon"])*0)


        if self.selectJpsi:
            # Apply J/Psi selection
            jpsi_mask = (dimuon.mass > 2.8) & (dimuon.mass < 3.4)
            tag = tag[jpsi_mask]
            probe = probe[jpsi_mask]
            events = events[jpsi_mask]
        h_cutflow.fill(cutflow="num_events_selection", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuon"])*0)

        # Fill histograms
        for l1_trigger_to_measure in self.l1_triggers_to_measure:
            h_trigger_mass_den.fill(trigger=l1_trigger_to_measure, mass=dimuon.mass)
            h_trigger_mass_num.fill(trigger=l1_trigger_to_measure, mass=dimuon.mass[events["L1"][l1_trigger_to_measure]])
            h_trigger_pt_den.fill(trigger=l1_trigger_to_measure, pt=probe.pt)
            h_trigger_pt_num.fill(trigger=l1_trigger_to_measure, pt=probe.pt[events["L1"][l1_trigger_to_measure]])
            
        for hlt_trigger_to_measure in self.hlt_triggers_to_measure:
            h_trigger_mass_den.fill(trigger=hlt_trigger_to_measure, mass=dimuon.mass)
            h_trigger_mass_num.fill(trigger=hlt_trigger_to_measure, mass=dimuon.mass[events["DST"][hlt_trigger_to_measure]])
            h_trigger_pt_den.fill(trigger=hlt_trigger_to_measure, pt=probe.pt)
            h_trigger_pt_num.fill(trigger=hlt_trigger_to_measure, pt=probe.pt[events["DST"][hlt_trigger_to_measure]])

        return {
            "trigger_pt_den": h_trigger_pt_den,
            "trigger_pt_num": h_trigger_pt_num,
            "trigger_mass_den": h_trigger_mass_den,
            "trigger_mass_num": h_trigger_mass_num,
            "cutflow": h_cutflow,
        }
    
    def postprocess(self, accumulator):
        pass

# Example submission: python3 scripts_dask/make_L1DoubleMuonEfficiency_dask.py --infile files/2024i_files.txt --redirector root://xrootd-cms.infn.it/ --outfile /vols/cms/pb4918/HLTScouting/MuonPOG/MuonScoutingNano/outputs/output.root --useVtx --selectJpsi --cluster lx04
def main():
    parser = argparse.ArgumentParser(description="Coffea processor for L1 Double Muon Efficiency")
    parser.add_argument("--infile", type=str, help="Input file")
    parser.add_argument("--outfile", type=str, default="output_coffea.root", help="Output file (default: output_coffea.root)")
    parser.add_argument("--redirector", type=str, help="Redirector URL for input files (e.g. root://xrootd-cms.infn.it/)")
    parser.add_argument("--hlt", type=str, default="all", help="HLT path to select (default: all)")
    parser.add_argument("--useVtx", action='store_true', help="Use ScoutingMuonVtx collection")
    parser.add_argument("--selectJpsi", action='store_true', help="Select J/Psi candidates")
    parser.add_argument("--cluster", type=str, choices=['local', 'lxplus', 'lx04'], default='local', help="Cluster type to use (default: local)")
    args = parser.parse_args()

    cwd = os.getcwd()
    infile = args.infile
    outfile = args.outfile
    redirector = args.redirector
    hlt = args.hlt
    useVtx = args.useVtx
    selectJpsi = args.selectJpsi
    # Change these parameters based on your own proxy location and appropriate port number
    user_proxy_dir = "/vols/cms/pb4918/HLTScouting/MuonPOG/MuonScoutingNano/proxy/cms.proxy"
    log_dir = "/vols/cms/pb4918/HLTScouting/MuonPOG/MuonScoutingNano/logs/dask_logs"
    #n_port = 8786
    n_port = 60000
    os.makedirs(log_dir, exist_ok=True)

    print(f"Job spec")
    if hlt == 'all': print("  HLT: all")
    else: print(f"  HLT: {hlt}")
    if useVtx: print("  Using ScoutingMuonVtx collection")
    if selectJpsi: print("  Selecting only J/Psi candidates")

    # Generate fileset from input text file list
    fileset = {"2024": {"files": {}}}
    with open(infile, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if redirector is None: infile_name = line
            else: infile_name = f"{redirector}{line}"
            #print(f"Processing file: {infile_name}")
            fileset["2024"]["files"][infile_name] = "Events"


    # Check port availability
    if not check_port(n_port):
        raise RuntimeError(
            f"Port '{n_port}' is now occupied on this node. Try another one."
        )

    # Environment related settings
    env_extra = [
        f"cd {cwd}",
        "source /home/hep/pb4918/cms_source.sh",
        "source /home/hep/pb4918/mambainit.sh",
        "micromamba activate coffea_env",
        f"export X509_USER_PROXY={user_proxy_dir}",
    ]

    # Dask cluster setup
    if args.cluster == 'local':
        print("Using local Dask cluster")
        client = Client()
    
    elif args.cluster == 'lxplus':
        print("Using lxplus Dask cluster")
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
        cluster.adapt(minimum=0, maximum=1000)
        print(cluster.job_script())
        client = Client(cluster)

    elif args.cluster == 'lx04':
        print("Using lx04 Dask cluster")
        from dask_iclx import ICCluster
        cluster = ICCluster(
            cores = 1,
            memory = '3000MB',
            disk = '10GB',
            death_timeout = '60',
            lcg = False,
            nanny = False,
            container_runtime = 'none',
            log_directory = '/vols/cms/pb4918/HLTScouting/MuonPOG/MuonScoutingNano/logs/dask_logs',
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
        cluster.adapt(minimum=0, maximum=100)
        print(cluster.job_script())
        client = Client(cluster)

    # Job execution and monitoring
    print("Dashboard running at", client.dashboard_link)
    dataset_runnable, dataset_updated = preprocess(
        fileset,
        step_size=100000,
        skip_bad_files=True,
    )
    processor_instance = L1DoubleMuonEfficiencyProcessor(hlt=hlt, useVtx=useVtx, selectJpsi=selectJpsi)
    to_compute = apply_to_fileset(
        processor_instance,
        dataset_runnable,
        schemaclass=ScoutingNanoAODSchema,
    )
    (output, ) = dask.compute(to_compute)
    print(output)

    # All the keys in the output are histograms
    print(f"Saving output to {outfile}")
    with uproot.recreate(outfile) as f:
        for key, hist in output["2024"].items():
            f[key] = hist


if __name__ == "__main__":
    main()
    