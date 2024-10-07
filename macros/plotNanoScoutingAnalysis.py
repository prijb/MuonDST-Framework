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
    

if __name__ == "__main__":

    ### Vtx vs NoVtx comparison
    inputdir = '/eos/user/f/fernance/DST-Muons'
    inputfiles = []
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_0.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_1.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_2.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_3.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_4.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_5.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_6.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_7.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_8.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_9.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_10.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_11.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_12.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_13.root')
    inputfiles.append('/eos/user/f/fernance/DST-Muons/ScoutingOutput_Run2024E_DST_PFScouting_ZeroBias_12_0_Total/output_Run2024E_DST_PFScouting_ZeroBias_12_0_Total_14.root')
    histogram = 'ScoutingMuonNoVtx_pt'
    histogram_list = []
    histogram_list.append(['ScoutingMuonVtx_pt', 'ScoutingMuonNoVtx_pt'])
    #histogram_list.append(['ScoutingMuonVtx_eta', 'ScoutingMuonNoVtx_eta'])
    histogram_list.append(['ScoutingMuonVtx_phi', 'ScoutingMuonNoVtx_phi'])
    for histogram in histogram_list:
        for i,inputfile in enumerate(inputfiles):
            if not i:
                histoVtx = getObject(inputfile, histogram[0])
                histoNoVtx = getObject(inputfile, histogram[1])
            else:
                histoVtx.Add(getObject(inputfile, histogram[0]))
                histoNoVtx.Add(getObject(inputfile, histogram[1]))
        plotHistograms(histogram[0], [histoVtx, histoNoVtx], histogram[0], ['MuonVtx', 'MuonNoVtx'], False, 2024, 7.81, False, False, '')
