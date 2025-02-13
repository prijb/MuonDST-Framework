import ROOT as r
from ROOT import gDirectory, gROOT, gStyle, TLatex
import optparse
import os
import copy
from matplotlib.colors import LogNorm

def getObject(filename, key):

    _f = r.TFile(filename)
    _h = _f.Get(key)
    _hcopy = copy.deepcopy(_h)
    _f.Close()

    return _hcopy


def plotSimpleEfficiency(eff, output, option = 'AP', extralabel = ''):

    c1 = r.TCanvas("c1", "", 700, 600)
    c1.cd()
    eff.Draw(option)

    # CMS logo
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.055);
    latex.DrawLatex(0.13, 0.93, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.04);
    latexb.DrawLatex(0.23, 0.93, "#it{Internal}")

    latexe = TLatex()
    latexe.SetNDC();
    latexe.SetTextAngle(0);
    latexe.SetTextColor(r.kBlack);
    latexe.SetTextFont(42);
    latexe.SetTextAlign(31);
    latexe.SetTextSize(0.04);
    latexe.DrawLatex(0.9, 0.93, extralabel)

    if output[-1] != '/': output = output + '/'
    c1.SaveAs(output + eff.GetName()+'.png')


### Function to plot several histograms
def plotSimple(name, histos_, output, option = 'HIST', ylog = False, xlog = False, rebin = False, maxDigits = False, extralabel = '', labels = [], fromRDF = False):

    colors = [r.kCyan-2, r.kOrange+1, r.kGray+2]
    colors = [r.kBlack,
             r.TColor.GetColor('#448aff'),
             r.TColor.GetColor('#1565c0'),
             r.TColor.GetColor('#009688'),
             r.TColor.GetColor('#8bc34a'),
             r.TColor.GetColor('#ffc107'),
             r.TColor.GetColor('#ff9800'),
             r.TColor.GetColor('#f44336'),
             r.TColor.GetColor('#ad1457'),
             r.TColor.GetColor('#9d4edd')]

    colors = [r.kBlack,
             r.TColor.GetColor('#ff7073'),
             r.TColor.GetColor('#ea9e8d'),
             r.TColor.GetColor('#dbb3b1'),
             r.TColor.GetColor('#ffe085'),
             r.TColor.GetColor('#fed35d'),
             r.TColor.GetColor('#96e6b3'),
             r.TColor.GetColor('#73d3c9'),
             r.TColor.GetColor('#8cd9f8'),
             r.TColor.GetColor('#a0b7cf')]

    # Make the plot bonito
    histos = []
    for h,histo_ in enumerate(histos_):
        if fromRDF:
            histo = copy.deepcopy(histo_.DrawCopy())
        else:
            histo = copy.deepcopy(histo_)
        histo.Sumw2()
        histo.GetXaxis().SetTitleSize(0.045)
        histo.GetYaxis().SetTitleSize(0.045)
        if maxDigits:
            histo.GetXaxis().SetMaxDigits(maxDigits)
            histo.GetYaxis().SetMaxDigits(maxDigits)

        histo.SetLineColor(colors[h])
        histo.SetLineWidth(2)
        histos.append(histo)

    c1 = r.TCanvas("c1", "", 700, 600)
    c1.cd()

    if ylog:
        histos[0].SetMaximum(1000*histos[0].GetMaximum())
        histos[0].SetMinimum(10)
        c1.SetLogy(1)
    else:
        histos[0].SetMaximum(1.4*histos[0].GetMaximum())
        histos[0].SetMinimum(0.0)
    if xlog:
        c1.SetLogx(1)

    for h,histo in enumerate(histos):
        if not h:
            histo.Draw(option)
        else:
            histo.Draw(option+', SAME')

    legend = r.TLegend(0.15, 0.64, 0.8, 0.87)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.025)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    for h,histo in enumerate(histos):
        legend.AddEntry(histo, labels[h], 'l')
    legend.Draw()

    # CMS logo
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.055);
    if maxDigits:
        latex.DrawLatex(0.23, 0.93, "#bf{CMS}")
    else:
        latex.DrawLatex(0.13, 0.93, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.042);
    if maxDigits:
        latexb.DrawLatex(0.33, 0.93, "#it{Preliminary}")
    else:
        latexb.DrawLatex(0.23, 0.93, "#it{Preliminary}")

    latexe = TLatex()
    latexe.SetNDC();
    latexe.SetTextAngle(0);
    latexe.SetTextColor(r.kBlack);
    latexe.SetTextFont(42);
    latexe.SetTextAlign(31);
    latexe.SetTextSize(0.037);
    latexe.DrawLatex(0.9, 0.93, extralabel)

    if output[-1] != '/': output = output + '/'
    c1.SaveAs(output + name +'.png')


def plotComparison(name, tree_new, tree_ref, var, cut, nbin, xmin, xmax, label = ''):

    histo_new = r.TH1F(name + "_new", "", nbin, xmin, xmax)
    histo_ref = r.TH1F(name + "_ref", "", nbin, xmin, xmax)
    histo_new.Sumw2()
    histo_ref.Sumw2()
    tree_ref.Project(histo_ref.GetName(), var, cut, "")
    tree_new.Project(histo_new.GetName(), var, cut, "")
    histo_sub = histo_new.Clone(name + "_sub")
    histo_sub.Add(histo_ref, -1)

    ## Tune histos
    histo_ref.SetMarkerSize(1)
    histo_ref.SetMarkerStyle(20)
    histo_ref.SetLineWidth(2)
    histo_ref.SetLineColor(r.kBlack)
    histo_ref.SetMarkerColor(r.kBlack)
    histo_ref.GetYaxis().SetTitleSize(0.045)
    histo_ref.GetYaxis().SetLabelSize(0.045)
    histo_ref.GetXaxis().SetLabelSize(0.045)
    histo_ref.GetXaxis().SetTitle(var)
    histo_ref.GetYaxis().SetTitle('Counts')
    histo_ref.SetMinimum(histo_sub.GetMinimum())

    histo_new.SetMarkerSize(1)
    histo_new.SetMarkerStyle(24)
    histo_new.SetMarkerColor(r.kRed)
    histo_new.SetLineColor(r.kRed)
    histo_new.SetLineWidth(2)
    histo_new.GetYaxis().SetLabelSize(0.045)

    histo_sub.SetMarkerSize(1)
    histo_sub.SetMarkerStyle(20)
    histo_sub.SetLineWidth(2)
    histo_sub.SetLineColor(r.kBlue)
    histo_sub.SetMarkerColor(r.kBlue)
    histo_sub.GetYaxis().SetTitleSize(0.045)

    ## Legend
    legend = r.TLegend(0.55, 0.76, 0.8, 0.87)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.035)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    legend.AddEntry(histo_ref, 'Reference', 'l')
    legend.AddEntry(histo_new, 'New', 'pl')
    legend.AddEntry(histo_sub, 'New - Reference', 'l')

    ## Zero line
    line = r.TLine(xmin, 0, xmax, 0)
    line.SetLineColor(r.kGray+2)
    line.SetLineWidth(2)
    line.SetLineStyle(7)

    ## Plot histos
    c1 = r.TCanvas("c1", "", 700, 600)
    c1.cd()
    #c1.SetLogy(1)

    histo_ref.Draw("HIST")
    line.Draw("SAME")
    histo_new.Draw("P, SAMES")
    histo_sub.Draw("HIST,SAME")
    legend.Draw()

    ## CMS logo
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.065);
    latex.DrawLatex(0.17, 0.83, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.042);
    latexb.DrawLatex(0.17, 0.78, "#it{Internal}")

    uplabel = TLatex()
    uplabel.SetNDC();
    uplabel.SetTextAngle(0);
    uplabel.SetTextColor(r.kBlack);
    uplabel.SetTextFont(42);
    uplabel.SetTextAlign(11);
    uplabel.SetTextSize(0.032);
    uplabel.DrawLatex(0.13, 0.93, label)


    c1.SaveAs('tupleplots/' + name + '.png')


def plotComparisonRatio(name, tree_new, tree_ref, var, cut, nbin, xmin, xmax, label = '', output = 'ratiotuples', ylog = False):

    histo_new = r.TH1F(name + "_new", "", nbin, xmin, xmax)
    histo_ref = r.TH1F(name + "_ref", "", nbin, xmin, xmax)
    histo_new.Sumw2()
    histo_ref.Sumw2()
    tree_ref.Project(histo_ref.GetName(), var, cut, "")
    tree_new.Project(histo_new.GetName(), var, cut, "")
    histo_sub = histo_new.Clone(name + "_sub")
    histo_sub.Add(histo_ref, -1)

    ## Tune histos
    histo_ref.SetMarkerSize(1)
    histo_ref.SetMarkerStyle(20)
    histo_ref.SetLineWidth(2)
    histo_ref.SetLineColor(r.kBlack)
    histo_ref.SetMarkerColor(r.kBlack)
    histo_ref.GetYaxis().SetTitleSize(0.045)
    histo_ref.GetYaxis().SetLabelSize(0.045)
    histo_ref.GetXaxis().SetLabelSize(0)
    histo_ref.GetXaxis().SetTitle(var)
    histo_ref.GetYaxis().SetTitle('Counts')

    histo_new.SetMarkerSize(1)
    histo_new.SetMarkerStyle(24)
    histo_new.SetMarkerColor(r.kRed)
    histo_new.SetLineColor(r.kRed)
    histo_new.SetLineWidth(2)
    histo_new.GetYaxis().SetLabelSize(0.045)

    histo_sub.SetMarkerSize(1)
    histo_sub.SetMarkerStyle(20)
    histo_sub.SetLineWidth(2)
    histo_sub.SetLineColor(r.kBlue)
    histo_sub.SetMarkerColor(r.kBlue)
    histo_sub.GetYaxis().SetTitleSize(0.14)
    histo_sub.GetXaxis().SetTitleSize(0.14)
    histo_sub.GetYaxis().SetLabelSize(0.14)
    histo_sub.GetXaxis().SetLabelSize(0.14)
    histo_sub.GetXaxis().SetTitle(var)
    histo_sub.GetYaxis().SetTitle('New - Ref')
    histo_sub.GetYaxis().CenterTitle()
    histo_sub.GetYaxis().SetTitleOffset(0.45)
    histo_sub.GetXaxis().SetTitleOffset(1.0)

    c1 = r.TCanvas("c1", "", 550, 600)
    c1.cd()

    pad1 = r.TPad("pad1", "pad1", 0, 0.25, 1, 1.0)
    pad1.SetBottomMargin(0.03)
    if ylog:
        pad1.SetLogy(1)
    pad1.Draw()

    ### pad 2 drawing
    r.gStyle.SetOptStat(0)
    pad2 = r.TPad("pad2", "pad2", 0, 0.0, 1, 0.25)
    pad2.SetTopMargin(0.0);
    pad2.SetBottomMargin(0.30);
    pad2.Draw();

    ### pad 1 drawing
    pad1.cd()
    histo_ref.Draw("HIST")
    histo_new.Draw("P, SAMES")
     

    legend = r.TLegend(0.5, 0.76, 0.8, 0.87)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.035)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    legend.AddEntry(histo_ref, 'Reference', 'l')
    legend.AddEntry(histo_new, 'New', 'pl')
    legend.AddEntry(histo_sub, 'New - Reference', 'l')
    legend.Draw()


    ### pad2 drawing
    pad2.cd()
    histo_sub.Draw("HIST,SAME")
    line = r.TLine(xmin, 0, xmax, 0)
    line.SetLineColor(r.kGray+2)
    line.SetLineWidth(2)
    line.SetLineStyle(7)
    line.Draw("Same")


    ## CMS logo
    pad1.cd()
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.065);
    latex.DrawLatex(0.17, 0.83, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.042);
    latexb.DrawLatex(0.17, 0.78, "#it{Internal}")

    uplabel = TLatex()
    uplabel.SetNDC();
    uplabel.SetTextAngle(0);
    uplabel.SetTextColor(r.kBlack);
    uplabel.SetTextFont(42);
    uplabel.SetTextAlign(11);
    uplabel.SetTextSize(0.035);
    uplabel.DrawLatex(0.13, 0.93, label)

    ## Save the plot
    if output[-1] != '/': output = output + '/'
    c1.SaveAs(output + name +'.png')



def plot2D(histo, output, zlog = False, rebin = False, maxDigits = False):

    histo.Sumw2()

    # Make the plot bonito
    histo.GetXaxis().SetTitleSize(0.045)
    histo.GetYaxis().SetTitleSize(0.045)
    if maxDigits:
        histo.GetXaxis().SetMaxDigits(maxDigits)
        histo.GetYaxis().SetMaxDigits(maxDigits)


    c1 = r.TCanvas("c1", "", 600, 600)
    c1.cd()

    if zlog:
        c1.SetLogz(1)

    histo.Draw('COLZ')



    # CMS logo
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.055);
    if maxDigits:
        latex.DrawLatex(0.23, 0.93, "#bf{CMS}")
    else:
        latex.DrawLatex(0.13, 0.93, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.04);
    if maxDigits:
        latexb.DrawLatex(0.35, 0.93, "#it{Internal}")
    else:
        latexb.DrawLatex(0.25, 0.93, "#it{Internal}")
    


    if output[-1] != '/': output = output + '/'
    c1.SaveAs(output + histo.GetName()+'.png')


def plotValidation(name, target, reference, output, tlabel, rlabel, relval, ylog = False, rebin = False):

    target.Sumw2()
    reference.Sumw2()

    if rebin:
        target.Rebin(rebin)
        reference.Rebin(rebin)

    target.SetMarkerSize(1)
    target.SetMarkerStyle(24)
    target.SetMarkerColor(r.kBlue)
    target.SetLineColor(r.kBlue)
    target.SetLineWidth(2)
    target.GetYaxis().SetLabelSize(0.045)

    reference.SetMarkerSize(1)
    reference.SetMarkerStyle(20)
    reference.SetLineWidth(2)
    reference.SetLineColor(r.kBlack)
    reference.SetMarkerColor(r.kBlack)
    reference.GetYaxis().SetTitleSize(0.045)
    reference.GetYaxis().SetLabelSize(0.045)
    reference.GetXaxis().SetLabelSize(0)
    #reference.GetXaxis().SetTitle(reference.GetTitle())

    ratio = target.Clone(target.GetName() + '_ratio')
    ratio.Reset()
    for n in range(1, target.GetNbinsX() + 1):
        tv = target.GetBinContent(n)
        rv = reference.GetBinContent(n)
        te = target.GetBinError(n)
        re = reference.GetBinError(n)
        if tv != 0.0 and rv != 0.0:
            value = tv/rv
            error = value * ( (te/tv)**2 + (re/rv)**2 )**0.5
        else:
            value = 0.0
            error = 0.0
        ratio.SetBinContent(n, value)
        ratio.SetBinError(n, error)


    ratio.SetTitle(";"+reference.GetXaxis().GetTitle()+";Ratio")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleOffset(0.4)
    ratio.GetYaxis().SetTitleSize(0.14)
    ratio.GetYaxis().SetLabelSize(0.14)
    ratio.GetXaxis().SetLabelSize(0.14)
    ratio.GetXaxis().SetTitleSize(0.14)
    ratio.SetMarkerColor(r.kRed)
    ratio.SetLineColor(r.kRed)
    ratio.SetLineWidth(2)
    ratio.SetFillColor(r.kRed)
    ratio.SetMarkerStyle(20)
    ratio.Sumw2()

    target.SetTitle(';;')
    reference.SetTitle(';;Counts')
    ymax = max([target.GetMaximum(), reference.GetMaximum()])
    if not ylog:
        reference.SetMaximum(1.4*ymax)
        reference.SetMinimum(0.0)
    else:
        reference.SetMaximum(100.*ymax)
        reference.SetMinimum(0.1)

    c1 = r.TCanvas("c1", "", 550, 600)
    c1.cd()

    pad1 = r.TPad("pad1", "pad1", 0, 0.25, 1, 1.0)
    pad1.SetBottomMargin(0.03)
    if ylog:
        pad1.SetLogy(1)
    pad1.Draw()

    ### pad 2 drawing
    r.gStyle.SetOptStat(0)
    pad2 = r.TPad("pad2", "pad2", 0, 0.0, 1, 0.25)
    pad2.SetTopMargin(0.0);
    pad2.SetBottomMargin(0.30);
    pad2.Draw();

    ### pad 1 drawing
    pad1.cd()
    reference.Draw('P')
    target.Draw('P SAMES')

    legend = r.TLegend(0.35, 0.76, 0.7, 0.87)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.035)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    legend.AddEntry(reference, rlabel + " ({0})".format(int(reference.GetEntries())), 'pl')
    legend.AddEntry(target, tlabel + " ({0})".format(int(target.GetEntries())), 'pl')
    legend.Draw()


    ### pad2 drawing
    pad2.cd()
    ratio.Draw("P,SAME")
    line = r.TLine(ratio.GetBinLowEdge(1), 1, ratio.GetBinLowEdge(ratio.GetNbinsX()+1), 1)
    line.Draw("Same")


    ### RelVal text
    pad1.cd()
    rvlabel = r.TLatex()
    rvlabel.SetNDC()
    rvlabel.SetTextAngle(0)
    rvlabel.SetTextColor(r.kBlack)
    rvlabel.SetTextFont(42)
    rvlabel.SetTextAlign(31)
    rvlabel.SetTextSize(0.035)
    if relval:
        rvlabel.DrawLatex(0.88, 0.935, relval)

    ## CMS logo
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.065);
    latex.DrawLatex(0.17, 0.83, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.042);
    latexb.DrawLatex(0.17, 0.78, "#it{Internal}")

    ## Save the plot
    if output[-1] != '/': output = output + '/'
    c1.SaveAs(output + name +'.png')


## Plot efficiency with validation style
def plotEfficiency(name, target, reference, output, tlabel, rlabel, relval, ylog = False, rebin = False):

    target.SetMarkerSize(1)
    target.SetMarkerStyle(24)
    target.SetMarkerColor(r.kBlue)
    target.SetLineColor(r.kBlue)
    target.SetLineWidth(2)

    reference.SetMarkerSize(1)
    reference.SetMarkerStyle(20)
    reference.SetLineWidth(2)
    reference.SetLineColor(r.kBlack)
    reference.SetMarkerColor(r.kBlack)

    tmp_num = target.GetTotalHistogram().Clone()
    tmp_den = reference.GetTotalHistogram().Clone()
    for n in range(0,tmp_num.GetNbinsX()):
        tmp_den.SetBinContent(n+1, reference.GetEfficiency(n+1))
        tmp_num.SetBinContent(n+1, target.GetEfficiency(n+1))
        tmp_den.SetBinError(n+1, reference.GetEfficiencyErrorLow(n+1))
        tmp_num.SetBinError(n+1, target.GetEfficiencyErrorLow(n+1))
    ratio = tmp_num.Clone(name+'_ratio')
    ratio.Divide(tmp_den) 

    ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleOffset(0.4)
    ratio.GetYaxis().SetTitleSize(0.14)
    ratio.GetYaxis().SetLabelSize(0.14)
    ratio.GetXaxis().SetLabelSize(0.14)
    ratio.GetXaxis().SetTitleSize(0.14)
    ratio.SetMarkerColor(r.kRed)
    ratio.SetLineColor(r.kRed)
    ratio.SetLineWidth(2)
    ratio.SetMarkerStyle(20)
    ratio.Sumw2()

    # Canvas
    c1 = r.TCanvas("c1", "", 550, 600)
    c1.cd()

    # Pads
    pad1 = r.TPad("pad1", "pad1", 0, 0.25, 1, 1.0)
    pad1.SetBottomMargin(0.03)
    if ylog:
        pad1.SetLogy(1)
    pad1.Draw()

    # Pad 2 drawing
    r.gStyle.SetOptStat(0)
    pad2 = r.TPad("pad2", "pad2", 0, 0.0, 1, 0.25)
    pad2.SetTopMargin(0.0);
    pad2.SetBottomMargin(0.30);
    pad2.Draw();

    # Pad 1 drawing
    _h = r.TH1F("h", ";;Efficiency", 1, tmp_num.GetBinLowEdge(1), tmp_num.GetBinLowEdge(tmp_num.GetNbinsX()) + tmp_num.GetBinWidth(tmp_num.GetNbinsX()))
    _h.SetMinimum(0.0)
    _h.SetMaximum(1.25)
    _h.GetYaxis().SetTitleSize(0.045)
    _h.GetYaxis().SetTitle(tmp_num.GetYaxis().GetTitle())
    _h.GetYaxis().SetLabelSize(0.045)
    _h.GetXaxis().SetLabelSize(0)
    pad1.cd()
    _h.Draw("AXIS")
    reference.Draw('P, SAME')
    target.Draw('P, SAME')

    legend = r.TLegend(0.35, 0.76, 0.7, 0.87)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.035)
    legend.SetLineWidth(0)
    legend.SetBorderSize(0)
    legend.AddEntry(reference, rlabel, 'pl')
    legend.AddEntry(target, tlabel, 'pl')
    legend.Draw()


    # Pad 2 final drawing
    pad2.cd()
    #ratio.SetMinimum(0.9)
    #ratio.SetMaximum(1.1)
    ratio.Draw("P")
    line = r.TLine(ratio.GetBinLowEdge(1), 1, ratio.GetBinLowEdge(ratio.GetNbinsX()+1), 1)
    line.Draw("Same")


    # Reference text
    pad1.cd()
    rvlabel = r.TLatex()
    rvlabel.SetNDC()
    rvlabel.SetTextAngle(0)
    rvlabel.SetTextColor(r.kBlack)
    rvlabel.SetTextFont(42)
    rvlabel.SetTextAlign(31)
    rvlabel.SetTextSize(0.035)
    rvlabel.DrawLatex(0.85, 0.935, relval)

    # CMS logo
    latex = TLatex()
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(r.kBlack);
    latex.SetTextFont(42);
    latex.SetTextAlign(11);
    latex.SetTextSize(0.065);
    latex.DrawLatex(0.17, 0.83, "#bf{CMS}")

    latexb = TLatex()
    latexb.SetNDC();
    latexb.SetTextAngle(0);
    latexb.SetTextColor(r.kBlack);
    latexb.SetTextFont(42);
    latexb.SetTextAlign(11);
    latexb.SetTextSize(0.042);
    latexb.DrawLatex(0.17, 0.78, "#it{Internal}")

    ## Save the plot
    if output[-1] != '/': output = output + '/'
    c1.SaveAs(output + name +'.png')

   
## Plot efficiency with validation style
def plotEfficiencyV2(name, target, reference, output, tlabel, rlabel, relval, ylog = False, rebin = False):

    target.SetMarkerSize(0.7)
    target.SetMarkerStyle(8)
    target.SetMarkerColor(r.kOrange+1)
    target.SetLineColor(r.kOrange+1)
    target.SetFillColorAlpha(r.kOrange+1, 0.3)
    target.SetLineWidth(1)

    reference.SetMarkerSize(0.7)
    reference.SetMarkerStyle(8)
    reference.SetLineWidth(1)
    reference.SetLineColor(r.kCyan-2)
    reference.SetFillColorAlpha(r.kCyan-2, 0.3)
    reference.SetMarkerColor(r.kCyan-2)

    tmp_num = target.GetTotalHistogram().Clone()
    tmp_den = reference.GetTotalHistogram().Clone()
    for n in range(0,tmp_num.GetNbinsX()):
        tmp_den.SetBinContent(n+1, reference.GetEfficiency(n+1))
        tmp_num.SetBinContent(n+1, target.GetEfficiency(n+1))
        tmp_den.SetBinError(n+1, reference.GetEfficiencyErrorLow(n+1))
        tmp_num.SetBinError(n+1, target.GetEfficiencyErrorLow(n+1))
    ratio = tmp_num.Clone(name+'_ratio')
    ratio.Divide(tmp_den)

    ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetTitleOffset(0.4)
    ratio.GetYaxis().SetTitleSize(0.14)
    ratio.GetYaxis().SetLabelSize(0.14)
    ratio.GetXaxis().SetLabelSize(0.14)
    ratio.GetXaxis().SetTitleSize(0.14)
    ratio.SetMarkerColor(r.kBlack)
    ratio.SetLineColor(r.kBlack)
    ratio.SetLineWidth(2)
    ratio.SetMarkerStyle(8)
    ratio.SetMarkerSize(0.7)
    ratio.Sumw2()

    # Canvas
    c1 = r.TCanvas("c1", "", 550, 600)
    c1.cd()

    # Pads
    pad1 = r.TPad("pad1", "pad1", 0, 0.25, 1, 1.0)
    pad1.SetBottomMargin(0.03)

##
## mplhep tools
##
import mplhep as hep
import matplotlib.pyplot as plt
import numpy as np

colors = [ 'tab:'+c for c in ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']]

def getValues(histo):
    values = []
    bins = []
    for n in range(1, histo.GetNbinsX()+1):
        values.append(histo.GetBinContent(n))
        bins.append(histo.GetBinLowEdge(n))
    bins.append(histo.GetBinLowEdge(n) + histo.GetBinWidth(n))
    return np.array(values), np.array(bins)

def get2DValues(histo):
    nbins_x = histo.GetNbinsX()
    nbins_y = histo.GetNbinsY()
    values = np.zeros((nbins_x, nbins_y))
    x_edges = np.zeros(nbins_x + 1)
    y_edges = np.zeros(nbins_y + 1)
    for i in range(1, nbins_x + 1):
        for j in range(1, nbins_y + 1):
            values[i-1,j-1] = histo.GetBinContent(i,j)
    for i in range(1, nbins_x+1):
        x_edges[i-1] = histo.GetXaxis().GetBinLowEdge(i)
    for j in range(1, nbins_y+1):
        y_edges[j-1] = histo.GetYaxis().GetBinLowEdge(j)
    x_edges[-1] = histo.GetXaxis().GetBinUpEdge(nbins_x)
    y_edges[-1] = histo.GetYaxis().GetBinUpEdge(nbins_y)
    return values, x_edges, y_edges

def get2DEfficiencies(efficiency):
    histo = efficiency.GetTotalHistogram()
    nbins_x = histo.GetNbinsX()
    nbins_y = histo.GetNbinsY()
    values = np.zeros((nbins_x, nbins_y))
    x_edges = np.zeros(nbins_x + 1)
    y_edges = np.zeros(nbins_y + 1)
    for i in range(1, nbins_x + 1):
        for j in range(1, nbins_y + 1):
            values[i-1,j-1] = efficiency.GetEfficiency(efficiency.GetGlobalBin(i, j))
    for i in range(1, nbins_x+1):
        x_edges[i-1] = histo.GetXaxis().GetBinLowEdge(i)
    for j in range(1, nbins_y+1):
        y_edges[j-1] = histo.GetYaxis().GetBinLowEdge(j)
    x_edges[-1] = histo.GetXaxis().GetBinUpEdge(nbins_x)
    y_edges[-1] = histo.GetYaxis().GetBinUpEdge(nbins_y)
    return values, x_edges, y_edges

def getEfficiencyValues(eff):
    values = []
    lowerr = []
    uperr = []
    points = []
    histo = eff.GetTotalHistogram()
    for n in range(1, histo.GetNbinsX()+1):
        values.append(eff.GetEfficiency(n))
        lowerr.append(eff.GetEfficiencyErrorLow(n))
        uperr.append(eff.GetEfficiencyErrorUp(n))
        points.append(histo.GetBinLowEdge(n) + 0.5*histo.GetBinWidth(n))
    return np.array(values), np.array(points), np.array(lowerr), np.array(uperr)

def plotEfficiencyHEP(name, efficiency, output, label, xaxis = '', yaxis='', ylog = False, rebin = False):
    plt.style.use(hep.style.CMS)
    fig, ax = plt.subplots(figsize=(10, 8))
    hep.cms.label("Preliminary", data=True, year='2024', com='13.6', ax=ax)
    ax.set_xlabel(xaxis, fontsize=24)
    ax.set_ylabel(yaxis, fontsize=24)
    ax.set_ylim(0.0, 1.2)
    es_, ps_, ls_, us_ = getEfficiencyValues(efficiency)
    ax.errorbar(ps_, es_, yerr=[ls_,us_], xerr=0.5*(ps_[1]-ps_[0]), fmt='o', capsize=5, label=label, color='tab:blue', markersize=8)
    ax.legend(loc='upper left', fontsize = 18, frameon = True, ncol=1)
    fig.savefig('%s/%s.png'%(output,name), dpi=140)

def plotEfficiencyComparisonHEP(name, efficiencies, output, labels, xaxis = '', yaxis='', ylog = False, rebin = False):
    plt.style.use(hep.style.CMS)
    fig, (ax, ax_ratio) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1], 'hspace': 0.05}, sharex=True, figsize=(10, 10))
    hep.cms.label("Preliminary", data=False, year='2024', com='13.6', ax=ax)
    ax.set_xlabel('')
    ax_ratio.set_xlabel(xaxis, fontsize=24)
    ax.set_ylabel(yaxis, fontsize=24)
    ax_ratio.set_ylabel('Ratio', fontsize=24)
    ax.set_ylim(0.0, 1.2)
    es0_, ps0_, ls0_, us0_ = getEfficiencyValues(efficiencies[0])
    for e,eff in enumerate(efficiencies):
        es_, ps_, ls_, us_ = getEfficiencyValues(eff)
        ax.errorbar(ps_, es_, yerr=[ls_,us_], xerr=0.5*(ps_[1]-ps_[0]), fmt='o', capsize=5, label=labels[e], color=colors[e], markersize=8)
        if e>0 and e==1:
            err0 = [ls0_[x] if es0_[x] > es_[x] else us0_[x] for x in range(0, len(es0_))]
            err1 = [ls_[x] if es_[x] > es0_[x] else us_[x] for x in range(0, len(es_))]
            err = es_/es0_*((err0/es0_)**2 + (err1/es_)**2)
            ax_ratio.errorbar(ps_, es_/es0_, yerr=err, xerr=0.5*(ps_[1]-ps_[0]), fmt='o', capsize=5, label=labels[e], color='k', markersize=8)
    ax.legend(loc='upper left', fontsize = 18, frameon = True, ncol=1)
    fig.savefig('%s/%s_fit.png'%(output,name), dpi=140)
    
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
    
    
def plotHistogram2D(name, histo, label, output, xaxis = '', yaxis='', year='X', lumi=''):    
    values, x_edges, y_edges = get2DValues(histo)
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(
        values.T, 
        extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
        origin='lower',
        cmap="viridis",
        norm=LogNorm(vmin=np.min(values[values > 0]), vmax=np.max(values))
    )
    cbar = fig.colorbar(im, ax=ax, pad=0.01)
    cbar.set_label("Yield", fontsize=18)
    cbar.ax.tick_params(labelsize=14, width=1.5)
    cbar.outline.set_linewidth(1.5)
    hep.cms.label("Preliminary", data=False, year=year, com='13.6', fontsize=18)
    ax.set_xlabel(xaxis, fontsize=18, labelpad=10)
    ax.set_ylabel(yaxis, fontsize=18, labelpad=10)
    ax.tick_params(axis='both', which='major', labelsize=14, width=1.5)  # Ticks principales
    ax.tick_params(axis='both', which='minor', labelsize=14, width=1.5)
    ax.legend(title=label, fontsize=12, frameon=True, loc='lower right', title_fontsize=12)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["right"].set_linewidth(1.5)
    ax.spines["top"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    fig.savefig(output+'/'+name+".png", dpi=140)


def plotEfficiency2D(name, efficiency, label, output, xaxis = '', yaxis='', year='X', lumi='', text=False):    
    values, x_edges, y_edges = get2DEfficiencies(efficiency)
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(
        values.T, 
        extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
        origin='lower',
        cmap="viridis",
        vmin=0.0,
        vmax=1.0
    )
    cbar = fig.colorbar(im, ax=ax, pad=0.01)
    cbar.set_label("Efficiency", fontsize=18)
    cbar.ax.tick_params(labelsize=14, width=1.5)
    cbar.outline.set_linewidth(1.5)
    for i in range(0, len(x_edges)-1):
            for j in range(0, len(y_edges)-1):
                val = values[i,j]
                sval = '%.2f'%(val)
                text = ax.text(x_edges[i] + 0.5*(x_edges[i+1]-x_edges[i]), x_edges[j] + 0.5*(x_edges[j+1]-x_edges[j]), sval, ha="center", va="center", color="w", fontsize=8)
                print(x_edges[i] + 0.5*(x_edges[i+1]-x_edges[i]), x_edges[j] + 0.5*(x_edges[j+1]-x_edges[j]))
    hep.cms.label("Preliminary", data=False, year=year, com='13.6', fontsize=18)
    ax.set_xlabel(xaxis, fontsize=18, labelpad=10)
    ax.set_ylabel(yaxis, fontsize=18, labelpad=10)
    ax.tick_params(axis='both', which='major', labelsize=14, width=1.5)  # Ticks principales
    ax.tick_params(axis='both', which='minor', labelsize=14, width=1.5)
    ax.legend(title=label, fontsize=12, frameon=True, loc='lower right', title_fontsize=12)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["right"].set_linewidth(1.5)
    ax.spines["top"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    fig.savefig(output+'/'+name+".png", dpi=140)



