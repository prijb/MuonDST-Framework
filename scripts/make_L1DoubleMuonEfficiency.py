# Coffea/Awkward version of L1DoubleMuonEfficiency
import argparse
import os
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
import dask_awkward as dak
import hist.dask as hda

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
        pt_axis = hist.axis.Regular(100, 0, 50, name="pt", label="Probe $p_T$ (GeV)")
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
        events = events[ak.num(events[muon_collection_key]) == 2]
        events = events[events[muon_collection_key, "charge"][:, 0] * events[muon_collection_key, "charge"][:, 1] < 0]
        h_cutflow.fill(cutflow="num_events_prefilter", cutflow_count=ak.ones_like(events["DST"]["PFScouting_DoubleMuon"])*0)

        # Tag and probe muons
        tag_muon_mask = events[muon_collection_key, "pt"][:, 0] > events[muon_collection_key, "pt"][:, 1]

        tag_record = {}
        probe_record = {}

        vars = ["pt", "eta", "phi", "trk_dxy", "trk_dxyError", "charge"]
        for var in vars:
            tag_record[var] = events[muon_collection_key, var][:, 0]*tag_muon_mask + events[muon_collection_key, var][:, 1]*(~tag_muon_mask)
            probe_record[var] = events[muon_collection_key, var][:, 0]*(~tag_muon_mask) + events[muon_collection_key, var][:, 1]*(tag_muon_mask)
        tag_record["absdxy"] = np.abs(tag_record["trk_dxy"])
        probe_record["absdxy"] = np.abs(probe_record["trk_dxy"])
        tag_record["mass"] = ak.ones_like(tag_record["pt"]) * 0.105658
        probe_record["mass"] = ak.ones_like(probe_record["pt"]) * 0.105658

        tag = ak.zip(tag_record, with_name="PtEtaPhiMCandidate", behavior=candidate.behavior)
        probe = ak.zip(probe_record, with_name="PtEtaPhiMCandidate", behavior=candidate.behavior)
        dimuon = tag + probe

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

def main():
    parser = argparse.ArgumentParser(description="Coffea processor for L1 Double Muon Efficiency")
    parser.add_argument("--infile", type=str, help="Input file")
    parser.add_argument("--outfile", type=str, default="output_coffea.root", help="Output file (default: output_coffea.root)")
    parser.add_argument("--hlt", type=str, default="all", help="HLT path to select (default: all)")
    parser.add_argument("--useVtx", action='store_true', help="Use ScoutingMuonVtx collection")
    parser.add_argument("--selectJpsi", action='store_true', help="Select J/Psi candidates")
    args = parser.parse_args()

    cwd = os.getcwd()
    infile = args.infile
    outfile = args.outfile
    hlt = args.hlt
    useVtx = args.useVtx
    selectJpsi = args.selectJpsi

    print(f"Job spec")
    if hlt == 'all': print("  HLT: all")
    else: print(f"  HLT: {hlt}")
    if useVtx: print("  Using ScoutingMuonVtx collection")
    if selectJpsi: print("  Selecting only J/Psi candidates")

    # Generate fileset from input argument
    fileset = {"2024": {"files": {}}}
    infile_name = f"{infile}"
    print(f"Processing file: {infile_name}")
    fileset["2024"]["files"][infile_name] = "Events"

    client = Client()
    print(f"Dask Client: {client}")

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
    