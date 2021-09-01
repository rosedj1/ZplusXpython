"""Draw distributions for RedBkg studies."""
import os
import ROOT as rt
# Local modules.
from Utils_ROOT.ROOT_classes import make_TH1F, make_TH2F
from Utils_ROOT.Printer import CanvasPrinter
from Utils_Python.Utils_Files import check_overwrite

# infile = "./data/ZLL_CR_FRapplied/Data.root"
infile = "./data/ZLL_CR_FRapplied/Data_and_ZZ.root"
outpath_pdf = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/plots/m4l_Dkinvsm4l/test/test13_data_and_zz_branchdict.pdf"
overwrite = 1

os.makedirs(os.path.dirname(outpath_pdf), exist_ok=True)
check_overwrite(outpath_pdf, overwrite=overwrite)

f = rt.TFile(infile, "read")
t = f.Get("passedEvents")

xlabel_m4l_refit = r"m_{4l}^{refit}"
xlabel_m4l_vtxFSR_BS = r"m_{4l}^{FSR, VX}"
xlabel_m4l_refit_vtx_BS = r"m_{4l}^{refit, VX}"
formula_str = r"N_{SR}^{RedBkg} = "
formula_str += r"#sum_{i}^{N_{3P1F}}#frac{f^{i}}{1-f^{i}} - "
formula_str += r"w_{ZZ}#sum_{j}^{N_{3P1F}^{ZZ}}#frac{f^{j}}{1-f^{j}} - "
formula_str += r"#sum_{k}^{N_{2P2F}}#left(#frac{f^{k}_{3}}{1-f^{k}_{3}}#right)"
formula_str += r"#left(#frac{f^{k}_{4}}{1-f^{k}_{4}}#right)"

def make_hist_draw_tree(branch, hist_internal_name, n_bins=70,
                        xlabel=None, x_min=105, x_max=140,
                        ylabel=None, y_min=None, y_max=None,
                        weight=1):
    h = make_TH1F(internal_name=hist_internal_name, title=formula_str, n_bins=n_bins,
                xlabel=xlabel, x_min=x_min, x_max=x_max,
                ylabel=ylabel, y_min=y_min, y_max=y_max, units="GeV")
    # tex = rt.TLatex()
    # tex.SetNDC()
    # tex.SetTextSize(0.03)
    # tex.SetTextColor(rt.kRed)
    bin_beg = h.FindBin(x_min*1.001)
    bin_end = h.FindBin(x_max*0.999)
    t.Draw(f"{branch}>>{hist_internal_name}", weight, "hist")
    integ = h.Integral(bin_beg, bin_end)
    # tex.DrawLatex(0.6, 0.7, f"Integral = {integ:.1f}")
    print_str = (
        f"branch = {branch:<25}, x_min = {x_min:<13}, x_max = {x_max:<13}, integral = {integ:.6f}"
    )
    print(print_str)
    printer.canv.Print(outpath_pdf)

# h_eventWeight = make_TH1F(internal_name="h_eventWeight", title="eventWeight", n_bins=100,
#               xlabel="eventWeight", x_min=-1, x_max=3,
#               ylabel=None, units=None)
# h_mass4lREFIT_wide = make_TH1F(internal_name="h_mass4lREFIT_wide", title=formula_str, n_bins=250,
#               xlabel=xlabel_m4l_refit, x_min=70, x_max=570,
#               ylabel=None, units="GeV")
# h_mass4lREFIT_higgswindow = make_TH1F(internal_name="h_mass4lREFIT_higgswindow", title=formula_str, n_bins=70,
#               xlabel=xlabel_m4l_refit, x_min=105, x_max=140,
#               ylabel=None, units="GeV")
# h_mass4lREFIT_higgswindow_narrow = make_TH1F(internal_name="h_mass4lREFIT_higgswindow_narrow", title=formula_str, n_bins=24,
#               xlabel=xlabel_m4l_refit, x_min=118, x_max=130,
#               ylabel=None, units="GeV")
# h_mass4l_vtxFSR_BS_higgswindow = make_TH1F(internal_name="h_mass4l_vtxFSR_BS_higgswindow", title=formula_str, n_bins=70,
#               xlabel=xlabel_m4l_vtxFSR_BS, x_min=105, x_max=140,
#               ylabel=None, units="GeV")
# h_mass4l_vtxFSR_BS_higgswindow_narrow = make_TH1F(internal_name="h_mass4l_vtxFSR_BS_higgswindow_narrow", title=formula_str, n_bins=24,
#               xlabel=xlabel_m4l_vtxFSR_BS, x_min=118, x_max=130,
#               ylabel=None, units="GeV")
# h_mass4lREFIT_vtx_BS_higgswindow = make_TH1F(internal_name="h_mass4lREFIT_vtx_BS_higgswindow", title=formula_str, n_bins=70,
#               xlabel=xlabel_m4l_vtxFSR_BS, x_min=105, x_max=140,
#               ylabel=None, units="GeV")
# h_mass4lREFIT_vtx_BS_higgswindow_narrow = make_TH1F(internal_name="h_mass4lREFIT_vtx_BS_higgswindow_narrow", title=formula_str, n_bins=24,
#               xlabel=xlabel_m4l_vtxFSR_BS, x_min=118, x_max=130,
#               ylabel=None, units="GeV")
# h2 = make_TH2F(internal_name="h2", title="", 
#           n_binsx=70, x_label=xlabel_m4l_refit, x_units="GeV", x_min=105, x_max=140,
#           n_binsy=100, y_label=r"D_{bkg}^{kin}", y_units=None, y_min=0, y_max=1,
#           z_min=None, z_max=None, z_label_size=None,
#           n_contour=100)

printer = CanvasPrinter(show_plots=False, show_statsbox=1, canv=None)
printer.canv.Print(outpath_pdf + "[")
# Draw distributions.
weight = "is3P1F*weight_fr - is3P1F_zz*weight_fr - is2P2F*weight_fr"
weight_alwayspos = f"({weight}) * ({weight}>=0)"  # 

branch_dct = {
    # m4l.
    # "mass4l_noFSR",
    "mass4lREFIT" : r"m_{4l}^{refit}",
    "mass4lREFIT_vtx" : r"m_{4l}^{refit, VX}",
    "mass4lREFIT_vtx_BS" : r"m_{4l}^{refit, VX+BS}",
    "mass4l_vtx" : r"m_{4l}^{VX}",
    "mass4l_vtx_BS" : r"m_{4l}^{VX+BS}",
    # "mass4l_vtxFSR" : r"m_{4l}",
    "mass4l_vtxFSR_BS" : r"m_{4l}^{FSR, VX+BS}",
    # # Mass uncertainties : r"m_{4l}".
    # "mass4lErr" : r"m_{4l}",
    # "mass4lErr_vtx" : r"m_{4l}",
    # "mass4lErr_vtx_BS" : r"m_{4l}",
    # "mass4lErrREFIT" : r"m_{4l}",
    # "mass4lErrREFIT_vtx" : r"m_{4l}",
    # "mass4lErrREFIT_vtx_BS" : r"m_{4l}",
    # # Discriminants : r"m_{4l}".
    # "D_bkg_kin" : r"m_{4l}",
    # "D_bkg_kin_vtx_BS" : r"m_{4l}",
}

for br in branch_dct.keys():
    if ("mass4l" in br) and not ("Err" in br):
        make_hist_draw_tree(branch=br, hist_internal_name=f"h_{br}_wide", n_bins=125, xlabel=branch_dct[br], x_min=70, x_max=570, ylabel=None, y_min=0.0, y_max=10.0, weight=weight_alwayspos)
for br in branch_dct.keys():
    if ("mass4l" in br) and not ("Err" in br):
        make_hist_draw_tree(branch=br, hist_internal_name=f"h_{br}_higgswindow", n_bins=70, xlabel=branch_dct[br], x_min=105, x_max=140, ylabel=None, y_min=0.0, y_max=3.0, weight=weight_alwayspos)
for br in branch_dct.keys():
    if ("mass4l" in br) and not ("Err" in br):
        make_hist_draw_tree(branch=br, hist_internal_name=f"h_{br}_higgswindow_narrow", n_bins=24, xlabel=branch_dct[br], x_min=118, x_max=130, ylabel=None, y_min=0.0, y_max=3.0, weight=weight_alwayspos)


# make_hist_draw_tree(branch="mass4lREFIT_vtx_BS", hist_internal_name="h_mass4lREFIT_vtx_BS_wide", n_bins=125, xlabel=xlabel_m4l_vtxFSR_BS, x_min=70, x_max=570, ylabel=None, y_min=None, y_max=None, weight=weight_alwayspos)
# make_hist_draw_tree(branch="mass4lREFIT_vtx_BS", hist_internal_name="h_mass4lREFIT_vtx_BS_higgswindow", n_bins=70, xlabel=xlabel_m4l_vtxFSR_BS, x_min=105, x_max=140, ylabel=None, y_min=0.0, y_max=None, weight=weight_alwayspos)
# make_hist_draw_tree(branch="mass4lREFIT_vtx_BS", hist_internal_name="h_mass4lREFIT_vtx_BS_higgswindow_narrow", n_bins=24, xlabel=xlabel_m4l_vtxFSR_BS, x_min=118, x_max=130, ylabel=None, y_min=0.0, y_max=None, weight=weight_alwayspos)


# t.Draw("eventWeight>>h_eventWeight", "eventWeight", "hist")
# printer.canv.Print(outpath_pdf)

# t.Draw("D_bkg_kin:mass4lREFIT>>h2", weight_alwayspos, "colz1")
# printer.canv.Print(outpath_pdf)

printer.canv.Print(outpath_pdf + "]")