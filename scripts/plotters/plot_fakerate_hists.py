"""Fake Rate Histogram Plotter

Use this code after running:
- main_FR_CR.py
- WZremoval_from_FR_comp.py
Plots FRs before and after WZ removal
"""
# import ROOT as rt
from ROOT import TFile, TCanvas, kRed, kBlue, TLegend
from Utils_Python.Utils_Files import check_overwrite

infile = "../../data/Hist_Data_ptl3_Data.root"
infile_wz = "../../data/Hist_Data_ptl3_Data_WZremoved.root"
outfile = "../../plots/test/fakerate_hists_01.pdf"
overwrite = 0

check_overwrite(outfile, overwrite=overwrite)

f = TFile(infile)
f_wz = TFile(infile_wz)
key_ls = f.GetListOfKeys()

c = TCanvas('c', 'c', 0, 67, 600, 600)
c.Print(outfile + "[")

def draw_kinem_dists(key_ls):
    """Draw all kinematic distributions with key in `key_ls`.
    
    NOTE: Skips over any key containing 'FR'.
    """
    for k in key_ls:
        name = k.GetName()
        hist = f.Get(name)
        if 'FR' in name:
            continue
        # opt = "" if 'FR' in name else "hist e1"
        opt = 'hist e'
        hist.Draw(opt)
        c.Print(outfile)

c.SetTickx(1)
c.SetTicky(1)

h_EB = f.Get('Data_FRel_EB')
h_MB = f.Get('Data_FRmu_EB')
h_EE = f.Get('Data_FRel_EE')
h_ME = f.Get('Data_FRmu_EE')

# Plots after removing WZ events.
h_EB_wz = f_wz.Get('Data_FRel_EB')
h_MB_wz = f_wz.Get('Data_FRmu_EB')
h_EE_wz = f_wz.Get('Data_FRel_EE')
h_ME_wz = f_wz.Get('Data_FRmu_EE')

h_EE.SetLineColor(kRed)
h_EB.SetLineColor(kBlue)
h_EE_wz.SetLineColor(kRed)
h_EB_wz.SetLineColor(kBlue)
h_ME.SetLineColor(kRed)
h_MB.SetLineColor(kBlue)
h_ME_wz.SetLineColor(kRed)
h_MB_wz.SetLineColor(kBlue)

h_EE_wz.SetLineStyle(2)  # Dashed.
h_EB_wz.SetLineStyle(2)
h_ME_wz.SetLineStyle(2)  # Dashed.
h_MB_wz.SetLineStyle(2)

h_EB.GetXaxis().SetTitle(r'p_{T}^{e} [GeV]')
h_MB.GetXaxis().SetTitle(r'p_{T}^{#mu} [GeV]')
h_EB.GetYaxis().SetTitle(r'Fake Rate')
h_MB.GetYaxis().SetTitle(r'Fake Rate')
h_EB.SetTitle('Third lepton (loose): electron')
h_MB.SetTitle('Third lepton (loose): muon')
h_EB.GetXaxis().SetTitleOffset(1.1)
h_MB.GetXaxis().SetTitleOffset(1.1)
h_EB.GetYaxis().SetTitleOffset(1.5)
h_MB.GetYaxis().SetTitleOffset(1.5)
# h_EB.GetXaxis().SetRangeUser(4, 84)
h_EB.GetYaxis().SetRangeUser(0.01, 0.35)
h_MB.GetYaxis().SetRangeUser(0.04, 0.35)
h_EB.SetStats(0)
h_MB.SetStats(0)

h_EB.Draw()
h_EE.Draw('same')
h_EB_wz.Draw('same')
h_EE_wz.Draw('same')

leg = TLegend(0.1220736, 0.6069565, 0.4331104, 0.8521739)
# leg = TLegend(30, 20, '', 'brNDC')
leg.AddEntry(h_EB, "barrel uncorrected", "l")
leg.AddEntry(h_EB_wz, "barrel corrected", "l")
leg.AddEntry(h_EE, "endcap uncorrected", "l")
leg.AddEntry(h_EE_wz, "endcap corrected", "l")
# leg.SetLineWidth(3)
# leg.SetBorderSize(0)
# leg.SetTextSize(0.03)
leg.Draw("same")

# c.Update()
c.Print(outfile)

#--- Now print muon FR plots. ---#
h_MB.Draw()
h_ME.Draw('same')
h_MB_wz.Draw('same')
h_ME_wz.Draw('same')

leg = TLegend(0.1220736, 0.6069565, 0.4331104, 0.8521739)
# leg = TLegend(30, 20, '', 'brNDC')
leg.AddEntry(h_MB, "barrel uncorrected", "l")
leg.AddEntry(h_MB_wz, "barrel corrected", "l")
leg.AddEntry(h_ME, "endcap uncorrected", "l")
leg.AddEntry(h_ME_wz, "endcap corrected", "l")
# leg.SetLineWidth(3)
# leg.SetBorderSize(0)
# leg.SetTextSize(0.03)
leg.Draw("same")

c.Print(outfile)

# draw_fakerate_plots()
# draw_kinem_dists(key_ls)
c.Print(outfile + "]")
