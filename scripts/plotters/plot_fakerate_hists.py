"""Fake Rate Histogram Plotter

Use this code after running:
- main_FR_CR.py
- WZremoval_from_FR_comp.py
Plots FRs before and after WZ removal
"""
# import ROOT as rt
from ROOT import TFile, TCanvas, kRed, kBlue, TLegend
from Utils_Python.Utils_Files import check_overwrite

import argparse
parser = argparse.ArgumentParser()
# parser.add_argument('-d', '--frs_data', dest="frs_data", type=str, help='input Data rootfile')
# parser.add_argument('-w', '--frs_wzrm',   dest="frs_wzrm", type=str, help='input rootfile with fake rates (WZ removed)')
# parser.add_argument('-o', '--outfile',     dest="outfile", type=str, help='output pdf with fake rate plots')
parser.add_argument('-x', '--overwrite',   dest="overwrite", action='store_true', help='Overwrite existing file.')
# parser.add_argument('-y', '--year',        dest="year", type=int, help='Year of data set sample.')
# parser.add_argument('-a', '--axisAN',        dest="axis_AN", action='store_true', help='Use AN-19-139 axis bounds.')
args = parser.parse_args()
# infile_data = args.frs_data
# infile_wz_rmv = args.frs_wzrm
# outfile = args.outfile
overwrite = args.overwrite
# year = args.year
# axis_AN = args.axis_AN

infile_data = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/vukasin_version_of_code/freshinstall_20220224/hists_Data2016_WZxs5p26pb_woFSR_preVFP_again/Hist_Data_ptl3_Data_2016.root"
infile_wz_rmv = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/vukasin_version_of_code/freshinstall_20220224/hists_Data2016_WZxs5p26pb_woFSR_preVFP_again/Hist_Data_ptl3_WZremoved_2016.root"
outfile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/plots/hists_fakerate/fakerates_2016preVFP_UL_WZxs5p26pb_woFSR_niceaxisrange.pdf"
# outfile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/plots/hists_fakerate/fakerates_2016preVFP_UL_WZxs5p26pb_woFSR_yaxissyncwithAN.pdf"
year = 2016
axis_AN = False
x_axis_range = [5.0, 80.0]

check_overwrite(outfile, overwrite=overwrite)

f = TFile(infile_data)
f_wz = TFile(infile_wz_rmv)
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
# h_EB.SetTitle('Third lepton (loose): electron')
# h_MB.SetTitle('Third lepton (loose): muon')
h_EB.SetTitle('')
h_MB.SetTitle('')
h_EB.GetXaxis().SetTitleOffset(1.1)
h_MB.GetXaxis().SetTitleOffset(1.1)
h_EB.GetYaxis().SetTitleOffset(1.5)
h_MB.GetYaxis().SetTitleOffset(1.5)
# h_EB.GetXaxis().SetRangeUser(4, 84)
if year == 2016:
    if axis_AN:
        y_min_muon = 0.04
        y_max_muon = 0.35
        y_min_elec = 0.008
        y_max_elec = 0.35
    else:
        y_min_muon = 0.0
        y_max_muon = 0.25
        y_min_elec = 0.0
        y_max_elec = 0.25
elif year == 2017:
    if axis_AN:
        y_min_muon = 0.0098
        y_max_muon = 0.35
        y_min_elec = 0.01
        y_max_elec = 0.35
    else:
        y_min_muon = 0.0
        y_max_muon = 0.25
        y_min_elec = 0.0
        y_max_elec = 0.25
elif year == 2018:
    if axis_AN:
        y_min_muon = 0.04
        y_max_muon = 0.35
        y_min_elec = 0.01
        y_max_elec = 0.35
    else:
        y_min_muon = 0.0
        y_max_muon = 0.25
        y_min_elec = 0.0
        y_max_elec = 0.25
else:
    raise ValueError(f"Year ({year}) must be 2016, 2017, or 2018.")

h_EB.GetYaxis().SetRangeUser(y_min_elec, y_max_elec)
h_EB.GetXaxis().SetRangeUser(x_axis_range[0], x_axis_range[1])
h_MB.GetYaxis().SetRangeUser(y_min_muon, y_max_muon)
h_MB.GetXaxis().SetRangeUser(x_axis_range[0], x_axis_range[1])
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

c.Update()
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
