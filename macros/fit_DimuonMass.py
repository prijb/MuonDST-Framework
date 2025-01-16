#!/bin/env python3                                                                                                                                               
import ROOT, array, random, copy                                                                                                    
from ROOT import TCanvas, TFile, TH1, TH1F, TF1, gSystem                                                                                        
import ROOT, array, random, copy                                                                                        
from ROOT import RooCmdArg, RooArgSet, kFALSE, RooLinkedList, kBlue, kRed, kBlack, kOpenStar, kWhite, kGray                                    
from ROOT import gStyle, TStyle, TGraph, TGraphErrors, TMath, TMultiGraph, TLine, gPad, TGaxis, TLegend, TText, TLatex, TColor, TPaveText      
from ROOT import TAttFill, TLegend, TRatioPlot, TPad, THStack, TFileCollection                                                      
from ROOT import kBlue, kRed, kBlack, kWhite, kAzure, kOrange, kPink, kGreen, kYellow, kCyan, kMagenta                                         
from ROOT import RooRealVar, RooDataHist, RooCBShape, RooGaussian, RooExponential, RooAddPdf, RooFit, RooArgList, RooPolynomial, RooBernstein
from ROOT import RooCmdArg, RooArgSet, RooLinkedList, kFALSE, kBlue, kRed, kBlack, kGray
from ROOT import gStyle, TCanvas, TLatex, TLegend, TFile
import math                                                                                                                             
import os                                                                                                            
import argparse                                                                                                                         
import sys
import numpy as np
import mplhep as hep
import matplotlib.pyplot as plt

argparser = argparse.ArgumentParser(description='Parser used for non default arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)  
argparser.add_argument('--outdir', dest='outdir', default='/eos/user/e/elfontan/www/CMS_SCOUTING/2024', help='Output directory')       
args = argparser.parse_args()                                                                                       
outputdir = args.outdir                                                                                                            

ROOT.gROOT.SetBatch()                                                                                          
ROOT.gStyle.SetOptStat(0)                                                                                    
ROOT.gStyle.SetOptTitle(0)

def getValues(histo):
    values = []
    bins = []
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
        bins.append(histo.GetBinLowEdge(n))
    bins.append(histo.GetBinLowEdge(n) + histo.GetBinWidth(n))
    return np.array(values), np.array(bins)

def fit_histogram_roofit(name, histogram, fit_range=(2.8, 3.4)):
    # Define observable: mass
    mass = RooRealVar("mass", "J/#psi Mass [GeV]", fit_range[0], fit_range[1])

    # Double Crystal Ball parameters
   # mean = RooRealVar("mean", "mean of crystal ball", 3.1, 2.85, 3.25)
   # sigma = RooRealVar("sigma", "width of crystal ball", 0.05, 0.001, 0.2)
   # alphaL = RooRealVar("alpha", "low side alpha", 1.0, 0.1, 3.0)
   # nL = RooRealVar("n", "low side n",1.0, 1.0, 2.0)
   # alphaR = RooRealVar("alpha", "low side alpha", 1.0, 0.1, 3.0)
   # nR = RooRealVar("n", "right side n", 1.0, 1.0, 2.0)



    # Double Crystal Ball components
    #cb = RooCBShape("cb", "cb", mass, mean, sigma, alphaL, nL)

    ## Gaussian parameters
    #gaus_mean = RooRealVar("gaus_mean", "mean of Gaussian", 3.1, 2.85, 3.25)
    #gaus_sigma = RooRealVar("gaus_sigma", "width of Gaussian", 0.03, 0.001, 0.2)
    #gauss = RooGaussian("gauss", "gauss", mass, gaus_mean, gaus_sigma)

    mean = RooRealVar("mean", "mean of crystal ball", 3.1, 2.85, 3.25)
    sigma = RooRealVar("sigma", "width of crystal ball", 0.02*3.1, 0.001, 0.09)
    gauss = RooGaussian("gauss", "gauss", mass, mean, sigma)
    #
    alphaL = RooRealVar("alphaL", "alphaL", 1.1, 1.0, 10.0)
    alphaR = RooRealVar("alphaR", "alphaR", 1.1, 1.0, 10.0)
    nL = RooRealVar("nL", "nL", 1.1, 1.0, 5.0)
    nR = RooRealVar("nR", "nR", 1.1, 1.0, 5.0)
    cb = RooCBShape("dcb", "dcb", mass, mean, sigma, alphaL, nL)

    # Background exponential
    #expo_slope  = RooRealVar("expo_slope","expo_slope",-0.02,-20.0,20.0);
    #background = RooExponential("background_exponential", "background_exponential",mass,expo_slope);
    #b0 = RooRealVar("b0", "constant term", 1.0, 0.0, 10.0)
    #b1 = RooRealVar("b1", "linear term", 1.0, -1.0, 5.0)
    #background = RooPolynomial("background", "background", mass, RooArgList(b0, b1))
    par0 = RooRealVar("pbern0_order2", "pbern0_order2", 0.0, 0.0, 10.0)
    par1 = RooRealVar("pbern1_order2", "pbern1_order2", 0.0, 0.0, 10.0)
    par2 = RooRealVar("pbern2_order2", "pbern2_order2", 0.0, 0.0, 10.0)
    background = RooBernstein("background_bernstein_order2","background_bernstein_order2",mass,RooArgList(par0,par1,par2))

    # Combine the models
    frac_gauss = RooRealVar("frac_gauss", "fraction of Gaussian", 0.2, 0.0, 1.0)
    frac_cb = RooRealVar("frac_cb", "fraction of crystal ball", 0.2, 0.0, 1.0)
    model = RooAddPdf("model", "DCB + Gaussian + Background", RooArgList(cb, gauss, background), RooArgList(frac_cb, frac_gauss))

    # Convert the histogram into a RooDataHist for RooFit
    data_hist = RooDataHist("data_hist", "Dataset", RooArgList(mass), histogram)

    # Fit the model to the data
    fit_result = model.fitTo(data_hist, RooFit.Save(), RooFit.Range(fit_range[0], fit_range[1]))

    # Combined sigma
    #csigma = (gaus_sigma.getVal()*frac_gauss.getVal() + sigma.getVal()*frac_cb.getVal())/(frac_cb.getVal() + frac_gauss.getVal())
    csigma = sigma.getVal()

    # Create a frame to plot the fit result
    frame = mass.frame(RooFit.Title("J/psi Mass Fit"))
    data_hist.plotOn(frame)
    model.plotOn(frame)
    model.plotOn(frame,RooFit.Name("cb"), RooFit.Components("cb"), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(kMagenta-7))
    model.plotOn(frame, RooFit.Components("background"), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(kGray))
    model.plotOn(frame, RooFit.Components("gauss"), RooFit.LineStyle(ROOT.kDashed), RooFit.LineColor(kOrange-3))

    # Set axis labels with an offset
    frame.SetXTitle("J/#psi mass [GeV]")
    frame.GetXaxis().SetTitleOffset(1.3)
    frame.SetYTitle("Events / 0.01 GeV / fb^{-1}")

    # Get Chi2 and normalize by ndof and number of bins
    chi2 = frame.chiSquare(fit_result.floatParsFinal().getSize())  # chi^2
    ndof = fit_result.floatParsFinal().getSize()  # Number of degrees of freedom
    nBins = histogram.GetNbinsX()  # Number of bins
    chi2_over_ndof = chi2 / (nBins - ndof)
    print("----------------------------------------")
    print("nBins = ", nBins)
    print("chi2_over_ndof = ", chi2_over_ndof)
    print("----------------------------------------")    

    # Define the signal range over which you want to integrate (e.g., around the J/psi mass peak)
    signal_range = fit_range  # Adjust this range depending on your specific signal region
    
    # Define the range in the observable (mass) to integrate
    mass.setRange("signal_region", signal_range[0], signal_range[1])
    
    # Integral for the total signal (CB + Gaussian)
    signal_integral = model.createIntegral(RooArgSet(mass), RooFit.NormSet(RooArgSet(mass)), RooFit.Range("signal_region"))    
    # Integral for the background component
    bkg_integral = background.createIntegral(RooArgSet(mass), RooFit.NormSet(RooArgSet(mass)), RooFit.Range("signal_region"))
    # Integral for the CB + Gaussian without the background
    signal_only_integral = signal_integral.getVal() - bkg_integral.getVal()    
    # Get the total number of events from the dataset (histogram)
    total_events = histogram.Integral()    
    # Number of signal events

    num_signal_events = signal_only_integral * total_events
    
    # Display the number of signal events
    print("----------------------------------------")
    print(f"TOTAL NUMBER OF EVENTS: {total_events}") 
    print(f"Number of signal events in the peak: {num_signal_events:.2f}")
    print("----------------------------------------")
    #latex.DrawLatexNDC(0.657, 0.70, f"Signal Integral = {sig_integral_val:.2f}")

    # Print fit result summary
    fit_result.Print()

    # Plotting
    histo, bins = getValues(histogram)
    y_err = histo**0.5
    xval = np.linspace(2.6, 3.6, 200)
    vbkg = []  
    vcb = []  
    vgaus = []  
    vmodel = []  
    model_integral_value = model.createIntegral(RooArgSet(mass)).getVal()
    bkg_integral_value = background.createIntegral(RooArgSet(mass)).getVal()
    gauss_integral_value = gauss.createIntegral(RooArgSet(mass)).getVal()
    cb_integral_value = cb.createIntegral(RooArgSet(mass)).getVal()
    binw = histogram.GetBinLowEdge(2)-histogram.GetBinLowEdge(1)
        

    for val in xval:
        mass.setVal(val)
        frac_bkg = 1.0 - frac_cb.getVal()-frac_gauss.getVal()
        vbkg.append(background.getVal()*histogram.Integral()*binw*(frac_bkg)/bkg_integral_value)
        vcb.append(cb.getVal()*histogram.Integral()*binw*frac_cb.getVal()/cb_integral_value)
        vgaus.append(gauss.getVal()*histogram.Integral()*binw*frac_gauss.getVal()/gauss_integral_value)
        vmodel.append(model.getVal()*histogram.Integral()*binw)

    #
    masses = []
    for i in range(0, len(bins)-1):
        masses.append(0.5*(bins[i] + bins[i+1]))
    plt.style.use(hep.style.CMS)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_ylabel(r'Events / 0.01 GeV', fontsize=24)
    ax.set_xlabel(r'Dimuon mass (GeV)', fontsize=24)
    ax.set_xlim(fit_range[0],fit_range[1])
    hep.cms.label("Preliminary", data=True, year='Run2024I', lumi=5.92, com='13.6')
    ax.set_ylim(0.0,1.2*max(histo))
    ax.errorbar(bins[:-1], histo, yerr=y_err, fmt='o', capsize=5, label='Data', color='k', markersize=8)
    ax.plot(xval, vbkg, label='Background', color='firebrick', lw = 3)
    ax.plot(xval, vgaus, label='Gaussian', color='deepskyblue', lw = 3)
    ax.plot(xval, vcb, label='Crystal Ball', color='violet', lw = 3)
    ax.plot(xval, vmodel, label='Signal + Background', color='slateblue', lw = 3)
    if 'L1' in name:
        ax.text(0.45, 0.95, 'L1' + name.split('L1')[1], fontsize=16, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    ax.text(0.45, 0.91, 'Signal / Total: %.1e / %.1e'%((frac_cb.getVal()+frac_gauss.getVal())*total_events, total_events), fontsize=15, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    ax.text(0.65, 0.8, 'Fit parameters:', fontsize=18, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    ax.text(0.65, 0.76, r'Mean = %.3f GeV'%(mean.getVal()), fontsize=18, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    #ax.text(0.65, 0.72, r'$\sigma_{gauss} =$ %.3f GeV'%(gaus_sigma.getVal()), fontsize=18, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    #ax.text(0.65, 0.68, r'$\sigma_{cb} = $ %.3f GeV'%(sigma.getVal()), fontsize=18, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    ax.text(0.65, 0.64, r'$\sigma_{comb} = $ %.3f%%'%(csigma/mean.getVal()*100.), fontsize=18, color='black', horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
    ax.legend(loc='upper left', fontsize = 18, frameon = True, ncol=1)
    fig.savefig('%s_fit.png'%(name), dpi=140)  

    return fit_result, model

# List of ROOT files
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_nanoCentra1000_Total/output_nanoCentra1000_Total_all.root")
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_DoubleMuon_NoVtx_v1_Total/output_DoubleMuon_NoVtx_v1_Total_all.root")
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_DoubleMuon_NoVtx_v1_ElisaBin_Total/output_DoubleMuon_NoVtx_v1_ElisaBin_Total_all.root")
#file.ls()
##h_24I = f_24I.Get("DiScoutingMuonNoVtx_mass_jpsi")
#names = []
#names.append("DiScoutingMuonNoVtx_mass_jpsiAll")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu_15_7")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu4p5er2p0_SQ_OS_Mass_X")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu8_SQ")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMuX_SQ_OS_dR_MaxY")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu0_UptX")
#
# Fit the histogram for 2024F
#for name in names:
#    histo = file.Get(name)
#    print(type(histo))
#    fit_result, model = fit_histogram_roofit(name, histo)
##
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_nanoCentral1000Single_Total/output_nanoCentral1000Single_Total_all.root")
#names = []
#names.append("DiScoutingMuonVtx_mass_jpsiAll")
#for name in names:
#    histo = file.Get(name)
#    print(type(histo))
#    fit_result, model = fit_histogram_roofit(name, histo)
##
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_ZeroBias_Vtx_Total/output_ZeroBias_Vtx_Total_all.root")
#names = []
#names.append("DiScoutingMuonVtx_mass_jpsiAll")
#for name in names:
#    histo = file.Get(name)
#    print(type(histo))
#    fit_result, model = fit_histogram_roofit('ZeroBias'+name, histo)
#
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_ZeroBias_Vtx_v1_Total/output_ZeroBias_Vtx_v1_Total_all.root")
#names = []
#names.append("DiScoutingMuonVtx_mass_jpsiAll")
#for name in names:
#    histo = file.Get(name)
#    print(type(histo))
#    fit_result, model = fit_histogram_roofit('ZeroBias'+name, histo)
##
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_ZeroBias_NoVtx_v1_Total/output_ZeroBias_NoVtx_v1_Total_all.root")
#names = []
#names.append("DiScoutingMuonNoVtx_mass_jpsiAll")
#for name in names:
#    histo = file.Get(name)
#    print(type(histo))
#    fit_result, model = fit_histogram_roofit('ZeroBias'+name, histo, (2.8,3.4))
#
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_DoubleMuon_NoVtx_v1_ElisaBin_Total/output_DoubleMuon_NoVtx_v1_ElisaBin_Total_all.root")
file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_ZeroBias_NoVtx_v1_Definite_Total/output_ZeroBias_NoVtx_v1_Definite_Total_all.root")
names = []
names.append("DiScoutingMuonNoVtx_mass_jpsiAll")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu_15_7")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu4p5er2p0_SQ_OS_Mass_X")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu8_SQ")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMuX_SQ_OS_dR_MaxY")
#names.append("DiScoutingMuonNoVtx_mass_jpsiL1_DoubleMu0_UptX")
for name in names:
    histo = file.Get(name)
    print(type(histo))
    fit_result, model = fit_histogram_roofit('ZeroBias_Vtx_'+name, histo, (2.8,3.4))
#
#file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_SingleMuon_NoVtx_v1_ElisaBin_Total/output_SingleMuon_NoVtx_v1_ElisaBin_Total_all.root")
file = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_ZeroBias_Vtx_v1_Definite_Total/output_ZeroBias_Vtx_v1_Definite_Total_all.root")
names = []
names.append("DiScoutingMuonVtx_mass_jpsiAll")
for name in names:
    histo = file.Get(name)
    print(type(histo))
    fit_result, model = fit_histogram_roofit('ZeroBias_NoVtx'+name, histo, (2.8,3.4))
#


