#!/bin/env python3                                                                                                                                               
import ROOT, array, random, copy                                                                                                    
from ROOT import TCanvas, TFile, TH1, TH1F, TF1, gSystem                                                                                        
import ROOT, array, random, copy                                                                                        
from ROOT import RooCmdArg, RooArgSet, kFALSE, RooLinkedList, kBlue, kRed, kBlack, kOpenStar, kWhite, kGray                                    
from ROOT import gStyle, TStyle, TGraph, TGraphErrors, TMath, TMultiGraph, TLine, gPad, TGaxis, TLegend, TText, TLatex, TColor, TPaveText      
from ROOT import TAttFill, TLegend, TRatioPlot, TPad, THStack, TFileCollection                                                      
from ROOT import kBlue, kRed, kBlack, kWhite, kAzure, kOrange, kPink, kGreen, kYellow, kCyan, kMagenta                                         
from ROOT import RooRealVar, RooDataHist, RooCBShape, RooGaussian, RooExponential, RooAddPdf, RooFit, RooArgList, RooPolynomial
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

def fit_histogram_roofit(histogram, fit_range=(2.6, 3.6)):
    # Define observable: mass
    mass = RooRealVar("mass", "J/#psi Mass [GeV]", fit_range[0], fit_range[1])

    # Double Crystal Ball parameters
    mean = RooRealVar("mean", "mean of crystal ball", 3.1, 2.9, 3.2)
    sigma = RooRealVar("sigma", "width of crystal ball", 0.1, 0.0005, 0.2)
    alpha = RooRealVar("alpha", "low side alpha", 10, -10, 50.0)
    n = RooRealVar("n", "low side n", 5.0, -5, 5.0)

    # Double Crystal Ball components
    cb = RooCBShape("cb", "cb", mass, mean, sigma, alpha, n)

    # Gaussian parameters
    gaus_mean = RooRealVar("gaus_mean", "mean of Gaussian", 3.1, 2.9, 3.2)
    gaus_sigma = RooRealVar("gaus_sigma", "width of Gaussian", 0.05, 0.001, 0.1)
    gauss = RooGaussian("gauss", "gauss", mass, gaus_mean, gaus_sigma)

    # Background exponential
    #expo_slope  = RooRealVar("expo_slope","expo_slope",-0.02,-20.0,20.0);
    #background = RooExponential("background_exponential", "background_exponential",mass,expo_slope);
    b0 = RooRealVar("b0", "constant term", 1.0, 0.0, 10.0)
    b1 = RooRealVar("b1", "linear term", 0.0, -1.0, 1.0)
    background = RooPolynomial("background", "background", mass, RooArgList(b0, b1))

    # Combine the models
    frac_gauss = RooRealVar("frac_gauss", "fraction of Gaussian", 0.5, 0.0, 1.0)
    frac_cb = RooRealVar("frac_cb", "fraction of crystal ball", 0.1, 0.0, 1.0)
    model = RooAddPdf("model", "DCB + Gaussian + Background", RooArgList(cb, gauss, background), RooArgList(frac_cb, frac_gauss))

    # Convert the histogram into a RooDataHist for RooFit
    data_hist = RooDataHist("data_hist", "Dataset", RooArgList(mass), histogram)

    # Fit the model to the data
    fit_result = model.fitTo(data_hist, RooFit.Save(), RooFit.Range(fit_range[0], fit_range[1]))

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
    signal_range = (2.6, 3.6)  # Adjust this range depending on your specific signal region
    
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
    plt.style.use(hep.style.CMS)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_ylabel(r'Events / 0.01 GeV', fontsize=24)
    ax.set_xlabel(r'Dimuon mass (GeV)', fontsize=24)
    ax.set_xlim(2.6,3.6)
    hep.cms.label("Preliminary", data=True, lumi=1, year=2024, com='13.6')
    ax.errorbar(bins[:-1], histo, yerr=y_err, fmt='o', capsize=5, label='Data', color='k', markersize=8)
    ax.plot(xval, vbkg, label='Background', color='firebrick', lw = 3)
    ax.plot(xval, vgaus, label='Gaussian', color='deepskyblue', lw = 3)
    ax.plot(xval, vcb, label='Crystal Ball', color='violet', lw = 3)
    ax.plot(xval, vmodel, label='Signal + Background', color='slateblue', lw = 3)
    ax.legend(loc='upper left', fontsize = 18, frameon = True, ncol=1)
    fig.savefig('fit.png', dpi=140)  

    return fit_result, model

# List of ROOT files
f_24I = ROOT.TFile.Open("/eos/user/f/fernance/DST-Muons/ScoutingOutput_tag_Total/output_tag_Total_0.root")
f_24I.ls()
h_24I = f_24I.Get("DiScoutingMuonNoVtx_mass_jpsi")

# Fit the histogram for 2024F
fit_result_24F, model_24F = fit_histogram_roofit(h_24I)
