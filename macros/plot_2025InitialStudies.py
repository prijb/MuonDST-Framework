import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import hist
import glob
import pickle
from tqdm import tqdm

colors = ['k', '#3f90da', '#ffa90e', '#bd1f01']

with open("histos_2025_TrgNoVtx_Vtx.pkl", "rb") as f:
    obj = pickle.load(f)

## 2024, TrigNoVtx, Vtx
with open("histos_2024_TrgNoVtx_Vtx.pkl", "rb") as f:
    h_mass_2024_TrgNoVtx_Vtx = pickle.load(f)
    h_pt_2024_TrgNoVtx_Vtx = pickle.load(f)
    h_eta_2024_TrgNoVtx_Vtx = pickle.load(f)
    h_phi_2024_TrgNoVtx_Vtx = pickle.load(f)
## 2024, TrigNoVtx, NoVtx
with open("histos_2024_TrgNoVtx_NoVtx.pkl", "rb") as f:
    h_mass_2024_TrgNoVtx_NoVtx = pickle.load(f)
    h_pt_2024_TrgNoVtx_NoVtx = pickle.load(f)
    h_eta_2024_TrgNoVtx_NoVtx = pickle.load(f)
    h_phi_2024_TrgNoVtx_NoVtx = pickle.load(f)
## 2025, TrigNoVtx, Vtx
with open("histos_2025_TrgNoVtx_Vtx.pkl", "rb") as f:
    h_mass_2025_TrgNoVtx_Vtx = pickle.load(f)
    h_pt_2025_TrgNoVtx_Vtx = pickle.load(f)
    h_eta_2025_TrgNoVtx_Vtx = pickle.load(f)
    h_phi_2025_TrgNoVtx_Vtx = pickle.load(f)
## 2025, TrigVtx, Vtx
with open("histos_2025_TrgVtx_Vtx.pkl", "rb") as f:
    h_mass_2025_TrgVtx_Vtx = pickle.load(f)
    h_pt_2025_TrgVtx_Vtx = pickle.load(f)
    h_eta_2025_TrgVtx_Vtx = pickle.load(f)
    h_phi_2025_TrgVtx_Vtx = pickle.load(f)
## 2025, TrigOR, Vtx
with open("histos_2025_TrgOR_Vtx.pkl", "rb") as f:
    h_mass_2025_TrgOR_Vtx = pickle.load(f)
    h_pt_2025_TrgOR_Vtx = pickle.load(f)
    h_eta_2025_TrgOR_Vtx = pickle.load(f)
    h_phi_2025_TrgOR_Vtx = pickle.load(f)
## 2025, TrigNoVtx, NoVtx
with open("histos_2025_TrgNoVtx_NoVtx.pkl", "rb") as f:
    h_mass_2025_TrgNoVtx_NoVtx = pickle.load(f)
    h_pt_2025_TrgNoVtx_NoVtx = pickle.load(f)
    h_eta_2025_TrgNoVtx_NoVtx = pickle.load(f)
    h_phi_2025_TrgNoVtx_NoVtx = pickle.load(f)
## 2025, TrigOR, NoVtx
with open("histos_2025_TrgOR_NoVtx.pkl", "rb") as f:
    h_mass_2025_TrgOR_NoVtx = pickle.load(f)
    h_pt_2025_TrgOR_NoVtx = pickle.load(f)
    h_eta_2025_TrgOR_NoVtx = pickle.load(f)
    h_phi_2025_TrgOR_NoVtx = pickle.load(f)


plt.style.use(hep.style.CMS)
#fig, ax = plt.subplots(figsize=(10,8))
fig, (ax, ax_ratio) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1], 'hspace': 0.05}, sharex=True, figsize=(11, 10))
hep.cms.label("Preliminary", data=True, year='', lumi=1, com='13.6', ax=ax)
h_mass_2024_TrgNoVtx_Vtx *= (1./1.362593)
h_mass_2025_TrgNoVtx_Vtx *= (1./1.58327)
h_mass_2025_TrgVtx_Vtx *= (1./1.58327)
h_mass_2025_TrgOR_Vtx *= (1./1.58327)
h_mass_2024_TrgNoVtx_Vtx.plot(ax=ax, label="2024I: DST_PFScouting_DoubleMuon (NoVtx)", color=colors[0])
h_mass_2025_TrgNoVtx_Vtx.plot(ax=ax, label="2025C: DST_PFScouting_DoubleMuonNoVtx", color=colors[1])
h_mass_2025_TrgVtx_Vtx.plot(ax=ax, label="2025C: DST_PFScouting_DoubleMuonVtx", color=colors[2])
h_mass_2025_TrgOR_Vtx.plot(ax=ax, label="2025C: DoubleMuonNoVtx OR DoubleMuonVtx", color=colors[3])
ax.set_xlim(0.1, 110)
ax.set_ylim(1, 1e11)
ax.set_ylabel("Number of muon pairs")
ax.set_xlabel("")
ax.set_xscale("log")
ax.set_yscale("log")
ax.text(0.04, 0.75, 'Vtx-constrained scouting muon reconstruction', ha='left', va='top', transform=ax.transAxes, fontsize=15, fontweight='bold')
ax.legend(loc='upper left', fontsize = 16, frameon = True, ncol=1)
h_ratio_mass_2025_TrgNoVtx_Vtx = h_mass_2025_TrgNoVtx_Vtx / h_mass_2024_TrgNoVtx_Vtx
h_ratio_mass_2025_TrgVtx_Vtx = h_mass_2025_TrgVtx_Vtx / h_mass_2024_TrgNoVtx_Vtx
h_ratio_mass_2025_TrgOR_Vtx = h_mass_2025_TrgOR_Vtx / h_mass_2024_TrgNoVtx_Vtx
h_ratio_mass_2025_TrgNoVtx_Vtx.plot(ax=ax_ratio, color=colors[1])
h_ratio_mass_2025_TrgVtx_Vtx.plot(ax=ax_ratio, color=colors[2])
h_ratio_mass_2025_TrgOR_Vtx.plot(ax=ax_ratio, color=colors[3])
ax_ratio.set_ylabel("Ratio")
ax_ratio.set_xlabel("Dimuon invariant mass [GeV]")
fig.savefig("hist_invariant-mass_Vtx_log.png", dpi=300)

plt.style.use(hep.style.CMS)
fig, (ax, ax_ratio) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1], 'hspace': 0.05}, sharex=True, figsize=(11, 10))
hep.cms.label("Preliminary", data=True, year='', lumi=1, com='13.6', ax=ax)
h_mass_2024_TrgNoVtx_NoVtx *= (1./1.362593)
h_mass_2025_TrgNoVtx_NoVtx *= (1./1.58327)
h_mass_2025_TrgOR_NoVtx *= (1./1.58327)
h_mass_2024_TrgNoVtx_NoVtx.plot(ax=ax, label="2024I: DST_PFScouting_DoubleMuon (NoVtx)", color=colors[0])
h_mass_2025_TrgNoVtx_NoVtx.plot(ax=ax, label="2025C: DST_PFScouting_DoubleMuonNoVtx", color=colors[1])
h_mass_2025_TrgOR_NoVtx.plot(ax=ax, label="2025C: DoubleMuonNoVtx OR DoubleMuonVtx", color=colors[2])
ax.set_xlim(0.1, 110)
ax.set_ylim(1, 1e10)
ax.set_xlabel("")
ax.set_ylabel("Number of muon pairs")
ax.set_xscale("log")
ax.set_yscale("log")
ax.text(0.04, 0.79, 'Vtx-unconstrained scouting muon reconstruction', ha='left', va='top', transform=ax.transAxes, fontsize=15, fontweight='bold')
ax.legend(loc='upper left', fontsize = 16, frameon = True, ncol=1)
h_ratio_mass_2025_TrgNoVtx_NoVtx = h_mass_2025_TrgNoVtx_NoVtx / h_mass_2024_TrgNoVtx_NoVtx
h_ratio_mass_2025_TrgOR_NoVtx = h_mass_2025_TrgOR_NoVtx / h_mass_2024_TrgNoVtx_NoVtx
h_ratio_mass_2025_TrgNoVtx_NoVtx.plot(ax=ax_ratio, color=colors[1])
h_ratio_mass_2025_TrgOR_NoVtx.plot(ax=ax_ratio, color=colors[2])
ax_ratio.set_ylabel("Ratio")
ax_ratio.set_xlabel("Dimuon invariant mass [GeV]")
ax_ratio.set_ylim(0, 20)
fig.savefig("hist_invariant-mass_NoVtx_log.png", dpi=300)

plt.style.use(hep.style.CMS)
fig, (ax, ax_ratio) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1], 'hspace': 0.05}, sharex=True, figsize=(11, 10))
hep.cms.label("Preliminary", data=True, year='', lumi=1, com='13.6', ax=ax)
h_pt_2024_TrgNoVtx_Vtx *= (1./1.362593)
h_pt_2025_TrgNoVtx_Vtx *= (1./1.58327)
h_pt_2025_TrgVtx_Vtx *= (1./1.58327)
h_pt_2025_TrgOR_Vtx *= (1./1.58327)
h_pt_2024_TrgNoVtx_Vtx.plot(ax=ax, label="2024I: DST_PFScouting_DoubleMuon (NoVtx)", color=colors[0])
h_pt_2025_TrgNoVtx_Vtx.plot(ax=ax, label="2025C: DST_PFScouting_DoubleMuonNoVtx", color=colors[1])
h_pt_2025_TrgVtx_Vtx.plot(ax=ax, label="2025C: DST_PFScouting_DoubleMuonVtx", color=colors[2])
h_pt_2025_TrgOR_Vtx.plot(ax=ax, label="2025C: DoubleMuonNoVtx OR DoubleMuonVtx", color=colors[3])
ax.set_xlim(0, 100)
ax.set_ylim(1, 1e12)
ax.set_xlabel("")
ax.set_ylabel("Number of muons")
ax.set_yscale("log")
ax.text(0.04, 0.75, 'Vtx-constrained scouting muon reconstruction', ha='left', va='top', transform=ax.transAxes, fontsize=15, fontweight='bold')
ax.legend(loc='upper left', fontsize = 16, frameon = True, ncol=1)
h_ratio_pt_2025_TrgNoVtx_Vtx = h_pt_2025_TrgNoVtx_Vtx / h_pt_2024_TrgNoVtx_Vtx
h_ratio_pt_2025_TrgVtx_Vtx = h_pt_2025_TrgVtx_Vtx / h_pt_2024_TrgNoVtx_Vtx
h_ratio_pt_2025_TrgOR_Vtx = h_pt_2025_TrgOR_Vtx / h_pt_2024_TrgNoVtx_Vtx
h_ratio_pt_2025_TrgNoVtx_Vtx.plot(ax=ax_ratio, color=colors[1])
h_ratio_pt_2025_TrgVtx_Vtx.plot(ax=ax_ratio, color=colors[2])
h_ratio_pt_2025_TrgOR_Vtx.plot(ax=ax_ratio, color=colors[3])
ax_ratio.set_ylabel("Ratio")
ax_ratio.set_xlabel(r"Scouting muon $p_{T}$ [GeV]")
fig.savefig("hist_pt_Vtx_log.png", dpi=300)

plt.style.use(hep.style.CMS)
fig, (ax, ax_ratio) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1], 'hspace': 0.05}, sharex=True, figsize=(11, 10))
hep.cms.label("Preliminary", data=True, year='', lumi=1, com='13.6', ax=ax)
h_pt_2024_TrgNoVtx_NoVtx *= (1./1.362593)
h_pt_2025_TrgNoVtx_NoVtx *= (1./1.58327)
h_pt_2025_TrgOR_NoVtx *= (1./1.58327)
h_pt_2024_TrgNoVtx_NoVtx.plot(ax=ax, label="2024I: DST_PFScouting_DoubleMuon (NoVtx)", color=colors[0])
h_pt_2025_TrgNoVtx_NoVtx.plot(ax=ax, label="2025C: DST_PFScouting_DoubleMuonNoVtx", color=colors[1])
h_pt_2025_TrgOR_NoVtx.plot(ax=ax, label="2025C: DoubleMuonNoVtx OR DoubleMuonVtx", color=colors[2])
ax.set_xlim(0, 100)
ax.set_ylim(1, 1e11)
ax.set_xlabel("")
ax.set_ylabel("Number of muons")
ax.set_yscale("log")
ax.text(0.04, 0.79, 'Vtx-unconstrained scouting muon reconstruction', ha='left', va='top', transform=ax.transAxes, fontsize=15, fontweight='bold')
ax.legend(loc='upper left', fontsize = 16, frameon = True, ncol=1)
h_ratio_pt_2025_TrgNoVtx_NoVtx = h_pt_2025_TrgNoVtx_NoVtx / h_pt_2024_TrgNoVtx_NoVtx
h_ratio_pt_2025_TrgOR_NoVtx = h_pt_2025_TrgOR_NoVtx / h_pt_2024_TrgNoVtx_NoVtx
h_ratio_pt_2025_TrgNoVtx_NoVtx.plot(ax=ax_ratio, color=colors[1])
h_ratio_pt_2025_TrgOR_NoVtx.plot(ax=ax_ratio, color=colors[2])
ax_ratio.set_ylabel("Ratio")
ax_ratio.set_xlabel(r"Scouting muon $p_{T}$ [GeV]")
fig.savefig("hist_pt_NoVtx_log.png", dpi=300)

"""
plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
h_eta.plot(ax=ax)
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(1, 1e8)
ax.set_xlabel("Dimuon invariant mass [GeV]")
ax.set_ylabel("Number of events")
ax.set_yscale("log")
fig.savefig("hist_eta_log.png", dpi=300)

plt.style.use(mplhep.style.CMS)
fig, ax = plt.subplots(figsize=(10,8))
h_phi.plot(ax=ax)
ax.set_xlim(-4, 4)
ax.set_ylim(1, 1e8)
ax.set_xlabel("Dimuon invariant mass [GeV]")
ax.set_ylabel("Number of events")
ax.set_yscale("log")
fig.savefig("hist_phi_log.png", dpi=300)
"""
