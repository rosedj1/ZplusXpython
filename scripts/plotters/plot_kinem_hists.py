"""Kinematic Variable Plotter

Use this code after running:
- main_FR_CR.py

Makes distributions of:
    "mass4l", "mass4lREFIT", "mass4lREFIT_vtx_BS",
    "mass4lErr", "mass4lErrREFIT", "mass4lErrREFIT_vtx_BS",
    "met", "D_bkg_kin", "D_bkg_kin_vtx_BS"
"""
from ROOT import TFile, TCanvas, kRed, kBlue, TLegend
from Utils_Python.Utils_Files import check_overwrite
from scripts.main_FR_CR import kinem_ls

infile = "/blue/avery/rosedj1/ZplusXpython/data/Hist_Data_ptl3_Data.root"
outfile = "/blue/avery/rosedj1/ZplusXpython/plots/test/kinem_hists_baseline_vs_vxbs_03.pdf"
overwrite = 0

def fix_4ell_in_titles(h):
    """Change '4#ell' to '4#font[12]{l}' in a hist's title."""
    if '4#ell' in h.GetXaxis().GetTitle():
        old_title = h.GetXaxis().GetTitle()
        new_title = old_title.replace('4#ell', r'4#font[12]{l}')
        h.GetXaxis().SetTitle(new_title)
    if '4#ell' in h.GetTitle():
        old_title = h.GetTitle()
        new_title = old_title.replace('4#ell', r'4#font[12]{l}')
        h.SetTitle(new_title)
        
def fix_y_axis_title(h, merge_n_bins):
    """Change the event's per bin depending on the rebinning."""
    y_title = h.GetYaxis().GetTitle()
    bin_part = y_title.split('/')[1]  
    num_with_units = bin_part.lstrip().lstrip('(').rstrip(')')
    num_as_str = num_with_units.split()[0]
    num = float(num_as_str)
    # Now account for rebinning.
    new_num = num * merge_n_bins
    new_y_title = y_title.replace(num_as_str, str(new_num))
    h.GetYaxis().SetTitle(new_y_title)

related_kinems = [
    # Kinematics in the same tuple are plotted together.
    ("mass4l", "mass4lREFIT", "mass4lREFIT_vtx_BS"),
    ("mass4lErr", "mass4lErrREFIT", "mass4lErrREFIT_vtx_BS"),
    ("D_bkg_kin", "D_bkg_kin_vtx_BS"),
    ("met"),
    ]


check_overwrite(outfile, overwrite=overwrite)

f = TFile(infile)
key_ls = f.GetListOfKeys()

c = TCanvas('c', 'c', 0, 67, 600, 600)
c.Print(outfile + "[")

merge_n_bins = 2

# for kinem in kinem_ls:
for rel_kin_tup in related_kinems:
    # rel_kin_tup is a tuple with variable length.
    for control_reg in 'inclus 3P1F 2P2F'.split():
        for fs in '4e 4mu 2e2mu 2mu2e':

            for name in hist_names:
                h_list.append(f.Get(name))
            
            hist_names = [f.Get() for tit in ]
            hists = []
            for kinem in rel_kin_tup:
                find_related_hists(rel_kin, control_reg, fs)
            
            for color, h in enumerate(h_list, 2):
                fix_4ell_in_titles(h)
                if (merge_n_bins is not None) and ('m4l' in h.GetTitle()):
                    fix_y_axis_title(h, merge_n_bins)
                    h.Rebin(merge_n_bins)
                # h_base.Rebin(merge_n_bins)
                # h_refit.Rebin(merge_n_bins)
                # h_refit_vxbs.Rebin(merge_n_bins)
            
            h.SetTitle(title)
            # h1D_mass4l_3P1F_inclus.SetFillColor(4)
            h_base.SetLineColor(color)
            h_refit.SetLineColor(3)
            h_refit_vxbs.SetLineColor(2)

            opt = ' hist e '
            h_base.Draw(opt)
            h_refit.Draw('same' + opt)
            h_refit_vxbs.Draw('same' + opt)

            leg = TLegend(0.15, 0.7, 0.45, 0.85)
            leg.AddEntry(h_base, r"baseline", "f")
            leg.AddEntry(h_refit, r"Z constraint", "f")
            leg.AddEntry(h_refit_vxbs, r"Z constraint + BSC", "f")

            leg.Draw("same")

            c.Print(outfile)






def draw_three_kinem_hists(tfile, hist_name_tup, merge_n_bins, title, canv, outfile):
    """Draws three histograms to a TCanvas.

    1. baseline
    2. Z constraint (refit)
    3. Z constraint + beam spot constraint
    """
    assert len(hist_name_tup) == 3
    
    h_base = tfile.Get(hist_name_tup[0])
    h_refit = tfile.Get(hist_name_tup[1])
    h_refit_vxbs = tfile.Get(hist_name_tup[2])

    h_tup = (h_base, h_refit, h_refit_vxbs)

    for h in h_tup:
        fix_4ell_in_titles(h)
        if merge_n_bins is not None:
            fix_y_axis_title(h, merge_n_bins)
            h.Rebin(merge_n_bins)
        # h_base.Rebin(merge_n_bins)
        # h_refit.Rebin(merge_n_bins)
        # h_refit_vxbs.Rebin(merge_n_bins)
    
    h_base.SetTitle(title)
    # h1D_mass4l_3P1F_inclus.SetFillColor(4)
    h_base.SetLineColor(4)
    h_refit.SetLineColor(3)
    h_refit_vxbs.SetLineColor(2)

    opt = ' hist e '
    h_base.Draw(opt)
    h_refit.Draw('same' + opt)
    h_refit_vxbs.Draw('same' + opt)

    leg = TLegend(0.15, 0.7, 0.45, 0.9)
    leg.AddEntry(h_base, r"baseline", "f")
    leg.AddEntry(h_refit, r"Z constraint", "f")
    leg.AddEntry(h_refit_vxbs, r"Z constraint + BSC", "f")

    leg.Draw("same")

    c.Print(outfile)


draw_three_kinem_hists(
    tfile=f,
    hist_name_tup=('h1D_mass4l_3P1F_inclus', 'h1D_mass4lREFIT_3P1F_inclus', 'h1D_mass4lREFIT_vtx_BS_3P1F_inclus'),
    merge_n_bins=merge_n_bins,
    title='3P1F 4e/4#mu/2e2#mu/2#mu2e',
    canv=c,
    outfile=outfile
)

draw_three_kinem_hists(
    tfile=f,
    hist_name_tup=('h1D_mass4l_2P2F_inclus', 'h1D_mass4lREFIT_2P2F_inclus', 'h1D_mass4lREFIT_vtx_BS_2P2F_inclus'),
    merge_n_bins=merge_n_bins,
    title='2P2F 4e/4#mu/2e2#mu/2#mu2e',
    canv=c,
    outfile=outfile
)

# h1D_mass4l_3P1F_inclus = f.Get('h1D_mass4l_3P1F_inclus')
# h1D_mass4lREFIT_3P1F_inclus = f.Get('h1D_mass4lREFIT_3P1F_inclus')
# h1D_mass4lREFIT_vtx_BS_3P1F_inclus = f.Get('h1D_mass4lREFIT_vtx_BS_3P1F_inclus')

# h1D_mass4l_3P1F_inclus.Rebin(2)
# h1D_mass4lREFIT_3P1F_inclus.Rebin(2)
# h1D_mass4lREFIT_vtx_BS_3P1F_inclus.Rebin(2)

# h1D_mass4l_3P1F_inclus.SetTitle('3P1F 4e/4#mu/2e2#mu/2#mu2e')
# h1D_mass4l_3P1F_inclus.SetFillColor(4)
# h1D_mass4l_3P1F_inclus.SetLineColor(4)
# h1D_mass4lREFIT_3P1F_inclus.SetLineColor(3)
# h1D_mass4lREFIT_vtx_BS_3P1F_inclus.SetLineColor(2)

# opt = ' hist e '
# h1D_mass4l_3P1F_inclus.Draw(opt)
# h1D_mass4lREFIT_3P1F_inclus.Draw('same' + opt)
# h1D_mass4lREFIT_vtx_BS_3P1F_inclus.Draw('same' + opt)

# leg = TLegend(0.1220736, 0.6069565, 0.4331104, 0.8521739)
# leg = TLegend()
# leg.AddEntry(h1D_mass4l_3P1F_inclus, r"baseline", "f")
# leg.AddEntry(h1D_mass4lREFIT_3P1F_inclus, r"Z constraint", "f")
# leg.AddEntry(h1D_mass4lREFIT_vtx_BS_3P1F_inclus, r"Z constraint + VXBS", "f")
# leg.SetLineWidth(3)
# leg.SetBorderSize(0)
# leg.SetTextSize(0.03)
# leg.Draw("same")

# c.Print(outfile)
c.Print(outfile + ']')

# def draw_kinem_dists(key_ls):
#     """Draw all kinematic distributions with key in `key_ls`.
    
#     NOTE: Skips over any key containing 'FR'.
#     """
#     for k in key_ls:
#         name = k.GetName()
#         hist = f.Get(name)
#         if 'FR' in name:
#             continue
#         # opt = "" if 'FR' in name else "hist e1"
#         opt = 'hist e'
#         hist.Draw(opt)
#         c.Print(outfile)

# c.SetTickx(1)
# c.SetTicky(1)

# h_EB = f.Get('Data_FRel_EB')
# h_MB = f.Get('Data_FRmu_EB')
# h_EE = f.Get('Data_FRel_EE')
# h_ME = f.Get('Data_FRmu_EE')

# # Plots after removing WZ events.
# h_EB_wz = f_wz.Get('Data_FRel_EB')
# h_MB_wz = f_wz.Get('Data_FRmu_EB')
# h_EE_wz = f_wz.Get('Data_FRel_EE')
# h_ME_wz = f_wz.Get('Data_FRmu_EE')

# h_EE.SetLineColor(kRed)
# h_EB.SetLineColor(kBlue)
# h_EE_wz.SetLineColor(kRed)
# h_EB_wz.SetLineColor(kBlue)
# h_ME.SetLineColor(kRed)
# h_MB.SetLineColor(kBlue)
# h_ME_wz.SetLineColor(kRed)
# h_MB_wz.SetLineColor(kBlue)

# h_EE_wz.SetLineStyle(2)  # Dashed.
# h_EB_wz.SetLineStyle(2)
# h_ME_wz.SetLineStyle(2)  # Dashed.
# h_MB_wz.SetLineStyle(2)

# h_EB.GetXaxis().SetTitle(r'p_{T}^{e} [GeV]')
# h_MB.GetXaxis().SetTitle(r'p_{T}^{#mu} [GeV]')
# h_EB.GetYaxis().SetTitle(r'Fake Rate')
# h_MB.GetYaxis().SetTitle(r'Fake Rate')
# h_EB.SetTitle('Third lepton (loose): electron')
# h_MB.SetTitle('Third lepton (loose): muon')
# h_EB.GetXaxis().SetTitleOffset(1.1)
# h_MB.GetXaxis().SetTitleOffset(1.1)
# h_EB.GetYaxis().SetTitleOffset(1.5)
# h_MB.GetYaxis().SetTitleOffset(1.5)
# # h_EB.GetXaxis().SetRangeUser(4, 84)
# h_EB.GetYaxis().SetRangeUser(0.01, 0.35)
# h_MB.GetYaxis().SetRangeUser(0.04, 0.35)
# h_EB.SetStats(0)
# h_MB.SetStats(0)

# h_EB.Draw()
# h_EE.Draw('same')
# h_EB_wz.Draw('same')
# h_EE_wz.Draw('same')

# # c.Update()
# c.Print(outfile)

# #--- Now print muon FR plots. ---#
# h_MB.Draw()
# h_ME.Draw('same')
# h_MB_wz.Draw('same')
# h_ME_wz.Draw('same')

# leg = TLegend(0.1220736, 0.6069565, 0.4331104, 0.8521739)
# # leg = TLegend(30, 20, '', 'brNDC')
# leg.AddEntry(h_MB, "barrel uncorrected", "l")
# leg.AddEntry(h_MB_wz, "barrel corrected", "l")
# leg.AddEntry(h_ME, "endcap uncorrected", "l")
# leg.AddEntry(h_ME_wz, "endcap corrected", "l")
# # leg.SetLineWidth(3)
# # leg.SetBorderSize(0)
# # leg.SetTextSize(0.03)
# leg.Draw("same")

# c.Print(outfile)

# # draw_fakerate_plots()
# # draw_kinem_dists(key_ls)
# c.Print(outfile + "]")
