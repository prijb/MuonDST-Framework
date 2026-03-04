# Plot a list of datasets along with a ratio wrt to the first dataset in the list
import uproot
import hist
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

def plot_ratio(ax, h_num, h_den, color, alpha=0.8):
    h_num_values = h_num.values()
    h_num_variances = h_num.variances()
    h_den_values = h_den.values()
    h_den_variances = h_den.variances()
    h_num_rel_err = np.sqrt(h_num_variances) / h_num_values
    h_den_rel_err = np.sqrt(h_den_variances) / h_den_values    
    ratio = h_num_values/h_den_values
    ratio_err = ratio * np.sqrt(h_num_rel_err**2 + h_den_rel_err**2)
    ax.errorbar(h_den.axes[0].centers, ratio, yerr=ratio_err, fmt='o', color=color, alpha=alpha, markersize=4)
    return ax

def plot_ratio_errps(ax, h_num, h_den, color, alpha=0.8):
    h_num_values = h_num.values()
    h_num_variances = h_num.variances()
    h_den_values = h_den.values()
    h_num_rel_err = np.sqrt(h_num_variances) / h_den_values
    ratio = h_num_values/h_den_values
    ax.errorbar(h_den.axes[0].centers, ratio, yerr=h_num_rel_err, fmt='o', color=color, alpha=alpha, markersize=4)
    return ax

# 2D plotting
def plot_2d_hist(ax, h, cmap="viridis", density=False, logz=False):
    if density:
        h *= (1/(h.values().sum()))
    hep.hist2dplot(h, ax=ax, cbarextend=True, cmap=cmap, norm=LogNorm() if logz else None)
    return h, ax

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
        norm=LogNorm(vmin=0.1, vmax=2) if logz else Normalize(vmin=0.5, vmax=1.5),
        cmap="viridis",
        #cmap="bwr"
    )
    return ax

# Example: python3 plotting_scripts/plot_2025Performance.py --files outputs/Combined/StripUnpacking/hltphysics_doublemuonvtx_jpsi_baseline.root outputs/Combined/StripUnpacking/hltphysics_doublemuonvtx_jpsi_customise_case1.root --labels Baseline Customise1 --addtxt "Vtx muons\nPass DST_PFScouting_DoubleMuonVtx\nDimuon selections" --outdir plots/hltphysics_doublemuonvtx_jpsi/
parser = argparse.ArgumentParser("Plot and compare datasets for muon performance")
parser.add_argument("--files", type=str, nargs="+", help="Files to open")
parser.add_argument("--labels", type=str, nargs="+", help="Labels for each of the files")
parser.add_argument("--lumis", type=float, nargs="*", help="List of luminosities for each file")
parser.add_argument("--norm", action="store_true", help="Normalize histograms to unit area")
parser.add_argument("--addtxt", type=str, help="Additional text")
parser.add_argument("--rlabel", type=str, default="1 \fb (13.6 TeV)$", help="Directory to store plots in")
parser.add_argument("--outdir", type=str, default="plots/performance", help="Directory to store plots in")
args = parser.parse_args()
colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

cwd = os.getcwd()
files = args.files
labels = args.labels
norm = args.norm
lumis = args.lumis
outdir = args.outdir
addtxt = args.addtxt
if lumis is None:
    lumis = np.ones(len(files))
if addtxt is not None:
    addtxt = addtxt.replace("\\n", "\n")

os.makedirs(outdir, exist_ok=True)

# Exceptions
if len(files) != len(labels):
    raise RuntimeError(f"File and label sizes {len(files)} and {len(labels)} uneven")

f_list = []
for file in files:
    f = uproot.open(file)
    f_list.append(f)
colors = colors[:len(files)]

# Print cutflow

# Plot variables that can be described generically
vars_dict = {
    "mass_JPsi": {
        "hname": "mass_JPsi",
        "label": r"$m_{\mu\mu}$ [GeV]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": None,
    },
    "mass_Z": {
        "hname": "mass_Z",
        "label": r"$m_{\mu\mu}$ [GeV]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": None,
    },
    "pt": {
        "hname": "pt",
        "label": r"Scouting muon $p_T$ [GeV]",
        "legend_loc": "upper right",
        "text_pos_x": 0.60,
        "text_pos_y": 0.70,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    "eta": {
        "hname": "eta",
        "label": r"Scouting muon $\eta$",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": None,
    },
    "phi": {
        "hname": "phi",
        "label": r"Scouting muon $\phi$",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": None,
    },
    "dxy_recomputed": {
        "hname": "dxy_recomputed",
        "label": r"Scouting muon recomputed $d_{xy}$ [cm]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    "dxy_recomputed_zoom": {
        "hname": "dxy_recomputed_zoom",
        "label": r"Scouting muon recomputed $d_{xy}$ [cm]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    "dz_recomputed": {
        "hname": "dz_recomputed",
        "label": r"Scouting muon recomputed $d_{z}$ [cm]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    "dz_recomputed_zoom": {
        "hname": "dz_recomputed_zoom",
        "label": r"Scouting muon recomputed $d_{z}$ [cm]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    "pv_z": {
        "hname": "pv_z",
        "label": r"Primary vertex $z$ [cm]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": None,
    },
    "vz": {
        "hname": "vz",
        "label": r"Scouting muon $v_{z}$ [cm]",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": None,
    },
    "pixelLayers": {
        "hname": "pixelLayers",
        "label": r"Scouting muon pixelLayers",
        "legend_loc": "upper left",
        "text_pos_x": 0.60,
        "text_pos_y": 0.80,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    "trackerLayers": {
        "hname": "trackerLayers",
        "label": r"Scouting muon trackerLayers",
        "legend_loc": "upper left",
        "text_pos_x": 0.05,
        "text_pos_y": 0.60,
        "ratio_ylim": (0.8, 1.2),
        "yscale": "log",
    },
    
}

# Plot 1D histograms
for key in vars_dict.keys():
    print(f"\nPlotting {key}")

    var_dict = vars_dict[key]

    h_list = []
    fig, axs = plt.subplots(2, 1, gridspec_kw=dict(height_ratios=[3, 1], hspace=0.1), sharex=True)

    for i, f in enumerate(f_list):
        h = f[f"{var_dict['hname']}"].to_hist()
        h *= (1.0/lumis[i])
        h_list.append(h)
        h, axs[0] = plot_1d_hist(axs[0], h, f"{labels[i]}", colors[i], density=args.norm)
        if i == 0:
            h_values = h.values()
            h_variances = h.variances()
            h_rel_err = np.sqrt(h_variances) / h_values  
            axs[1].stairs(1+h_rel_err, edges=h.axes[0].edges, baseline=1-h_rel_err, **errps)
        else:
            axs[1] = plot_ratio_errps(axs[1], h_num=h, h_den=h_list[0], color=colors[i])
    axs[0].set_xlabel("")
    axs[0].set_ylabel("Counts")
    if var_dict['yscale'] is not None: axs[0].set_yscale("log")
    axs[0].legend(fontsize=16*1.2, loc=f"{var_dict['legend_loc']}", ncol=1)
    if addtxt is not None: axs[0].text(var_dict['text_pos_x'], var_dict['text_pos_y'], f"{addtxt}", transform=axs[0].transAxes, fontsize=16)
    axs[1].set_xlabel(f"{var_dict['label']}")
    axs[1].set_ylabel(f"Ratio to {labels[0]}")
    axs[1].set_ylim(*var_dict['ratio_ylim'])
    axs[1].axhline(1, color='black', linestyle='--')
    hep.cms.label(data=True, llabel="Preliminary", rlabel=args.rlabel, ax=axs[0])
    plt.savefig(f"{outdir}/{key}.png")
    plt.close()

# Plot 2D histograms

# Profile pixel and tracker layers histograms both in 2D and profiled in angle
for layerName in ["pixelLayers", "trackerLayers"]:
    for angle in ["eta", "phi"]:
        print(f"\nPlotting {layerName} profiled in {angle}")

        var_dict_layer = vars_dict[layerName]
        var_dict_angle = vars_dict[angle]

        h_list_2d = []
        h_list = []
        fig, axs = plt.subplots(2, 1, gridspec_kw=dict(height_ratios=[3, 1], hspace=0.1), sharex=True)

        # Plot profiled histograms
        for i, f in enumerate(f_list):
            h = f[f"{var_dict_angle['hname']}_{var_dict_layer['hname']}"].to_hist()
            h *= (1.0/lumis[i])
            h_list_2d.append(h)
            h = h.profile(1)
            h_list.append(h)
            h, axs[0] = plot_1d_hist(axs[0], h, f"{labels[i]}", colors[i], density=args.norm, histtype="errorbar")
        if i == 0:
            h_values = h.values()
            h_variances = h.variances()
            h_rel_err = np.sqrt(h_variances) / h_values  
            axs[1].stairs(1+h_rel_err, edges=h.axes[0].edges, baseline=1-h_rel_err, **errps)
        else:
            axs[1] = plot_ratio_errps(axs[1], h_num=h, h_den=h_list[0], color=colors[i])
        axs[0].set_xlabel("")
        axs[0].set_ylabel(r"Avg." + f"{var_dict_layer['label']}")
        axs[0].legend(fontsize=16*1.2, loc=f"{var_dict_layer['legend_loc']}", ncol=1)
        if addtxt is not None: axs[0].text(var_dict_layer['text_pos_x'], var_dict_layer['text_pos_y'], f"{addtxt}", transform=axs[0].transAxes, fontsize=16)
        axs[1].set_xlabel(f"{var_dict_angle['label']}")
        axs[1].set_ylabel(f"Ratio to {labels[0]}")
        axs[1].set_ylim(*var_dict_layer['ratio_ylim'])
        axs[1].axhline(1, color='black', linestyle='--')
        hep.cms.label(data=True, llabel="Preliminary", rlabel=args.rlabel, ax=axs[0])
        plt.savefig(f"{outdir}/{angle}_{layerName}_profiled.png")
        plt.close()

        # Plot 2D histograms
        for i, h_2d in enumerate(h_list_2d):
            fig, ax = plt.subplots()
            h_2d, ax = plot_2d_hist(ax, h_2d, cmap="viridis", density=args.norm, logz=False)
            ax.set_xlabel(f"{var_dict_angle['label']}")
            ax.set_ylabel(f"{var_dict_layer['label']}")
            hep.cms.label(data=True, llabel="Preliminary", rlabel=args.rlabel, ax=ax)
            plt.savefig(f"{outdir}/{angle}_{layerName}_{labels[i]}.png")
            plt.close()

            # Plot ratio wrt first
            if i > 0:
                fig, ax = plt.subplots()
                ax = plot_2d_ratio(ax, h_num=h_2d, h_den=h_list_2d[0], logz=False)
                ax.set_xlabel(f"{var_dict_angle['label']}")
                ax.set_ylabel(f"{var_dict_layer['label']}")
                hep.cms.label(data=True, llabel="Preliminary", rlabel=args.rlabel, ax=ax)
                plt.savefig(f"{outdir}/{angle}_{layerName}_{labels[i]}_over_{labels[0]}.png")
