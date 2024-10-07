import ROOT as r
import uproot
import numpy as np
import optparse
from include.plotTools import *
import __main__
import mplhep as hep
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

PWD = ''
for _p,path in enumerate(os.path.abspath(__main__.__file__).split('/')):
       if _p == len(os.path.abspath(__main__.__file__).split('/')) - 1: break
       PWD += path + '/'
print(PWD)

r.gROOT.LoadMacro(PWD+'include/tdrstyle.C')
#r.gROOT.LoadMacro(PWD+'libraries/muon_scouting_run3.C')
r.gROOT.SetBatch(1)
r.setTDRStyle()
hep.style.use("CMS")

### Plotting functions

def getValues(histo):
    values = []
    bins = []
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
        bins.append(histo.GetBinLowEdge(n))
    bins.append(histo.GetBinLowEdge(n) + histo.GetBinWidth(n))
    return np.array(values), np.array(bins)




def plotHistograms(name, histos, var, labels, isstack, year='X', lumi='', ylog=False, xlog=False, extra = ''):
    hs = []
    colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]
    
    for h in histos:
        hs_, bins_ = getValues(h)
        print(len(hs_))
        print(len(bins_))
        hs.append(hs_)
        bins = bins_
    fig, ax = plt.subplots(figsize=(10, 8))
    htype = 'fill' if isstack else 'step'
    hep.histplot(
        hs,
        bins=bins, # Assumed that all of them have same binning
        histtype=htype,
        color=colors[:len(hs)],
        edgecolor="black" if isstack else colors[:len(hs)],
        label=labels,
        stack=isstack,
        ax=ax,
    )
    hep.cms.label("Preliminary", data=True, year=year, lumi=lumi, com='13.6')
    ax.set_xlabel(histos[0].GetXaxis().GetTitle(), fontsize=20)
    ax.set_ylabel("Events", fontsize=20)
    if ylog:
        ax.set_yscale('log')
        ax.set_ylim(0.1, 100*max([max(x) for x in hs]))
    if xlog:
        ax.set_xscale('log')
    ax.set_xlim(bins[0], bins[-1])
    legsize = 16 
    lcol = 1 #if len(labels)<7 else 2
    ax.legend(fontsize=legsize, ncol=lcol)
    ax.text(0.2, 1e8, extra, fontsize=12, color='black')
    fig.savefig(name+".png", dpi=140)
    
def plotHistogramsWithRatio(name, histos, var, labels, isstack, year='X', lumi='', ylog=False, xlog=False, extra = ''):
    hs = []
    colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]
    
    for h in histos:
        hs_, bins_ = getValues(h)
        hs.append(hs_)
        bins = bins_

    # ratio:
    ratio = hs[1]/hs[0]
    sigma0 = np.sqrt(hs[0])
    sigma1 = np.sqrt(hs[1])
    error_ratio = ratio * np.sqrt((sigma0 / hs[0])**2 + (sigma1 / hs[1])**2)

    # Figure
    fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(10, 10), sharex=True)
    htype = 'fill' if isstack else 'step'
    hep.histplot(
        hs,
        bins=bins, # Assumed that all of them have same binning
        histtype=htype,
        color=colors[:len(hs)],
        edgecolor="black" if isstack else colors[:len(hs)],
        label=labels,
        stack=isstack,
        ax=ax1,
    )
    hep.cms.label("Preliminary", data=True, year=year, lumi='X', com='13.6', ax=ax1)
    ax2.plot(bins[:-1], ratio, '-', color='gray', label='Offline / Scouting')
    ax2.fill_between(bins[:-1], ratio - error_ratio, ratio + error_ratio, color='gray', step='mid', label='Error Band')
    ax2.axhline(1, color='black', linestyle='dotted')
    ax2.set_xlabel(histos[0].GetXaxis().GetTitle(), fontsize=20)
    ax1.set_ylabel("Events", fontsize=20)
    if ylog:
        ax1.set_yscale('log')
        ax1.set_ylim(0.1, 100*max([max(x) for x in hs]))
    if xlog:
        ax1.set_xscale('log')
        ax2.set_xscale('log')
    ax2.set_xlim(bins[0], bins[-1])
    ax1.set_xlim(bins[0], bins[-1])
    ax1.set_xlim(0.2, 20.0)
    ax2.set_xlim(0.2, 20.0)
    ax2.set_ylim(0.5, 1.5)
    legsize = 16 
    lcol = 1 #if len(labels)<7 else 2
    ax1.legend(fontsize=legsize, ncol=lcol)
    ax1.text(0.2, 1e8, extra, fontsize=12, color='black')
    fig.savefig(name+"_ratio.png", dpi=140)

if __name__ == "__main__":

    ### Vtx vs NoVtx comparison
    inputdir = '/eos/user/f/fernance/DST-Muons'
    inputfiles = []
    #inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_PFMon_Total/output_PFMon_Total_0.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/output_Run2024G_DST_PFScouting_DoubleMuon_none_old.root')
    histogram_list = []
    #histogram_list.append(['DiMuon_mass', 'DiScoutingMuonVtx_mass'])
    #histogram_list.append(['DiMuon_mass', 'DiScoutingMuonNoVtx_mass'])
    histogram_list.append(['DiScoutingMuonNoVtx_mass', 'DiMuon_mass'])
    for histogram in histogram_list:
        for i,inputfile in enumerate(inputfiles):
            if not i:
                histo0 = getObject(inputfile, histogram[0])
                histo1 = getObject(inputfile, histogram[1])
            else:
                histo0.Add(getObject(inputfile, histogram[0]))
                histo1.Add(getObject(inputfile, histogram[1]))
        histo0.Scale(1, "width")
        histo1.Scale(1, "width")
        plotHistogramsWithRatio(histogram[0], [histo0, histo1], histogram[0], ['Scouting', 'Offline'], False, 2024, 1.0, True, True, '')

    # 2D histograms
    h2d_list = [['2D_mass', r'Offline muon $m_{\mu\mu}$ GeV', r'Scouting muon $m_{\mu\mu}$ GeV']]
    for h2d in h2d_list:
        for i,inputfile in enumerate(inputfiles):
            file = uproot.open(inputfile)
            hist = file[h2d[0]]
            # Extraer los valores de los bins
            counts = hist.values()
            x_edges = hist.axes[0].edges()
            y_edges = hist.axes[1].edges()
            # Figure
            fig, ax = plt.subplots(figsize=(12, 12))
            mesh = ax.pcolormesh(x_edges, y_edges, counts.T, cmap='Reds', norm=mcolors.LogNorm(vmin=counts.min()+1e-3, vmax=counts.max()))
            cbar = fig.colorbar(mesh, ax=ax, label="Counts")
            ax.set_xlabel(h2d[1])  # Etiqueta del eje X desde ROOT
            ax.set_ylabel(h2d[2])
            ax.set_xscale('log')
            ax.set_yscale('log')
            hep.cms.label("Preliminary", data=True, year=2024, lumi=1, com='13.6')
            fig.savefig("%s.png"%(h2d[0]), dpi=140)
