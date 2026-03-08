# Plot the trigger efficency for a list of datasets
import uproot
import hist
from hist.intervals import ratio_uncertainty
import argparse
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import mplhep as hep
import sys
hep.style.use("CMS")

errps = {'hatch':'////', 'facecolor':'none', 'lw': 0, 'edgecolor': 'k', 'alpha': 0.5}

def plot_1d_hist(ax, h, label, color, density=False, histtype="step"):
    if density:
        h *= (1/(h.values().sum()))
    hep.histplot(h, ax=ax, label=label, color=color, density=False, flow=None, histtype=histtype)
    return h, ax

# Helper functions
def plot_2d_ratio(ax, h_num, h_den, logz=False):
    v_num, x_num, y_num = h_num.to_numpy(flow=False)
    v_den, x_den, y_den = h_den.to_numpy(flow=False)
    ratio = np.divide(v_num, v_den, out=np.full_like(v_num, np.nan, dtype=float), where=v_den!=0)
    ratio = np.ma.masked_invalid(ratio)
    hep.hist2dplot(
        ratio,
        xbins=x_den,
        ybins=y_den,
        ax=ax,
        cbarextend=True,
        norm=LogNorm(vmin=0.1, vmax=2) if logz else Normalize(vmin=0.0, vmax=1.0),
        cmap="viridis"
    )
    return ax


parser = argparse.ArgumentParser("Plot trigger efficiencies")
parser.add_argument("--files", type=str, nargs="+", help="Files to open")
parser.add_argument("--labels", type=str, nargs="+", help="Labels for each of the files")
parser.add_argument("--addtxt", type=str, help="Additional text")
parser.add_argument("--rlabel", type=str, default="1 \fb (13.6 TeV)$", help="Directory to store plots in")
parser.add_argument("--outdir", type=str, default="plots/performance", help="Directory to store plots in")
# Script specific
parser.add_argument("--hltpath", type=str, help="HLT Path to plot")
parser.add_argument("--l1seeds", type=str, nargs="+", help="L1 seeds to plot")
parser.add_argument("--ptcut", type=float, help="pT > X cut for eta and dR 1D histograms")
parser.add_argument("--etacut", type=float, help="|eta| < X cut for pT and dR 1D histograms")
parser.add_argument("--drcut", type=float, help="dr > X cut for eta and dR 1D histograms")
args = parser.parse_args()
colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]

cwd = os.getcwd()
files = args.files
labels = args.labels
outdir = args.outdir
addtxt = args.addtxt
rlabel = args.rlabel
hltpath = args.hltpath
l1seeds = args.l1seeds
ptcut = args.ptcut
etacut = args.etacut
drcut = args.drcut
os.makedirs(outdir, exist_ok=True)
os.makedirs(f"{outdir}/2d", exist_ok=True)
if addtxt is not None:
    addtxt = addtxt.replace("\\n", "\n")

# Exceptions
if len(files) != len(labels):
    raise RuntimeError(f"File and label sizes {len(files)} and {len(labels)} uneven")

f_list = []
for file in files:
    f = uproot.open(file)
    f_list.append(f)
colors = colors[:len(files)]

# Load all the files 
# Den
trigger_pt_eta_leading_den_list = []
trigger_pt_dr_leading_den_list = []
trigger_eta_dr_leading_den_list = []
trigger_pt_eta_subleading_den_list = []
trigger_pt_dr_subleading_den_list = []
trigger_eta_dr_subleading_den_list = []
# Num
trigger_pt_eta_leading_num_list = []
trigger_pt_dr_leading_num_list = []
trigger_eta_dr_leading_num_list = []
trigger_pt_eta_subleading_num_list = []
trigger_pt_dr_subleading_num_list = []
trigger_eta_dr_subleading_num_list = []

for file in files:
    f = uproot.open(file)
    # Den
    trigger_pt_eta_leading_den_list.append(f["trigger_pt_eta_leading_den"].to_hist())
    trigger_pt_dr_leading_den_list.append(f["trigger_pt_dr_leading_den"].to_hist())
    trigger_eta_dr_leading_den_list.append(f["trigger_eta_dr_leading_den"].to_hist())
    trigger_pt_eta_subleading_den_list.append(f["trigger_pt_eta_subleading_den"].to_hist())
    trigger_pt_dr_subleading_den_list.append(f["trigger_pt_dr_subleading_den"].to_hist())
    trigger_eta_dr_subleading_den_list.append(f["trigger_eta_dr_subleading_den"].to_hist())
    # Num
    trigger_pt_eta_leading_num_list.append(f["trigger_pt_eta_leading_num"].to_hist())
    trigger_pt_dr_leading_num_list.append(f["trigger_pt_dr_leading_num"].to_hist())
    trigger_eta_dr_leading_num_list.append(f["trigger_eta_dr_leading_num"].to_hist())
    trigger_pt_eta_subleading_num_list.append(f["trigger_pt_eta_subleading_num"].to_hist())
    trigger_pt_dr_subleading_num_list.append(f["trigger_pt_dr_subleading_num"].to_hist())
    trigger_eta_dr_subleading_num_list.append(f["trigger_eta_dr_subleading_num"].to_hist())

print(f"\nFiles loaded successfully!")

##################### Plotting HLT path efficiency ####################
print(f"\nPlotting efficienicies for HLT path: {hltpath}")
hltpath_name = hltpath.replace("DST_", "")

# pT-eta 2D
for i in range(len(files)):
    trigger_pt_eta_leading_num = trigger_pt_eta_leading_num_list[i][hist.loc(hltpath_name), :, :]
    trigger_pt_dr_leading_num = trigger_pt_dr_leading_num_list[i][hist.loc(hltpath_name), :, :]
    trigger_eta_dr_leading_num = trigger_eta_dr_leading_num_list[i][hist.loc(hltpath_name), :, :]
    trigger_pt_eta_subleading_num = trigger_pt_eta_subleading_num_list[i][hist.loc(hltpath_name), :, :]
    trigger_pt_dr_subleading_num = trigger_pt_dr_subleading_num_list[i][hist.loc(hltpath_name), :, :]
    trigger_eta_dr_subleading_num = trigger_eta_dr_subleading_num_list[i][hist.loc(hltpath_name), :, :]

    trigger_pt_eta_leading_den = trigger_pt_eta_leading_den_list[i][hist.loc(hltpath_name), :, :]
    trigger_pt_dr_leading_den = trigger_pt_dr_leading_den_list[i][hist.loc(hltpath_name), :, :]
    trigger_eta_dr_leading_den = trigger_eta_dr_leading_den_list[i][hist.loc(hltpath_name), :, :]
    trigger_pt_eta_subleading_den = trigger_pt_eta_subleading_den_list[i][hist.loc(hltpath_name), :, :]
    trigger_pt_dr_subleading_den = trigger_pt_dr_subleading_den_list[i][hist.loc(hltpath_name), :, :]
    trigger_eta_dr_subleading_den = trigger_eta_dr_subleading_den_list[i][hist.loc(hltpath_name), :, :]

    ## Leading
    # pT-eta
    fig, ax = plt.subplots()
    ax = plot_2d_ratio(ax, trigger_pt_eta_leading_num, trigger_pt_eta_leading_den, logz=False)
    ax.set_xlabel(r"Leading Muon $p_{T}$ [GeV]")
    ax.set_ylabel(r"Leading Muon $\eta$")
    #ax.set_xlim(2, 30)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=f"{labels[i]}", ax=ax)
    plt.savefig(f"{outdir}/2d/{hltpath}_leading_pt_eta_{labels[i]}.png")
    plt.close()
    
    fig, ax = plt.subplots()
    ax = plot_2d_ratio(ax, trigger_pt_dr_leading_num, trigger_pt_dr_leading_den, logz=False)
    ax.set_xlabel(r"Leading Muon $p_{T}$ [GeV]")
    ax.set_ylabel(r"Dimuon $\Delta R$")
    ax.set_ylim(0, 1.0)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=f"{labels[i]}", ax=ax)
    plt.savefig(f"{outdir}/2d/{hltpath}_leading_pt_dr_{labels[i]}.png")
    plt.close()
        
    fig, ax = plt.subplots()
    ax = plot_2d_ratio(ax, trigger_eta_dr_leading_num, trigger_eta_dr_leading_den, logz=False)
    ax.set_xlabel(r"Leading Muon $\eta$ [GeV]")
    ax.set_ylabel(r"Dimuon $\Delta R$")
    ax.set_ylim(0, 1.0)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=f"{labels[i]}", ax=ax)
    plt.savefig(f"{outdir}/2d/{hltpath}_leading_eta_dr_{labels[i]}.png")
    plt.close()
    
    ## Subleading
    fig, ax = plt.subplots()
    ax = plot_2d_ratio(ax, trigger_pt_eta_subleading_num, trigger_pt_eta_subleading_den, logz=False)
    ax.set_xlabel(r"Subleading Muon $p_{T}$ [GeV]")
    ax.set_ylabel(r"Subleading Muon $\eta$")
    #ax.set_xlim(2, 30)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=f"{labels[i]}", ax=ax)
    plt.savefig(f"{outdir}/2d/{hltpath}_subleading_pt_eta_{labels[i]}.png")
    plt.close()
    
    fig, ax = plt.subplots()
    ax = plot_2d_ratio(ax, trigger_pt_dr_subleading_num, trigger_pt_dr_subleading_den, logz=False)
    ax.set_xlabel(r"Subleading Muon $p_{T}$ [GeV]")
    ax.set_ylabel(r"Dimuon $\Delta R$")
    ax.set_ylim(0, 1.0)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=f"{labels[i]}", ax=ax)
    plt.savefig(f"{outdir}/2d/{hltpath}_subleading_pt_dr_{labels[i]}.png")
    plt.close()
    
    fig, ax = plt.subplots()
    ax = plot_2d_ratio(ax, trigger_eta_dr_subleading_num, trigger_eta_dr_subleading_den, logz=False)
    ax.set_xlabel(r"Subleading Muon $\eta$ [GeV]")
    ax.set_ylabel(r"Dimuon $\Delta R$")
    ax.set_ylim(0, 1.0)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=f"{labels[i]}", ax=ax)
    plt.savefig(f"{outdir}/2d/{hltpath}_subleading_eta_dr_{labels[i]}.png")
    plt.close()
    
# Plot 1D versions 
# Leading pT
print("\nPlotting 1D histograms")
fig, ax = plt.subplots()
for i in range(len(files)):
    trigger_pt_leading_num = trigger_pt_eta_leading_num_list[i][hist.loc(hltpath_name), :, ::sum]
    trigger_pt_leading_den = trigger_pt_eta_leading_den_list[i][hist.loc(hltpath_name), :, ::sum]

    num = trigger_pt_leading_num
    den = trigger_pt_leading_den

    xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
    ratio = num.values()/den.values()
    ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

    ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
ax.axhline(1, color='black', linestyle='--')
ax.set_xlabel(r"Leading Muon $p_{T}$ [GeV]")
ax.set_ylabel("Efficiency")
ax.set_ylim(0, 1.2)
#ax.set_xlim(0, 30)
ax.legend(loc="upper right", fontsize=16, ncol=2)
if addtxt is not None: ax.text(0.05, 0.90, addtxt, transform=ax.transAxes, fontsize=16)
hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
plt.savefig(f"{outdir}/{hltpath}_leading_pt.png")
plt.close()

# Subeading pT
fig, ax = plt.subplots()
for i in range(len(files)):
    trigger_pt_subleading_num = trigger_pt_eta_subleading_num_list[i][hist.loc(hltpath_name), :, ::sum]
    trigger_pt_subleading_den = trigger_pt_eta_subleading_den_list[i][hist.loc(hltpath_name), :, ::sum]

    num = trigger_pt_subleading_num
    den = trigger_pt_subleading_den

    xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
    ratio = num.values()/den.values()
    ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

    ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
ax.axhline(1, color='black', linestyle='--')
ax.set_xlabel(r"Subleading Muon $p_{T}$ [GeV]")
ax.set_ylabel("Efficiency")
ax.set_ylim(0, 1.2)
#ax.set_xlim(0, 30)
ax.legend(loc="upper right", fontsize=16, ncol=2)
if addtxt is not None: ax.text(0.05, 0.90, addtxt, transform=ax.transAxes, fontsize=16)
hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
plt.savefig(f"{outdir}/{hltpath}_subleading_pt.png")
plt.close()

# Leading eta
fig, ax = plt.subplots()
for i in range(len(files)):
    trigger_eta_leading_num = trigger_pt_eta_leading_num_list[i][hist.loc(hltpath_name), ::sum, :]
    trigger_eta_leading_den = trigger_pt_eta_leading_den_list[i][hist.loc(hltpath_name), ::sum, :]

    num = trigger_eta_leading_num
    den = trigger_eta_leading_den

    xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
    ratio = num.values()/den.values()
    ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

    ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
ax.axhline(1, color='black', linestyle='--')
ax.set_xlabel(r"Leading Muon $\eta$ [GeV]")
ax.set_ylabel("Efficiency")
ax.set_ylim(0, 1.2)
#ax.set_xlim(0, 30)
ax.legend(loc="upper right", fontsize=16, ncol=2)
if addtxt is not None: ax.text(0.05, 0.90, addtxt, transform=ax.transAxes, fontsize=16)
hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
plt.savefig(f"{outdir}/{hltpath}_leading_eta.png")
plt.close()

# Subeading eta
fig, ax = plt.subplots()
for i in range(len(files)):
    trigger_eta_subleading_num = trigger_pt_eta_subleading_num_list[i][hist.loc(hltpath_name), ::sum, :]
    trigger_eta_subleading_den = trigger_pt_eta_subleading_den_list[i][hist.loc(hltpath_name), ::sum, :]

    num = trigger_eta_subleading_num
    den = trigger_eta_subleading_den

    xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
    ratio = num.values()/den.values()
    ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

    ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
ax.axhline(1, color='black', linestyle='--')
ax.set_xlabel(r"Subleading Muon $\eta$ [GeV]")
ax.set_ylabel("Efficiency")
ax.set_ylim(0, 1.2)
#ax.set_xlim(0, 30)
ax.legend(loc="upper right", fontsize=16, ncol=2)
if addtxt is not None: ax.text(0.05, 0.90, addtxt, transform=ax.transAxes, fontsize=16)
hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
plt.savefig(f"{outdir}/{hltpath}_subleading_eta.png")
plt.close()

# dR
fig, ax = plt.subplots()
for i in range(len(files)):
    trigger_dr_subleading_num = trigger_pt_dr_subleading_num_list[i][hist.loc(hltpath_name), ::sum, :]
    trigger_dr_subleading_den = trigger_pt_dr_subleading_den_list[i][hist.loc(hltpath_name), ::sum, :]

    num = trigger_dr_subleading_num
    den = trigger_dr_subleading_den

    xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
    ratio = num.values()/den.values()
    ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

    ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
ax.axhline(1, color='black', linestyle='--')
ax.set_xlabel(r"Dimuon $\Delta R$ [GeV]")
ax.set_ylabel("Efficiency")
ax.set_ylim(0, 1.2)
ax.set_xlim(0, 1.2)
ax.legend(loc="upper right", fontsize=16, ncol=2)
if addtxt is not None: ax.text(0.05, 0.90, addtxt, transform=ax.transAxes, fontsize=16)
hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
plt.savefig(f"{outdir}/{hltpath}_dr.png")
plt.close()

## Versions with cuts 
# Eta cut
print("\nPlotting 1D histograms with cuts")
if etacut is not None:
    print(f"Plotting pT and dR histograms with |eta| < {etacut}")  

    # Leading pT (eta cut)
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_pt_leading_etacut_num = trigger_pt_eta_leading_num_list[i][hist.loc(hltpath_name), :, hist.loc(-1.0*etacut):hist.loc(etacut):sum]
        trigger_pt_leading_etacut_den = trigger_pt_eta_leading_den_list[i][hist.loc(hltpath_name), :, hist.loc(-1.0*etacut):hist.loc(etacut):sum]

        num = trigger_pt_leading_etacut_num
        den = trigger_pt_leading_etacut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Leading Muon $p_{T}$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+f"\n $|\eta|<${etacut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_leading_pt_etacut.png")
    plt.close()

    # Subleading pT (eta cut)
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_pt_subleading_etacut_num = trigger_pt_eta_subleading_num_list[i][hist.loc(hltpath_name), :, hist.loc(-1.0*etacut):hist.loc(etacut):sum]
        trigger_pt_subleading_etacut_den = trigger_pt_eta_subleading_den_list[i][hist.loc(hltpath_name), :, hist.loc(-1.0*etacut):hist.loc(etacut):sum]

        num = trigger_pt_subleading_etacut_num
        den = trigger_pt_subleading_etacut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Subleading Muon $p_{T}$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+f"\n $|\eta|<${etacut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_subleading_pt_etacut.png")
    plt.close()

    # dR
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_dr_subleading_etacut_num = trigger_eta_dr_subleading_num_list[i][hist.loc(hltpath_name), hist.loc(-1.0*etacut):hist.loc(etacut):sum, :]
        trigger_dr_subleading_etacut_den = trigger_eta_dr_subleading_den_list[i][hist.loc(hltpath_name), hist.loc(-1.0*etacut):hist.loc(etacut):sum, :]

        num = trigger_dr_subleading_etacut_num
        den = trigger_dr_subleading_etacut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Dimuon $\Delta R$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    ax.set_xlim(0, 1.2)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+"\n"+r"$p_{T}$>10"+f"\n $|\eta|<${etacut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_dr_etacut.png")
    plt.close()

# pT cut (No point plotting dR due to strong correlation between pT and dR)
if ptcut is not None:
    print(f"Plotting eta histograms with pT > {ptcut}")  

    # Leading eta
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_eta_leading_ptcut_num = trigger_pt_eta_leading_num_list[i][hist.loc(hltpath_name), hist.loc(ptcut)::sum, :]
        trigger_eta_leading_ptcut_den = trigger_pt_eta_leading_den_list[i][hist.loc(hltpath_name), hist.loc(ptcut)::sum, :]

        num = trigger_eta_leading_ptcut_num
        den = trigger_eta_leading_ptcut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Leading Muon $\eta$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+"\n"+r"$p_{T}>$"+f"{ptcut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_leading_eta_ptcut.png")
    plt.close()

    # Subleading eta
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_eta_subleading_ptcut_num = trigger_pt_eta_subleading_num_list[i][hist.loc(hltpath_name), hist.loc(ptcut)::sum, :]
        trigger_eta_subleading_ptcut_den = trigger_pt_eta_subleading_den_list[i][hist.loc(hltpath_name), hist.loc(ptcut)::sum, :]

        num = trigger_eta_subleading_ptcut_num
        den = trigger_eta_subleading_ptcut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Subleading Muon $\eta$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+"\n"+r"$p_{T}>$"+f"{ptcut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_subleading_eta_ptcut.png")
    plt.close()

# dR cut 
if drcut is not None:
    print(f"Plotting pT and eta histograms with dR > {drcut}") 

    # Leading pT (dR cut)
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_pt_leading_drcut_num = trigger_pt_dr_leading_num_list[i][hist.loc(hltpath_name), :, hist.loc(drcut)::sum]
        trigger_pt_leading_drcut_den = trigger_pt_dr_leading_den_list[i][hist.loc(hltpath_name), :, hist.loc(drcut)::sum]

        num = trigger_pt_leading_drcut_num
        den = trigger_pt_leading_drcut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Leading Muon $p_{T}$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+f"\n dR>{drcut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_leading_pt_drcut.png")
    plt.close()

    # Subleading pT (dR cut)
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_pt_subleading_drcut_num = trigger_pt_dr_subleading_num_list[i][hist.loc(hltpath_name), :, hist.loc(drcut)::sum]
        trigger_pt_subleading_drcut_den = trigger_pt_dr_subleading_den_list[i][hist.loc(hltpath_name), :, hist.loc(drcut)::sum]

        num = trigger_pt_subleading_drcut_num
        den = trigger_pt_subleading_drcut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Subleading Muon $p_{T}$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+f"\n dR>{drcut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_subleading_pt_drcut.png") 
    plt.close()

    # Leading eta (dR cut)
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_eta_leading_drcut_num = trigger_eta_dr_leading_num_list[i][hist.loc(hltpath_name), : ,hist.loc(drcut)::sum]
        trigger_eta_leading_drcut_den = trigger_eta_dr_leading_den_list[i][hist.loc(hltpath_name), : ,hist.loc(drcut)::sum]

        num = trigger_eta_leading_drcut_num
        den = trigger_eta_leading_drcut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Leading Muon $\eta$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+"\n"+r"$p_{T}$>10"+f"\n dR>{drcut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_leading_eta_drcut.png")
    plt.close()

    # Subleading eta (dR cut)
    fig, ax = plt.subplots()
    for i in range(len(files)):
        trigger_eta_subleading_drcut_num = trigger_eta_dr_subleading_num_list[i][hist.loc(hltpath_name), : ,hist.loc(drcut)::sum]
        trigger_eta_subleading_drcut_den = trigger_eta_dr_subleading_den_list[i][hist.loc(hltpath_name), : ,hist.loc(drcut)::sum]

        num = trigger_eta_subleading_drcut_num
        den = trigger_eta_subleading_drcut_den

        xerr = 0.5 * (den.axes[0].edges[1:] - den.axes[0].edges[:-1])
        ratio = num.values()/den.values()
        ratio_err = ratio_uncertainty(num.values(), den.values(), uncertainty_type="efficiency")

        ax.errorbar(den.axes[0].centers, ratio, yerr=ratio_err, xerr=xerr, fmt="o", label=f"{labels[i]}", color=colors[i])
    ax.axhline(1, color='black', linestyle='--')
    ax.set_xlabel(r"Subleading Muon $\eta$ [GeV]")
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    #ax.set_xlim(0, 30)
    ax.legend(loc="upper right", fontsize=16, ncol=2)
    if addtxt is not None: ax.text(0.05, 0.85, addtxt+"\n"+r"$p_{T}$>10"+f"\n dR>{drcut}", transform=ax.transAxes, fontsize=16)
    hep.cms.label(data=True, llabel="Preliminary", rlabel=rlabel, ax=ax)
    plt.savefig(f"{outdir}/{hltpath}_subleading_eta_drcut.png")
    plt.close()

##################### Plotting L1 path efficiencies ####################