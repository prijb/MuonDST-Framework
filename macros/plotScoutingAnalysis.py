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
    fig, ax = plt.subplots(figsize=(12, 9))
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
    legsize = 20 if len(labels)<7 else 11
    lcol = 1 #if len(labels)<7 else 2
    ax.legend(fontsize=legsize, ncol=lcol)
    ax.text(0.2, 1e8, extra, fontsize=12, color='black')
    fig.savefig(name+".png", dpi=140)
    

if __name__ == "__main__":

    ### L1 splitting plot
    #tag = '2024E'
    #inputdir = '/eos/user/f/fernance/DST-Muons'
    #histogram = 'SelSVNoVtx_mass'

    #L1Seeds = []
    #L1Seeds.append("Total")
    #L1Seeds.append("L1_DoubleMu_15_7")
    #L1Seeds.append("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7")
    ##L1Seeds.append("L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18")
    #L1Seeds.append("L1_DoubleMu8_SQ")
    #L1Seeds.append("L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6")
    #L1Seeds.append("L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4")
    #L1Seeds.append("L1_DoubleMu4p5_SQ_OS_dR_Max1p2")
    #L1Seeds.append("L1_DoubleMu0_Upt15_Upt7")
    #L1Seeds.append("L1_DoubleMu0_Upt6_IP_Min1_Upt4")

    #histos = []
    #for l1seed in L1Seeds:
    #    filename = '%s/ScoutingOutput_%s_%s/output_%s_%s_all.root'%(inputdir, tag, l1seed, tag, l1seed)
    #    if not os.path.exists(filename):
    #        os.system('hadd %s %s/ScoutingOutput_%s_%s/output_%s_%s_*.root'%(filename, inputdir, tag, l1seed, tag, l1seed))
    #    print(filename)
    #    histos.append(getObject(filename, histogram))    

    ### Plot histograms
    #plotHistograms(histogram+'_L1seed', histos, histogram, L1Seeds, False, tag, 7.81, True, True, r'$\Delta R > 0.2$, OS-charge, $\chi^{2}/$ndof $<10$')

    ### Era comparison
    inputdir = '/eos/user/f/fernance/DST-Muons'
    file1 = '%s/ScoutingOutput_2024D_Total/output_2024D_Total_all.root'%(inputdir)
    file2 = '%s/ScoutingOutput_2024E_Total/output_2024E_Total_all.root'%(inputdir)
    if not os.path.exists(file1):
        os.system('hadd %s %s/ScoutingOutput_2024D_Total/output_2024D_Total_*.root'%(file1, inputdir))
    if not os.path.exists(file2):
        os.system('hadd %s %s/ScoutingOutput_2024E_Total/output_2024E_Total_*.root'%(file2, inputdir))
    #histogram = 'SelSVNoVtx_mass'
    for histogram in ['SelSVNoVtx_mass', 'MuonNoVtx_pt', 'MuonNoVtx_eta']:
        histo1 = getObject(file1, histogram)
        histo2 = getObject(file2, histogram)
        histo2.Scale(6.1945/7.8317)
        comps = [histo1, histo2]
        if 'mass' in histogram:
            plotHistograms(histogram+'_eraDE', comps, histogram, [r'2024D (6.19 fb$^{-1}$)', '2024E (7.83 fb$^{-1}$, scaled)'], False, '2024', '6.19', True, True)
        else:
            plotHistograms(histogram+'_eraDE', comps, histogram, [r'2024D (6.19 fb$^{-1}$)', '2024E (7.83 fb$^{-1}$, scaled)'], False, '2024', '6.19', True, False)



