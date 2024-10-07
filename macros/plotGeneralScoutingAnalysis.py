import ROOT as r
import numpy as np
import optparse
from include.plotTools import *
import __main__
import mplhep as hep
import matplotlib.pyplot as plt

PWD = ''
for _p,path in enumerate(os.path.abspath(__main__.__file__).split('/')):
       if _p == len(os.path.abspath(__main__.__file__).split('/')) - 1: break
       PWD += path + '/'
print(PWD)

r.gROOT.LoadMacro(PWD+'include/tdrstyle.C')
r.gROOT.LoadMacro(PWD+'libraries/muon_scouting_run3.C')
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

def plotHistograms(name, histos, var, labels, isstack, year='X', lumi=[1.0], ylog=False, xlog=False, extra = '', norm=False):
    hs = []
    colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]
    
    for h_,h in enumerate(histos):
        hs_, bins_ = getValues(h)
        print(len(hs_))
        print(len(bins_))
        if norm:
            hs_ = hs_/lumi[h_]
        hs.append(hs_)
        bins = bins_
    dtype = 'fill' if isstack else 'step'
    print(dtype)
    fig, ax = plt.subplots(figsize=(10, 8))
    htype = dtype
    hep.histplot(
        hs,
        bins=bins, # Assumed that all of them have same binning
        histtype=htype,
        color=colors[:len(hs)],
#        edgecolor="black" if isstack else colors[:len(hs)],
        label=labels,
        stack=isstack,
        ax=ax,
    )
    if norm:
        hep.cms.label("Preliminary", data=True, year=year, lumi='1', com='13.6')
    else:
        hep.cms.label("Preliminary", data=True, year=year, lumi='X', com='13.6')
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
    

if __name__ == "__main__":

    ### Input
    histograms2024 = [] # era, path, lumi
    histograms2024.append(['2024D', '/eos/user/f/fernance/DST-Muons/histograms/output_2024D.root', 3.782298009])
    histograms2024.append(['2024E', '/eos/user/f/fernance/DST-Muons/histograms/output_2024E.root', 9.391270340])
    histograms2024.append(['2024G', '/eos/user/f/fernance/DST-Muons/histograms/output_2024G.root', 6.715007344])

    ### Per era histograms
    hname_perEra = [] # name, xlog
    hname_perEra.append(['h_DoubleMu_SVNoVtx_mass_Total', True])
    hname_perEra.append(['h_DoubleMu_MuonNoVtx_pt_Total', False])
    hname_perEra.append(['h_DoubleMu_MuonNoVtx_eta_Total', False])
    hname_perEra.append(['h_DoubleMu_MuonNoVtx_phi_Total', False])
    hname_perEra.append(['h_SingleMu_MuonVtx_pt_Total', False])
    hname_perEra.append(['h_SingleMu_MuonVtx_eta_Total', False])
    hname_perEra.append(['h_SingleMu_MuonVtx_phi_Total', False])

    for histo in hname_perEra:
        hs = []
        labels = []
        lumis = []
        hname = histo[0]
        xlog = histo[1]
        for file in histograms2024:
            hs.append(getObject(file[1], hname))
            labels.append(r'%s (%.2f fb$^{-1}$)'%(file[0], file[2]))
            lumis.append(file[2])
        plotHistograms(hname, hs, 'Dimuon mass (GeV)', labels, False, 2024, lumis, True, xlog, '', True)

