# Script to obtain trigger efficiencies for Single and Double Muon paths (with options for single and dimuon topologies)
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

# Lumi mask
from coffea.lumi_tools import LumiMask

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

# Processor definition
class EfficiencyProcessor(processor.ProcessorABC):
    def __init__(self, hltpath=None, l1seeds=None, orthogonalpaths=None, useVtx=False, resonance_mask=None, no_dimuon=False, lumi_mask=None, year=2024):
        # Path and seeds to measure
        self.hltpath = hltpath.replace("DST_", "")
        self.l1seeds = []
        if l1seeds is not None:
            for l1seed in l1seeds:
                self.l1seeds.append(l1seed.replace("L1_", ""))
        # Orthogonal path used as reference
        self.orthogonalpaths = orthogonalpaths
        # Selection criteria
        self.useVtx = useVtx
        self.no_dimuon = no_dimuon
        self.resonance_mask = resonance_mask
        # Muon type
        self.muon_collection_key = "ScoutingMuonVtx" if useVtx else "ScoutingMuonNoVtx"
        if year < 2024:
            if self.useVtx:
                raise ValueError("--useVtx is an invalid option for Scouting Muons before 2024")
            print(f"Year {self.year} is before 2024, setting muon_collection_key to ScoutingMuon")
            self.muon_collection_key = "ScoutingMuon"
        self.lumi_mask = LumiMask(lumi_mask) if lumi_mask is not None else None

        print("\nProcessor initialised with following attributes")
        print(f"HLT path to measure: {self.hltpath}")
        print(f"L1 seeds to measure: {self.l1seeds}")
        print(f"Orthogonal paths used as reference: {self.orthogonalpaths}")
        print(f"Muon collection: {self.muon_collection_key}")
        if lumi_mask is not None: print(f"Lumi mask applied from {lumi_mask}")
        print(f"No dimuons: {no_dimuon}")
        if self.resonance_mask is not None: print(f"Selecting muons from resonance: {self.resonance_mask}")
    
    def process(self, events):
        muon_collection_key = self.muon_collection_key
        cutflow_axis = hist.axis.StrCategory([], growth=True, name="cutflow", label="Cutflow")
        h_cutflow = hist.Hist(
            cutflow_axis, 
            hist.axis.Regular(1, 0, 1, name="cutflow_count", label="Count"), 
            storage="weight", 
            label="Counts"
        )
        # Trigger efficiency 
        #trigger_axis = hist.axis.StrCategory([], growth=True, name="trigger", label="Trigger")
        allpaths = [self.hltpath] + list(self.l1seeds)
        trigger_axis = hist.axis.StrCategory(allpaths, growth=False, name="trigger", label="Trigger")
        pt_axis = hist.axis.Variable([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30, 40, 50], name="pt", label="Probe pT [GeV]")
        eta_axis = hist.axis.Regular(24, -2.4, 2.4, name="eta", label="Probe Eta")
        dr_axis = hist.axis.Variable([0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.24, 0.28, 0.32, 0.36, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.6, 2.0, 3.0], name="dr", label="dR(Tag, Probe)")
        
        # Denominator histograms
        h_trigger_pt_eta_leading_den = hist.Hist(trigger_axis, pt_axis, eta_axis, storage="weight")
        h_trigger_pt_dr_leading_den = hist.Hist(trigger_axis, pt_axis, dr_axis, storage="weight")
        h_trigger_eta_dr_leading_den = hist.Hist(trigger_axis, eta_axis, dr_axis, storage="weight")
        h_trigger_pt_eta_dr_leading_den = hist.Hist(trigger_axis, pt_axis, eta_axis, dr_axis, storage="weight")
        h_trigger_pt_eta_subleading_den = hist.Hist(trigger_axis, pt_axis, eta_axis, storage="weight")
        h_trigger_pt_dr_subleading_den = hist.Hist(trigger_axis, pt_axis, dr_axis, storage="weight")
        h_trigger_eta_dr_subleading_den = hist.Hist(trigger_axis, eta_axis, dr_axis, storage="weight")
        h_trigger_pt_eta_dr_subleading_den = hist.Hist(trigger_axis, pt_axis, eta_axis, dr_axis, storage="weight")
        # Numerator
        h_trigger_pt_eta_leading_num = hist.Hist(trigger_axis, pt_axis, eta_axis, storage="weight")
        h_trigger_pt_dr_leading_num = hist.Hist(trigger_axis, pt_axis, dr_axis, storage="weight")
        h_trigger_eta_dr_leading_num = hist.Hist(trigger_axis, eta_axis, dr_axis, storage="weight")
        h_trigger_pt_eta_dr_leading_num = hist.Hist(trigger_axis, pt_axis, eta_axis, dr_axis, storage="weight")
        h_trigger_pt_eta_subleading_num = hist.Hist(trigger_axis, pt_axis, eta_axis, storage="weight")
        h_trigger_pt_dr_subleading_num = hist.Hist(trigger_axis, pt_axis, dr_axis, storage="weight")
        h_trigger_eta_dr_subleading_num = hist.Hist(trigger_axis, eta_axis, dr_axis, storage="weight")
        h_trigger_pt_eta_dr_subleading_num = hist.Hist(trigger_axis, pt_axis, eta_axis, dr_axis, storage="weight")

        # Starting event count
        h_cutflow.fill(cutflow="num_events", cutflow_count=ak.ones_like(events["event"])*0)

        # Luminosity mask
        if self.lumi_mask is not None:
            print("Applying luminosity mask...")
            good_lumi_mask = self.lumi_mask(events.run, events.luminosityBlock)
            events = events[good_lumi_mask]
        h_cutflow.fill(cutflow="num_events_lumi", cutflow_count=ak.ones_like(events["event"])*0)

        # Apply orthogonal triggers
        orthogonal_mask = ak.zeros_like(events["event"], dtype=bool)
        if len(self.orthogonalpaths) > 0:
            for orthogonalpath in self.orthogonalpaths:
                path_to_apply = orthogonalpath.replace("DST_", "")
                orthogonal_mask = orthogonal_mask | events["DST"][path_to_apply]
            
            events = events[orthogonal_mask]
        h_cutflow.fill(cutflow="num_events_orthogonal", cutflow_count=ak.ones_like(events["event"])*0)
        
        # Choice of topology affects selections
        if self.no_dimuon:
            print(f"\nSingle muon selections")
            events = events[ak.num(events[muon_collection_key]) == 1]
            # Sort the muons
            muons = events[muon_collection_key]
            muons_pt_order = ak.argsort(muons.pt, axis=1, ascending=False)
            muons = muons[muons_pt_order]

            eta_filter = np.abs(muons.eta) < 2.4
            normchi2_filter = muons.normchi2 < 3.0
            muon_filter = eta_filter & normchi2_filter
            print(f"Applying basic filters on muons")
            muons = muons[muon_filter]
            muon_num_filter = ak.num(muons) == 1 
            events = events[muon_num_filter]
            muons = muons[muon_num_filter]

            tag = muons[:, 0]
            probe = muons[:, 0]
            dr = ak.zeros_like(tag.pt)

            # Cuts for 2D histograms
            pt_cut = probe.pt > 10
            dr_cut = ak.ones_like(probe.pt, dtype=bool)
            eta_cut = np.abs(probe.eta) < 2.4

        else:
            print(f"\nDimuon selections")
            events = events[ak.num(events[muon_collection_key]) == 2]
            # Sort the muons
            muons = events[muon_collection_key]
            muons_pt_order = ak.argsort(muons.pt, axis=1, ascending=False)
            muons = muons[muons_pt_order]
            
            # Apply basic filters on muons (eta and normchi2) and only save events with at least two muons passing selections
            eta_filter = np.abs(muons.eta) < 2.4
            normchi2_filter = muons.normchi2 < 3.0
            os_filter = muons.charge[:, 0] != muons.charge[:, 1]
            muon_filter = eta_filter & normchi2_filter
            print(f"Applying basic filters on muons")
            muons = muons[muon_filter]
            muon_num_filter = ak.num(muons) == 2 
            events = events[muon_num_filter & os_filter]
            muons = muons[muon_num_filter & os_filter]
            dimuons = muons[:, 0] + muons[:, 1]

            # Apply a resonance selection if required
            resonance_mask = ak.ones_like(dimuons.mass, dtype=bool)
            if self.resonance_mask == "eta":
                print("Selecting only dimuons in mass range [0.527, 0.573]")
                resonance_mask = (dimuons.mass > 0.527) & (dimuons.mass < 0.573)
            elif self.resonance_mask == "rho":
                print("Selecting only dimuons in mass range [0.748, 0.812]")
                resonance_mask = (dimuons.mass > 0.748) & (dimuons.mass < 0.812)
            elif self.resonance_mask == "jpsi":
                print("Selecting only dimuons in mass range [3.0, 3.2]")
                resonance_mask = (dimuons.mass > 3.0) & (dimuons.mass < 3.2)
            elif self.resonance_mask == "psi2s":
                print("Selecting only dimuons in mass range [3.55, 3.805]")
                resonance_mask = (dimuons.mass > 3.55) & (dimuons.mass < 3.805)
            elif self.resonance_mask == "upsilon":
                print("Selecting only dimuons in mass range [9.9, 10.8]")
                resonance_mask = (dimuons.mass > 9.9) & (dimuons.mass < 10.8)
            elif self.resonance_mask == "z":
                print("Selecting only dimuons in mass range [71, 111]")
                resonance_mask = (dimuons.mass > 71) & (dimuons.mass < 111)
            elif self.resonance_mask == "all":
                print("Using OR of dimuon resonances: eta, rho, jpsi, psi2s, upsilon, z")
                resonance_mask = (
                    ((dimuons.mass > 0.527) & (dimuons.mass < 0.573)) |
                    ((dimuons.mass > 0.748) & (dimuons.mass < 0.812)) |
                    ((dimuons.mass > 3.0) & (dimuons.mass < 3.2)) |
                    ((dimuons.mass > 3.55) & (dimuons.mass < 3.805)) |
                    ((dimuons.mass > 9.9) & (dimuons.mass < 10.8)) |
                    ((dimuons.mass > 71) & (dimuons.mass < 111))
                )
            else:
                resonance_mask = ak.ones_like(dimuons.mass, dtype=bool)

            events = events[resonance_mask]
            muons = muons[resonance_mask]
            dimuons = dimuons[resonance_mask]
            dr = muons[:, 0].delta_r(muons[:, 1])

            # Make tag and probe pairs
            tag = muons[:, 0]
            probe = muons[:, 1]

            # Cuts for 2D histograms
            pt_cut = probe.pt > 10
            dr_cut = dr > 0.0
            eta_cut = np.abs(probe.eta) < 2.4

        # Fill histograms
        h_cutflow.fill(cutflow="num_events_selection", cutflow_count=ak.ones_like(events["event"])*0)

        # Fill HLT decision
        path_mask = events["DST"][self.hltpath]

        # Denominator
        # Leading
        h_trigger_pt_eta_dr_leading_den.fill(trigger=self.hltpath, pt=tag.pt, eta=tag.eta, dr=dr)
        h_trigger_pt_eta_leading_den.fill(trigger=self.hltpath, pt=tag.pt[dr_cut], eta=tag.eta[dr_cut])
        h_trigger_pt_dr_leading_den.fill(trigger=self.hltpath, pt=tag.pt[eta_cut], dr=dr[eta_cut])
        h_trigger_eta_dr_leading_den.fill(trigger=self.hltpath, eta=tag.eta[pt_cut], dr=dr[pt_cut])
        # Subleading
        h_trigger_pt_eta_dr_subleading_den.fill(trigger=self.hltpath, pt=probe.pt, eta=probe.eta, dr=dr)
        h_trigger_pt_eta_subleading_den.fill(trigger=self.hltpath, pt=probe.pt[dr_cut], eta=probe.eta[dr_cut])
        h_trigger_pt_dr_subleading_den.fill(trigger=self.hltpath, pt=probe.pt[eta_cut], dr=dr[eta_cut])
        h_trigger_eta_dr_subleading_den.fill(trigger=self.hltpath, eta=probe.eta[pt_cut], dr=dr[pt_cut])

        # Numerator
        # Leading
        h_trigger_pt_eta_dr_leading_num.fill(trigger=self.hltpath, pt=tag.pt[path_mask], eta=tag.eta[path_mask], dr=dr[path_mask])
        h_trigger_pt_eta_leading_num.fill(trigger=self.hltpath, pt=tag.pt[dr_cut & path_mask], eta=tag.eta[dr_cut & path_mask])
        h_trigger_pt_dr_leading_num.fill(trigger=self.hltpath, pt=tag.pt[eta_cut & path_mask], dr=dr[eta_cut & path_mask])
        h_trigger_eta_dr_leading_num.fill(trigger=self.hltpath, eta=tag.eta[pt_cut & path_mask], dr=dr[pt_cut & path_mask])
        # Subleading
        h_trigger_pt_eta_dr_subleading_num.fill(trigger=self.hltpath, pt=probe.pt[path_mask], eta=probe.eta[path_mask], dr=dr[path_mask])
        h_trigger_pt_eta_subleading_num.fill(trigger=self.hltpath, pt=probe.pt[dr_cut & path_mask], eta=probe.eta[dr_cut & path_mask])
        h_trigger_pt_dr_subleading_num.fill(trigger=self.hltpath, pt=probe.pt[eta_cut & path_mask], dr=dr[eta_cut & path_mask])
        h_trigger_eta_dr_subleading_num.fill(trigger=self.hltpath, eta=probe.eta[pt_cut & path_mask], dr=dr[pt_cut & path_mask])

        # Fill L1 decisions (optional)
        if len(self.l1seeds) > 0:
            for l1seed in self.l1seeds:
                path_mask = events["L1"][l1seed]

                # Denominator
                # Leading
                h_trigger_pt_eta_dr_leading_den.fill(trigger=l1seed, pt=tag.pt, eta=tag.eta, dr=dr)
                h_trigger_pt_eta_leading_den.fill(trigger=l1seed, pt=tag.pt[dr_cut], eta=tag.eta[dr_cut])
                h_trigger_pt_dr_leading_den.fill(trigger=l1seed, pt=tag.pt[eta_cut], dr=dr[eta_cut])
                h_trigger_eta_dr_leading_den.fill(trigger=l1seed, eta=tag.eta[pt_cut], dr=dr[pt_cut])
                # Subleading
                h_trigger_pt_eta_dr_subleading_den.fill(trigger=l1seed, pt=probe.pt, eta=probe.eta, dr=dr)
                h_trigger_pt_eta_subleading_den.fill(trigger=l1seed, pt=probe.pt[dr_cut], eta=probe.eta[dr_cut])
                h_trigger_pt_dr_subleading_den.fill(trigger=l1seed, pt=probe.pt[eta_cut], dr=dr[eta_cut])
                h_trigger_eta_dr_subleading_den.fill(trigger=l1seed, eta=probe.eta[pt_cut], dr=dr[pt_cut])

                # Numerator
                # Leading
                h_trigger_pt_eta_dr_leading_num.fill(trigger=l1seed, pt=tag.pt[path_mask], eta=tag.eta[path_mask], dr=dr[path_mask])
                h_trigger_pt_eta_leading_num.fill(trigger=l1seed, pt=tag.pt[dr_cut & path_mask], eta=tag.eta[dr_cut & path_mask])
                h_trigger_pt_dr_leading_num.fill(trigger=l1seed, pt=tag.pt[eta_cut & path_mask], dr=dr[eta_cut & path_mask])
                h_trigger_eta_dr_leading_num.fill(trigger=l1seed, eta=tag.eta[pt_cut & path_mask], dr=dr[pt_cut & path_mask])
                # Subleading
                h_trigger_pt_eta_dr_subleading_num.fill(trigger=l1seed, pt=probe.pt[path_mask], eta=probe.eta[path_mask], dr=dr[path_mask])
                h_trigger_pt_eta_subleading_num.fill(trigger=l1seed, pt=probe.pt[dr_cut & path_mask], eta=probe.eta[dr_cut & path_mask])
                h_trigger_pt_dr_subleading_num.fill(trigger=l1seed, pt=probe.pt[eta_cut & path_mask], dr=dr[eta_cut & path_mask])
                h_trigger_eta_dr_subleading_num.fill(trigger=l1seed, eta=probe.eta[pt_cut & path_mask], dr=dr[pt_cut & path_mask])

        return {
            "cutflow": h_cutflow,
            #"trigger_pt_eta_dr_leading_den": h_trigger_pt_eta_dr_leading_den,
            "trigger_pt_eta_leading_den": h_trigger_pt_eta_leading_den,
            "trigger_pt_dr_leading_den": h_trigger_pt_dr_leading_den,
            "trigger_eta_dr_leading_den": h_trigger_eta_dr_leading_den,
            #"trigger_pt_eta_dr_subleading_den": h_trigger_pt_eta_dr_subleading_den,
            "trigger_pt_eta_subleading_den": h_trigger_pt_eta_subleading_den,
            "trigger_pt_dr_subleading_den": h_trigger_pt_dr_subleading_den,
            "trigger_eta_dr_subleading_den": h_trigger_eta_dr_subleading_den,
            #"trigger_pt_eta_dr_leading_num": h_trigger_pt_eta_dr_leading_num,
            "trigger_pt_eta_leading_num": h_trigger_pt_eta_leading_num,
            "trigger_pt_dr_leading_num": h_trigger_pt_dr_leading_num,
            "trigger_eta_dr_leading_num": h_trigger_eta_dr_leading_num,
            #"trigger_pt_eta_dr_subleading_num": h_trigger_pt_eta_dr_subleading_num,
            "trigger_pt_eta_subleading_num": h_trigger_pt_eta_subleading_num,
            "trigger_pt_dr_subleading_num": h_trigger_pt_dr_subleading_num,
            "trigger_eta_dr_subleading_num": h_trigger_eta_dr_subleading_num,
        }

    def postprocess(self, accumulator):
        pass

def main():
    parser = argparse.ArgumentParser("Script that obtains efficiency of an HLT path and L1 seed using orthogonal triggers")
    parser.add_argument("--infile", type=str, nargs="+", help="Input files")
    parser.add_argument("--outfile", type=str, default="output_coffea.root", help="Output file (default: output_coffea.root)")
    parser.add_argument("--redirector", "-r", type=str, help="XRootD redirector (e.g., root://xrootd-cms.infn.it/)")
    # Processor specific
    parser.add_argument("--hltpath", type=str, help="HLT path to measure (eg. DST_PFScouting_DoubleMuonVtx)")
    parser.add_argument("--l1seeds", type=str, nargs="*", help="L1 seeds to measure (eg. L1_DoubleMu_15_7)")
    parser.add_argument("--orthogonalpaths", type=str, nargs="*", help="Orthogonal paths as reference (eg. DST_PFScouting_JetHT)")
    parser.add_argument("--useVtx", action="store_true", help="Use vtx muons")
    parser.add_argument("--resonance_mask", type=str, help="Resonance mask applied to dimuons (eg. jpsi)")
    parser.add_argument("--no_dimuon", action="store_true", help="Selections do not use dimuons")
    parser.add_argument("--lumi_mask", type=str, help="Path to luminosity mask if exists")
    parser.add_argument("--year", type=int, default=2024, help="Data year (for naming Scouting Muon type)")
    # Dask related 
    parser.add_argument("--daskcondor", action="store_true", help="Use dask for processing (Do not use if individual job is on condor)")
    parser.add_argument("--daskcluster", type=str, choices=['lxplus', 'lxic'], default='lxic', help="Cluster type to use for dask (default: lxic)")
    args = parser.parse_args()

    cwd = os.getcwd()
    infile = args.infile 
    outfile = args.outfile
    hltpath = args.hltpath
    l1seeds = args.l1seeds
    orthogonalpaths = args.orthogonalpaths
    useVtx = args.useVtx
    resonance_mask = args.resonance_mask
    no_dimuon = args.no_dimuon
    lumi_mask = args.lumi_mask
    year = args.year
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


    processor_instance = EfficiencyProcessor(hltpath=hltpath, l1seeds=l1seeds, orthogonalpaths=orthogonalpaths, useVtx=useVtx, resonance_mask=resonance_mask, no_dimuon=no_dimuon, lumi_mask=lumi_mask, year=year)
    executor = processor.DaskExecutor(client=client, retries=3)
    run = processor.Runner(
        executor=executor,
        schema=ScoutingNanoAODSchema,
        xrootdtimeout=60,
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