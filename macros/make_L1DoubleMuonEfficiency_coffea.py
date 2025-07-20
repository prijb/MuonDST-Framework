# Coffea/Awkward version of L1DoubleMuonEfficiency
# Test: Measuring HLT efficiency
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
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema, ScoutingNanoAODSchema
from coffea.nanoevents.methods import vector

import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")

parser = argparse.ArgumentParser(description='Coffea L1 efficiency script')
parser.add_argument('--infile', type=str, required=True, help='Input file path')
parser.add_argument('--hlt', action='store', type=str,  dest='hlt', default='all', help='HLT path for denominator')
parser.add_argument('--useVtx', action='store_true', dest='useVtx', default=False, help='Use the ScoutingMuonVtx instead of ScoutingMuonNoVtx')
parser.add_argument('--selectJpsi', action='store_true', dest='selectJpsi', default=False, help='Apply J/Psi mass window cut on dimuon system')

args = parser.parse_args()
fname = args.infile
hlt = args.hlt
useVtx = args.useVtx
selectJpsi = args.selectJpsi

muon_collection_key = "ScoutingMuonVtx" if useVtx else "ScoutingMuonNoVtx"

pt_bins = np.linspace(0, 50, 101)

events = NanoEventsFactory.from_root(
    {fname : "Events"},
#    entry_stop=200000,
    schemaclass = ScoutingNanoAODSchema,
    metadata = {"dataset": "ScoutingPFRun3_2024H"},
).events()

print(f"Loaded {len(events)} events from with fields:")
print(sorted(events.fields))


# HLT (DST) selection
dst_paths = events["DST"].fields
print(f"\nAvailable HLT paths: {dst_paths}")
print(f"Applying HLT selection: {hlt}")
if hlt == 'all':
    events = events[
        events["DST"]["PFScouting_DoubleEG"] | 
        events["DST"]["PFScouting_JetHT"] |
        events["DST"]["PFScouting_ZeroBias"] 
    ]
else:
    events = events[dst_paths[hlt]]
print(f"\nAfter HLT selection, {len(events)} events remain.")

# Pre-filter to have exactly 2 OS muons 
events = events[ak.num(events[muon_collection_key]) == 2]
events = events[events[muon_collection_key, "charge"][:, 0] * events[muon_collection_key, "charge"][:, 1] < 0]
print(f"\nAfter pre-filtering, {len(events)} events with exactly 2 OS {muon_collection_key} muons remain.")

# Since we use orthogonal triggers, the leading muon is the tag and the sub-leading is the probe
tag_muon_mask = events[muon_collection_key, "pt"][:, 0] > events[muon_collection_key, "pt"][:, 1]

tag_record = {}
probe_record = {}

vars = ["pt", "eta", "phi", "trk_dxy", "trk_dxyError"]
for var in vars:
    tag_record[var] = events[muon_collection_key, var][:, 0]*tag_muon_mask + events[muon_collection_key, var][:, 1]*(~tag_muon_mask)
    probe_record[var] = events[muon_collection_key, var][:, 0]*(~tag_muon_mask) + events[muon_collection_key, var][:, 1]*(tag_muon_mask)

tag_record["absdxy"] = np.abs(tag_record["trk_dxy"])
probe_record["absdxy"] = np.abs(probe_record["trk_dxy"])
tag_record["mass"] = ak.ones_like(tag_record["pt"]) * 0.105658
probe_record["mass"] = ak.ones_like(probe_record["pt"]) * 0.105658

tag = ak.zip(tag_record, with_name="PtEtaPhiMLorentzVector", behavior=vector.behavior)
probe = ak.zip(probe_record, with_name="PtEtaPhiMLorentzVector", behavior=vector.behavior)

print("\nApplying J/Psi selection")
if selectJpsi:
    # Apply J/Psi selection
    dimuon = tag + probe
    jpsi_mask = (dimuon.mass > 2.8) & (dimuon.mass < 3.4)
    tag = tag[jpsi_mask]
    probe = probe[jpsi_mask]
    events = events[jpsi_mask]

print(f"\nTag and probe definitions set")

################## Efficiency measurement ##################
denominator = probe 
numerator = probe[events["DST", "PFScouting_DoubleMuon"]]
h_denominator = Hist(hist.axis.Regular(100, 0, 50, name="pt"))
h_numerator = Hist(hist.axis.Regular(100, 0, 50, name="pt"))
h_denominator.fill(denominator.pt)
h_numerator.fill(numerator.pt)

# Test plotting the histograms and the efficiency
# Histograms
fig, ax = plt.subplots()
hep.histplot(h_denominator, ax=ax, label="All Probes", histtype="step", color="tab:blue", flow=None)
hep.histplot(h_numerator, ax=ax, label="Passing Probes", histtype="step", color="tab:orange", flow=None)
ax.set_xlabel("Probe $p_T$ (GeV)")
ax.set_ylabel("Events/2 GeV")
ax.set_yscale("log")
ax.set_xlim(0, 50)
ax.legend()
hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
plt.savefig("prueba/probe_pt_histogram_HLT.png")

# Efficiency
ratio = h_numerator.values() / h_denominator.values()
ratio_uncert = ratio_uncertainty(h_numerator.values(), h_denominator.values(), uncertainty_type="efficiency")
fig, ax = plt.subplots()
ax.errorbar(h_denominator.axes[0].centers, ratio, yerr=ratio_uncert, fmt='o', label="DST_PFScouting_DoubleMuon", color="tab:blue", capsize=5)
ax.set_xlabel("Probe $p_T$ (GeV)")
ax.set_ylabel("HLT Efficiency")
ax.set_ylim(0, 1.2)
ax.set_xlim(0, 50)
ax.legend(loc='upper left')
hep.cms.label(data=True, year=2024, llabel="Preliminary", rlabel="2024 (13.6 TeV)")
plt.savefig("prueba/efficiency_HLT_coffea.png")









