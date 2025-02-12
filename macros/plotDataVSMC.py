import ROOT as r
from ROOT import gDirectory, gROOT, gStyle, gPad
import optparse
import os
from include.plotTools import *
import mplhep as hep

def getValues(histo):
    values = []
    errors = []
    bins = []
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
        errors.append(histo.GetBinError(n))
        bins.append(histo.GetBinLowEdge(n))
    bins.append(histo.GetBinLowEdge(n) + histo.GetBinWidth(n))
    return np.array(values), np.array(errors), np.array(bins)

if __name__ == "__main__":

    r.gROOT.LoadMacro('include/tdrstyle.C')
    r.gROOT.SetBatch(1)
    r.setTDRStyle()
    r.gStyle.SetPadRightMargin(0.12)

    data_filename = '/eos/user/f/fernance/DST-Muons/ScoutingOutput_DataVSMC/output_data.root'
    mc_filename = '/eos/user/f/fernance/DST-Muons/ScoutingOutput_DataVSMC/output_mc.root'


    histos = []
    histos.append(['SelDiMuonVtx_mass', r'Dimuon mass $m_{\mu\mu}$ (GeV)'])
    histos.append(['SelMuonVtx_pt', r'Muon $p_{T}$ (GeV)'])
    histos.append(['SelMuonVtx_eta', r'Muon mass $|\eta|$ '])

    for h in histos:

        ## Plot histograms
        data_histo_mass = getObject(data_filename, h[0])
        mc_histo_mass = getObject(mc_filename, h[0])

        mc_histo_mass.Scale(data_histo_mass.Integral()/mc_histo_mass.Integral())

        ratio_histo_mass = data_histo_mass.Clone('ratio')
        ratio_histo_mass.Divide(mc_histo_mass)

        plt.style.use(hep.style.CMS)
        fig, (ax, ax_ratio) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1], 'hspace': 0.05}, sharex=True, figsize=(10, 10))
        # Main plot
        hep.cms.label("Preliminary", data=True, year='2024I', com='13.6', ax=ax)
        dv, de, db = getValues(data_histo_mass)
        ddb = db + 0.5*(db[1]-db[0])
        ax.set_ylim(0.0,1.45*max(dv))
        ax.errorbar(ddb[:-1], dv, yerr=de, fmt='o', capsize=5, label='Data', color='k', markersize=8)
        mv, me, mb = getValues(mc_histo_mass)
        hep.histplot(mv, mb, color="darkturquoise", edgecolor="teal", label = r'$Z\rightarrow \mu\mu$ (m > 50 GeV)', histtype="fill", ax=ax)
        hep.histplot(mv, mb, color="teal", histtype="step", ax=ax)
        ax.legend(loc='upper left', fontsize = 18, frameon = True, ncol=1)
        ax.set_ylabel(r'Events / %.1f GeV'%(db[1]-db[0]), fontsize=24)
        ax.set_xlabel('')
        #ax.set_xlim(81, 101)
        # Residual subplot
        rv, re, rb = getValues(ratio_histo_mass)
        ax_ratio.errorbar(ddb[:-1], rv, yerr=re, fmt='o', capsize=5, label='Data', color='k', markersize=8)
        ax_ratio.axhline(y=1, color='gray', linestyle='--', linewidth=1)
        ax_ratio.set_ylabel("Ratio")
        ax_ratio.set_ylim([0.0, 2.0])
        ax_ratio.set_xlabel(h[1])
        #
        ax.text(0.04, 0.8, r'2 OS Global muons', fontsize=16, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        ax.text(0.04, 0.75, r'$p_{T} >$ 10 GeV, $|\eta|$ < 2.4', fontsize=16, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        ax.text(0.04, 0.7, r'TightID applied', fontsize=16, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        #
        props = dict(boxstyle='round', facecolor='wheat', alpha=1.0)
        ax.text(0.95, 0.95, r'81 < $m_{\mu\mu}$ < 101 GeV', transform=ax.transAxes, fontsize=16, verticalalignment='top', horizontalalignment='right', bbox=props)
        #ax.text(0.04, 0.82, r'$\chi^{2}$/ndof < 10', fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        #ax.text(0.04, 0.78, r'Hits in chambers > 0', fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        #ax.text(0.04, 0.74, r'Matched stations > 1', fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        #ax.text(0.04, 0.70, r'Valid pixel hits > 0', fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        #ax.text(0.04, 0.66, r'Tracker layers > 5', fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        #ax.text(0.04, 0.62, r'$|d_{xy}| < 0.2$, |d_{z}| < 0.5 cm', fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        fig.savefig('%s.png'%(h[0]), dpi=140)



