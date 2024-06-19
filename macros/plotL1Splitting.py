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
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
    return np.array(values)

def plotHistograms(name, histos, var, bins, labels, isstack, ylog=False, xlog=False):
    hs = []
    colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]
    
    for h in histos:
        hs.append(getValues(h))
    fig, ax = plt.subplots(figsize=(12, 9))
    htype = 'fill' if isstack else 'step'
    hep.histplot(
        hs,
        bins=bins,
        histtype=htype,
        color=colors[:len(hs)],
#        alpha=0.8,
        edgecolor="black" if isstack else colors[:len(hs)],
        label=labels,
        stack=isstack,
        ax=ax,
    )
    hep.cms.label("Preliminary", data=True, year='2024D', lumi='X', com='13.6')
    ax.set_xlabel(histos[0].GetXaxis().GetTitle(), fontsize=20)
    ax.set_ylabel("Events", fontsize=20)
    if ylog:
        ax.set_yscale('log')
        ax.set_ylim(0.1, 100*max([max(x) for x in hs]))
    if xlog:
        ax.set_xscale('log')
    ax.set_xlim(bins[0], bins[-1])
    legsize = 15 if len(labels)<7 else 10
    ax.legend(fontsize=15)
    fig.savefig(name+".png", dpi=140)
    

if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog [opts] FilenameWithSamples', version='%prog 1.0')
    parser.add_option('-v', '--var', action='store', type=str, dest='var', default='', help='Variable to plot')
    parser.add_option('-b', '--bins', action='store', type=int, dest='bins', default=1, help='Number of bins')
    parser.add_option('-m', '--xmin', action='store', type=float, dest='xmin', default=0.0, help='xmin')
    parser.add_option('-M', '--xmax', action='store', type=float, dest='xmax', default=100.0, help='xmax')
    parser.add_option('-x', '--xlog', action='store', type=int,  dest='xlog', default=0, help='If xlog')
    parser.add_option('--qsplit', action='store', type=int,  dest='qsplit', default=0, help='If it should be done with split in charge')
    (opts, args) = parser.parse_args()

    ## Running parameters
    var = opts.var
    xlog = opts.xlog
    bins = opts.bins
    xmin = opts.xmin
    xmax = opts.xmax
    
    ## Load samples
    inputdir = '/eos/user/f/fernance/DST-Muons/2023D_fix/ScoutingPFRun3/2023D_fix/240531_222546' # 2023D
    inputdir = '/eos/user/f/fernance/DST-Muons/2024D_fix/ScoutingPFRun3/2024D_fix/240531_222314' # 20234D
    inputdir = '/eos/user/f/fernance/DST-Muons/2024D_dimuon/ScoutingPFRun3/2024D_dimuon/240610_213840' # 20234D
    tchain = r.TChain('Events')
    for root, dirs, files in os.walk(inputdir):
        for f in files:
            if '.root' in f:
                print('Including %s file'%(f))
                tchain.Add(os.path.join(root, f))
                #break
    print(f'Init RDataFrame with {tchain.GetEntries()} entries')
    
    ## Load dataframe
    rdf = r.RDataFrame(tchain)
    
    ## Filters
    #rdf = rdf.Filter("nSVNoVtx == 1")

    ## Definitions
    print('Setting definitions...')
    #rdf = rdf.Define("SVNoVtx_selected", "(SVNoVtx_nAssocMuon>1 && SVNoVtx_isValid)") # Por lo general ya definido
    #rdf = rdf.Define("SelSVNoVtx_mass", "SVNoVtx_mass[SVNoVtx_selected]")
    #rdf = rdf.Define("nSelSVNoVtx", "SelSVNoVtx_mass.size()")
    #rdf = rdf.Define("SelSVNoVtx_idx1", "SVNoVtx_idx1[SVNoVtx_selected]")
    #rdf = rdf.Define("SelSVNoVtx_idx2", "SVNoVtx_idx2[SVNoVtx_selected]")
    #rdf = rdf.Define("SelSVNoVtx_didx", "SVNoVtx_idx1[SVNoVtx_selected] - SVNoVtx_idx2[SVNoVtx_selected]")
    #rdf = rdf.Define("SelSVNoVtx_pt1", "GetElements<float>(MuonNoVtx_pt, SelSVNoVtx_idx1)")
    #rdf = rdf.Define("SelSVNoVtx_pt2", "GetElements<float>(MuonNoVtx_pt, SelSVNoVtx_idx2)")
    #rdf = rdf.Define("SelSVNoVtx_charge1", "GetElements<int>(MuonNoVtx_charge, SelSVNoVtx_idx1)")
    #rdf = rdf.Define("SelSVNoVtx_charge2", "GetElements<int>(MuonNoVtx_charge, SelSVNoVtx_idx2)")
    ## For one SV case
    rdf = rdf.Define("SVNoVtx_pt1", "GetElements<float>(MuonNoVtx_pt, SVNoVtx_idx1)")
    rdf = rdf.Define("SVNoVtx_pt2", "GetElements<float>(MuonNoVtx_pt, SVNoVtx_idx2)")
    rdf = rdf.Define("SVNoVtx_charge1", "GetElements<int>(MuonNoVtx_charge, SVNoVtx_idx1)")
    rdf = rdf.Define("SVNoVtx_charge2", "GetElements<int>(MuonNoVtx_charge, SVNoVtx_idx2)")
    
    print('Definitions set')
    
    ## Main Vtx case
    rdf = rdf.Define("SVNoVtx_OS", "(SVNoVtx_charge1*SVNoVtx_charge2 < 0)")
    rdf = rdf.Define("SelSVNoVtx_mass", "SVNoVtx_mass[SVNoVtx_OS]")
    
    
    ## L1 rdfs
    L1Seeds = []
    L1Seeds.append("Total")
    L1Seeds.append("L1_DoubleMu_15_7")
    L1Seeds.append("L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7")
    L1Seeds.append("L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18")
    L1Seeds.append("L1_DoubleMu8_SQ")
    L1Seeds.append("L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6")
    L1Seeds.append("L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4")
    L1Seeds.append("L1_DoubleMu4p5_SQ_OS_dR_Max1p2")
    L1Seeds.append("L1_DoubleMu0_Upt15_Upt7")
    L1Seeds.append("L1_DoubleMu0_Upt6_IP_Min1_Upt4")
    
    L1rdfs = []
    for l1seed in L1Seeds:
        if "Total" in l1seed:
            L1rdfs.append(rdf)
        else:
            L1rdfs.append(rdf.Filter("%s == 1"%(l1seed)))
        print(f'{l1seed} RDataFrame has {L1rdfs[-1].Count().GetValue()} entries')
    
    
   # L1rdfs[0] = L1rdfs[0].Filter("(nSelSVNoVtx==1)")
   # L1rdfs[0] = L1rdfs[0].Range(10)
   # print("MuonNoVtx_pt", L1rdfs[0].Take["ROOT::RVec<float>"]("MuonNoVtx_pt").GetValue())
    #print(list(L1rdfs[0].Show("MuonNoVtx_pt"))

    ## Filling
    xlabel = ''
    if 'mass' in var:
        xlabel = '; Mass m_{\mu\mu} (GeV); Number of dimuons'
    elif 'pt' in var and 'Muon' in var:
        xlabel = '; Muon p_{T} (GeV); Number of muons'
    elif 'eta' in var and 'Muon' in var:
        xlabel = '; Muon |#eta|; Number of muons'
    elif 'run' in var:
        xlabel = ';Run number; Number of events'
    
    histo_cfg = []
    if xlog:
        xbins = np.logspace(xmin, xmax, bins+1)
        histo_cfg.append([var, xlabel, np.logspace(xmin, xmax, bins+1)])
    else:
        xbins = np.linspace(xmin, xmax, bins+1)
        histo_cfg.append([var, xlabel, np.linspace(xmin, xmax, bins+1)])
    histos = []
    for cfg in histo_cfg:
        hlist = []
        for d,df in enumerate(L1rdfs):
            hlist.append(df.Histo1D((cfg[0]+"_"+L1Seeds[d].split(" ")[0], cfg[1], len(cfg[2])-1, cfg[2]), cfg[0]))
            print('Histogram with %f'%(hlist[-1].GetEntries()))
        histos.append(hlist)

    ## Dedicated histograms  
    if opts.qsplit:
        L1rdfs_ss = L1rdfs[0].Define(var+'_ss', "%s[(SelSVNoVtx_charge1*SelSVNoVtx_charge2>0.0)]"%(var))
        L1rdfs_os = L1rdfs[0].Define(var+'_os', "%s[(SelSVNoVtx_charge1*SelSVNoVtx_charge2<0.0)]"%(var))
        hss = L1rdfs_ss.Histo1D((cfg[0]+"_ss", cfg[1], len(cfg[2])-1, cfg[2]), cfg[0]+'_ss')
        hos = L1rdfs_os.Histo1D((cfg[0]+"_os", cfg[1], len(cfg[2])-1, cfg[2]), cfg[0]+'_os')
        plotHistograms('qsplit_'+var, [hss, hos], var, xbins, ['Same-sign (SS) dimuons', 'Opposite-sign (OS) dimuons'], True, True, xlog)

    ## Plotting
    outputdir = PWD + '/L1Plots/'
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    plotHistograms(var, hlist, var, xbins, L1Seeds, False, True, xlog)
