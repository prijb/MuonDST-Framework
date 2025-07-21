# Coffea/Awkward version of L1DoubleMuonEfficiency (dask implementation attempt)
import argparse
import os
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')


import numpy as np
import uproot
import awkward as ak
import hist
from hist import Hist
from hist.intervals import ratio_uncertainty
import coffea
from coffea import processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, ScoutingNanoAODSchema
from coffea.nanoevents.methods import candidate
from coffea.dataset_tools import (
    apply_to_fileset,
    max_chunks,
    preprocess,
)

from dask.distributed import Client, LocalCluster
#import dask_awkward as dak
#import hist.dask as hda

import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")

class L1DoubleMuonEfficiencyProcessor(processor.ProcessorABC):
    def __init__(self, hlt='all', useVtx=False, selectJpsi=False):
        self.hlt = hlt
        self.useVtx = useVtx
        self.selectJpsi = selectJpsi
        self.muon_collection_key = "ScoutingMuonVtx" if useVtx else "ScoutingMuonNoVtx"
        
        # Histogramming
        self.l1_triggers_to_measure = ["DoubleMu4p5_SQ_OS_dR_Max1p2", "DoubleMu8_SQ"]
        self.hlt_triggers_to_measure = ["PFScouting_DoubleMuon"]
        trigger_axis = hist.axis.StrCategory(name="trigger", label="Trigger", categories=[], growth=True)
        pt_axis = hist.axis.Regular(100, 0, 50, name="pt", label="Muon pT (GeV)")
        mass_axis = hist.axis.Regular(30, 2.8, 3.4, name="mass", label="Dimuon Mass (GeV)")

        output_dict = {}
        
        output_dict["trigger_pt_den"]   = Hist(trigger_axis, pt_axis,    storage="weight")
        output_dict["trigger_pt_num"]   = Hist(trigger_axis, pt_axis,    storage="weight")
        output_dict["trigger_mass_den"] = Hist(trigger_axis, mass_axis,  storage="weight")
        output_dict["trigger_mass_num"] = Hist(trigger_axis, mass_axis,  storage="weight")

        # Cutflow
        output_dict["cutflow"] = processor.defaultdict_accumulator(int)

        self.output = processor.dict_accumulator(output_dict)

    def process(self, events):
        self.output["cutflow"]["num_events"] += len(events)
        muon_collection_key = self.muon_collection_key

        # HLT selection
        if self.hlt == 'all':
            events = events[
                events["DST"]["PFScouting_DoubleEG"] | 
                events["DST"]["PFScouting_JetHT"] |
                events["DST"]["PFScouting_ZeroBias"]
            ]
        else:
            events = events[events["DST"][self.hlt]]
        self.output["cutflow"]["num_events_orthogonal"] += len(events)

        # Pre-filter to have exactly 2 OS muons 
        events = events[ak.num(events[muon_collection_key]) == 2]
        events = events[events[muon_collection_key, "charge"][:, 0] * events[muon_collection_key, "charge"][:, 1] < 0]
        self.output["cutflow"]["num_events_prefilter"] += len(events)

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
        self.output["cutflow"]["num_events_selection"] += len(events)

        # Fill histograms
        for l1_trigger_to_measure in self.l1_triggers_to_measure:
            self.output["trigger_pt_den"].fill(trigger=l1_trigger_to_measure, pt=probe.pt, weight=1.0)
            self.output["trigger_pt_num"].fill(trigger=l1_trigger_to_measure, pt=probe.pt[events["L1"][l1_trigger_to_measure]], weight=1.0)
            self.output["trigger_mass_den"].fill(trigger=l1_trigger_to_measure, mass=dimuon.mass, weight=1.0)
            self.output["trigger_mass_num"].fill(trigger=l1_trigger_to_measure, mass=dimuon.mass[events["L1"][l1_trigger_to_measure]], weight=1.0)

        for hlt_trigger_to_measure in self.hlt_triggers_to_measure:
            self.output["trigger_pt_den"].fill(trigger=hlt_trigger_to_measure, pt=probe.pt, weight=1.0)
            self.output["trigger_pt_num"].fill(trigger=hlt_trigger_to_measure, pt=probe.pt[events["DST"][hlt_trigger_to_measure]], weight=1.0)
            self.output["trigger_mass_den"].fill(trigger=hlt_trigger_to_measure, mass=dimuon.mass, weight=1.0)
            self.output["trigger_mass_num"].fill(trigger=hlt_trigger_to_measure, mass=dimuon.mass[events["DST"][hlt_trigger_to_measure]], weight=1.0)

        return self.output
    
    def postprocess(self, accumulator):
        pass
    

def main():
    parser = argparse.ArgumentParser(description="Coffea processor for L1 Double Muon Efficiency")
    parser.add_argument("--hlt", type=str, default="all", help="HLT path to select (default: all)")
    parser.add_argument("--useVtx", action='store_true', help="Use ScoutingMuonVtx collection")
    parser.add_argument("--selectJpsi", action='store_true', help="Select J/Psi candidates")
    args = parser.parse_args()

    cwd = os.getcwd()
    hlt = args.hlt
    useVtx = args.useVtx
    selectJpsi = args.selectJpsi

    print(f"Job spec")
    if hlt == 'all': print("  HLT: all")
    else: print(f"  HLT: {hlt}")
    if useVtx: print("  Using ScoutingMuonVtx collection")
    if selectJpsi: print("  Selecting only J/Psi candidates")


    # Define fileset
    fileset = {
        '2024I': {
            "files": [
                f"file://{cwd}/files/2024I/scoutingnano_2024i_test.root",
            ],
        }
    }

    client = Client()
    # Print client information
    print(f"Dask Client: {client}")

    executor = processor.DaskExecutor(client=client)
    run = processor.Runner(
        executor=executor,
        schema=ScoutingNanoAODSchema,
        chunksize=100000,
    )

    processor_instance = L1DoubleMuonEfficiencyProcessor(hlt=hlt, useVtx=useVtx, selectJpsi=selectJpsi)
    output = run(fileset=fileset, treename="Events", processor_instance=processor_instance)
    print(output)

    # Plot the pT spectra and efficiencies 
    print("\nPlotting L1")
    # L1 efficiencies
    for l1_trigger_to_measure in processor_instance.l1_triggers_to_measure:
        pt_den = output["trigger_pt_den"][l1_trigger_to_measure, :]
        pt_num = output["trigger_pt_num"][l1_trigger_to_measure, :]
        mass_den = output["trigger_mass_den"][l1_trigger_to_measure, :]
        mass_num = output["trigger_mass_num"][l1_trigger_to_measure, :]

        # pT hist
        fig, ax = plt.subplots()
        hep.histplot(pt_den, ax=ax, label='All Probes', histtype='step', color="tab:blue", flow=None)
        hep.histplot(pt_num, ax=ax, label='Passing Probes', histtype='step', color="tab:orange", flow=None)
        ax.set_xlabel("Probe $p_T$ (GeV)")
        ax.set_ylabel("Events/2 GeV")
        ax.set_yscale("log")
        ax.set_xlim(0, 50)
        ax.legend()
        hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
        plt.savefig(f"{cwd}/prueba/probe_pt_histogram_L1_{l1_trigger_to_measure}_coffea.png")

        # Mass 
        fig, ax = plt.subplots()
        hep.histplot(mass_den, ax=ax, label='All Probes', histtype='step', color="tab:blue", flow=None)
        hep.histplot(mass_num, ax=ax, label='Passing Probes', histtype='step', color="tab:orange", flow=None)
        ax.set_xlabel("Probe Mass (GeV)")
        ax.set_ylabel("Events/0.02 GeV")
        #ax.set_yscale("log")
        ax.set_xlim(2.8, 3.4)
        ax.legend()
        hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
        plt.savefig(f"{cwd}/prueba/probe_mass_histogram_L1_{l1_trigger_to_measure}_coffea.png")

        # Efficiency
        ratio = pt_num.values() / pt_den.values()
        ratio_uncert = ratio_uncertainty(pt_num.values(), pt_den.values(), uncertainty_type="efficiency")
        fig, ax = plt.subplots()
        ax.errorbar(pt_den.axes[0].centers, ratio, yerr=ratio_uncert, fmt='o', label=f"L1_{l1_trigger_to_measure}", color="tab:blue", capsize=5)
        ax.set_xlabel("Probe $p_T$ (GeV)")
        ax.set_ylabel("L1 Efficiency")
        ax.set_ylim(0, 1.2)
        ax.set_xlim(0, 50)
        ax.legend(loc='upper left')
        hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
        plt.savefig(f"{cwd}/prueba/efficiency_L1_{l1_trigger_to_measure}_coffea.png")
    
    # Plot the HLT efficiencies
    print("\nPlotting HLT")
    # HLT efficiencies
    for hlt_trigger_to_measure in processor_instance.hlt_triggers_to_measure:
        pt_den = output["trigger_pt_den"][hlt_trigger_to_measure, :]
        pt_num = output["trigger_pt_num"][hlt_trigger_to_measure, :]
        mass_den = output["trigger_mass_den"][hlt_trigger_to_measure, :]
        mass_num = output["trigger_mass_num"][hlt_trigger_to_measure, :]

        # pT hist
        fig, ax = plt.subplots()
        hep.histplot(pt_den, ax=ax, label='All Probes', histtype='step', color="tab:blue", flow=None)
        hep.histplot(pt_num, ax=ax, label='Passing Probes', histtype='step', color="tab:orange", flow=None)
        ax.set_xlabel("Probe $p_T$ (GeV)")
        ax.set_ylabel("Events/2 GeV")
        ax.set_yscale("log")
        ax.set_xlim(0, 50)
        ax.legend()
        hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
        plt.savefig(f"{cwd}/prueba/probe_pt_histogram_DST_{hlt_trigger_to_measure}_coffea.png")

        # Mass 
        fig, ax = plt.subplots()
        hep.histplot(mass_den, ax=ax, label='All Probes', histtype='step', color="tab:blue", flow=None)
        hep.histplot(mass_num, ax=ax, label='Passing Probes', histtype='step', color="tab:orange", flow=None)
        ax.set_xlabel("Probe Mass (GeV)")
        ax.set_ylabel("Events/0.02 GeV")
        #ax.set_yscale("log")
        ax.set_xlim(2.8, 3.4)
        ax.legend()
        hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
        plt.savefig(f"{cwd}/prueba/probe_mass_histogram_DST_{hlt_trigger_to_measure}_coffea.png")

        # Efficiency
        ratio = pt_num.values() / pt_den.values()
        ratio_uncert = ratio_uncertainty(pt_num.values(), pt_den.values(), uncertainty_type="efficiency")
        fig, ax = plt.subplots()
        ax.errorbar(pt_den.axes[0].centers, ratio, yerr=ratio_uncert, fmt='o', label=f"DST_{hlt_trigger_to_measure}", color="tab:blue", capsize=5)
        ax.set_xlabel("Probe $p_T$ (GeV)")
        ax.set_ylabel("HLT Efficiency")
        ax.set_ylim(0, 1.2)
        ax.set_xlim(0, 50)
        ax.legend(loc='upper left')
        hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
        plt.savefig(f"{cwd}/prueba/efficiency_DST_{hlt_trigger_to_measure}_coffea.png")

if __name__ == "__main__":
    main()