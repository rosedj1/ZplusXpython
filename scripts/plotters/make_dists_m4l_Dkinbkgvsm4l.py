"""Draw distributions and estimate SR yields for RedBkg studies.

Plot info is stored in `branch_plotinfo_dct`.

Author: Jake Rosenzweig
Created: 2021-10-04
"""
import os
import json
import ROOT as rt
import pandas as pd
from pprint import pprint
# Local modules.
from Utils_ROOT.Printer import CanvasPrinter
from Utils_Python.Utils_Files import check_overwrite
from constants.mass4lErr_binedges import finalstate_dct
from scripts.helpers.normalize_col_2Dhist import cpp_str_normalize_th2f_col
from classes.yieldcollector import YieldCollector
from classes.redbkgestimator import RedBkgEstimator
from Utils_ROOT.ROOT_classes import make_TH1F

infile_data = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/Data_2018_newbranches.root"
infile_zz   = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/MC_ZZ_2018_newbranches.root"
# infile = "/blue/avery/rosedj1/ZplusXpython/data/ZLL_CR_FRapplied/Data_and_ZZ_isMCzz_branch.root"

outfile_name = "test01_fillhistsviaeventloop.pdf"
# outfile_name = "test12_mass4l_vtxFSR_BS_dists_DataAndZZ_105m4l140GeV_keepnegweights.pdf"
# outfile_name = "test12_mass4l_vtxFSR_BS_dists_DataAndZZ_70m4l870GeV_setnegweightstozero.pdf"
outpath_pdf = os.path.join("/blue/avery/rosedj1/ZplusXpython/plots/m4l_Dkinvsm4l/test/", outfile_name)
# Filippo needs yields in '.py' instead of '.txt'.
outpath_txt_yields = os.path.join("/blue/avery/rosedj1/ZplusXpython/txt/", outfile_name.replace("pdf", "py"))
overwrite = 1

branch_plotinfo_dct = {
    # # m4l.
    "mass4l" : {"title":None, "n_bins":40, "xlabel":r"m_{4l}", "x_min":70, "x_max":870, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"},
    "mass4lREFIT" : {"title":None, "n_bins":40, "xlabel":r"m_{4l}^{refit}", "x_min":70, "x_max":870, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"},
    # "mass4l_noFSR",
    # "mass4lREFIT_vtx"    : {"title":None, "n_bins":70, "xlabel":r"m_{4l}^{refit, VX}", "x_min":105, "x_max":140, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"},
    "mass4lREFIT_vtx_BS" : {"title":None, "n_bins":70, "xlabel":r"m_{4l}^{refit, VX+BS}", "x_min":105, "x_max":140, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"},
    # "mass4l_vtx" : r"m_{4l}^{VX}",
    # "mass4l_vtx_BS" : r"m_{4l}^{VX+BS}",
    # "mass4l_vtxFSR" : r"m_{4l}",
    "mass4l_vtxFSR_BS" : {"title":None, "n_bins":40, "xlabel":r"m_{4l}^{VX+BS}", "x_min":70, "x_max":870, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"},
    # # Mass uncertainties : r"m_{4l}".
    # "mass4lErr" : r"m_{4l}",
    # "mass4lErr_vtx" : r"m_{4l}",
    # "mass4lErr_vtx_BS" : r"m_{4l}",
    # "mass4lErrREFIT" : r"m_{4l}",
    # "mass4lErrREFIT_vtx" : r"m_{4l}",
    "mass4lErrREFIT_vtx_BS" : {"title":None, "n_bins":200, "xlabel":r"#deltam_{4l}^{refit, VX+BS}", "x_min":0, "x_max":20, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"},
    "mass4lErrREFIT_vtx_BS/mass4lREFIT_vtx_BS" : {"title":None, "n_bins":200, "xlabel":r"#deltam_{4l}^{refit, VX+BS}/m_{4l}^{refit, VX+BS}", "x_min":0, "x_max":0.03, "ylabel":None, "y_min":None, "y_max":None, "units":None},
    # # Discriminants : r"m_{4l}".
    # "D_bkg_kin" : r"m_{4l}",
    # "D_bkg_kin_vtx_BS" : r"m_{4l}",
    "D_bkg_kin:mass4lREFIT_vtx_BS" : {"title":None, "n_bins_x":70,  "xlabel":r"m_{4l}^{refit, VX+BS}", "x_min":105, "x_max":140, "x_units":"GeV",
                                             "n_bins_y":100, "ylabel":r"D_{bkg}^{kin}", "y_min":0, "y_max":1, "y_units":None},
}

os.makedirs(os.path.dirname(outpath_pdf), exist_ok=True)
check_overwrite(outpath_pdf, overwrite=overwrite)
check_overwrite(outpath_txt_yields, overwrite=overwrite)

f = rt.TFile(infile_data, "read")
t_data = f.Get("passedEvents")
print(f"Opened file:\n{infile_data}")

h_data_2p2f = make_TH1F(internal_name="h_data_2p2f", title="2P2F Data", n_bins=40,
                        xlabel=r"m_{2#mu2e}", x_min=70, x_max=870,
                        ylabel=r"Events / 20", y_min=0, y_max=300, units="GeV")
h_data_3p1f = make_TH1F(internal_name="h_data_3p1f", title="3P1F Data", n_bins=40,
                        xlabel=r"m_{2#mu2e}", x_min=70, x_max=870,
                        ylabel=r"Events / 20", y_min=0, y_max=300, units="GeV")
h_zz_3p1f = make_TH1F(internal_name="h_zz_3p1f", title="3P1F ZZ", n_bins=40,
                        xlabel=r"m_{2#mu2e}", x_min=70, x_max=870,
                        ylabel=r"Events / 20", y_min=0, y_max=300, units="GeV")

for h in (h_data_2p2f, h_data_3p1f, h_zz_3p1f):
    h.SetDirectory(0)
    
for evt in t_data:
    x_val = evt.mass4l_vtxFSR_BS
    wt = evt.weightwithFRratios
    if evt.is2P2F:
        h_data_2p2f.Fill(x_val, wt)
    elif evt.is3P1F:
        h_data_3p1f.Fill(x_val, wt)

f = rt.TFile(infile_zz, "read")
t_zz = f.Get("passedEvents")
print(f"Opened file:\n{infile_zz}")

for evt in t_zz:
    x_val = evt.mass4l_vtxFSR_BS
    wt = evt.weightwithFRratios
    if evt.is3P1F:
        h_zz_3p1f.Fill(x_val, wt)

printer = CanvasPrinter(show_plots=False, show_statsbox=1, canv=None)
printer.canv.SetMargin(0.12, 0.12, 0.12, 0.12)  # L, R, B, T.
printer.canv.Print(outpath_pdf + "[")
for h in (h_data_2p2f, h_data_3p1f, h_zz_3p1f):
    h.SetMarkerStyle(20)
    h.Draw()
    printer.canv.Print(outpath_pdf)
printer.canv.Print(outpath_pdf + "]")


# class RedBkgPlotter:
#     """
#     A class that plots combinations of samples by final state or relmasserr
#     bins.
#     """

#     def __init__(self):
#         self.sample_dct = {}

#     def add_sample(self, nickname, filepath):
#         """Add key:val pair to `self.sample_dct`."""
#         self.sample_dct[nickname] = filepath

#     def plot_2P2F(self, fs, relmasserr_bin):
#         for filepath in self.sample_dct.values():
#             h = make_thiskindofhist()




# rbplotter = RedBkgEstimatePlotter()

# delim = ","

# yc = YieldCollector()
# rbe_ls = []
# relmassErr_bin_ls = 'A B'.split()
# # relmassErr_bin_ls = 'A B C D E F G H I'.split()
# data_df = []
# # for fs in list(finalstate_dct.keys()):

# for fs in list(finalstate_dct.keys()):
#     integ_ls = []
#     for b_str in relmassErr_bin_ls:
#         rbe = RedBkgEstimator(finalstate_dct=finalstate_dct, fs=fs, relmass4lErr_bin_str=b_str)
#         # rbe.hist_ls.append( rbe.make_hist(tree=t, branch="mass4lREFIT", branch_plotinfo_dct=branch_plotinfo_dct, printer=printer, outpath_pdf=outpath_pdf) )
#         # rbe.hist_ls.append( rbe.make_hist(tree=t, branch="mass4lREFIT_vtx_BS", branch_plotinfo_dct=branch_plotinfo_dct, printer=printer, outpath_pdf=outpath_pdf) )

#         # h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, printer=printer, outpath_pdf=outpath_pdf, x_lim=[118, 130], n_bins=24, set_negweights_to_zero=False)  #70, 870, 40 bins
#         # h = rbe.make_hist(tree=t, branch="mass4l", branch_plotinfo_dct=branch_plotinfo_dct, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins
#         # h = rbe.make_hist(tree=t, branch="mass4lREFIT", branch_plotinfo_dct=branch_plotinfo_dct, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins
#         # h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins

#         h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, control_reg="2P2F",    show_stats=True, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins
#         h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, control_reg="3P1F",    show_stats=True, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins
#         h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, control_reg="3P1F_ZZ", show_stats=True, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins
#         # evt_weight_4P0F = "(is3P1F * !isMCzz * weightwithFRratios) - (is3P1F * isMCzz * weightwithFRratios) - (is2P2F * !isMCzz * weightwithFRratios)"
#         # Try this: evt_weight_4P0F = "((is3P1F * !isMCzz) - (is3P1F * isMCzz) - (is2P2F * !isMCzz)) * weightwithFRratios"
#         h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, control_reg="4P0F", show_stats=True, printer=printer, outpath_pdf=outpath_pdf)  #70, 870, 40 bins

#         # Get yield info.
#         yield_val = h.Integral()
#         integ_ls.extend([yield_val])
#         # integ_ls.extend([f"{yield_val}{delim}"])
#         # print(f"integ_ls = {integ_ls}")
#         yc.add_yield_info(fs_code=rbe.fs_code, relmass4lErr_bin_str=b_str, yield_val=yield_val)
#         rbe.hist_ls.append(h)
#         # rbe.hist_ls.append(
#         #   rbe.make_hist(tree=t, branch="D_bkg_kin:mass4lREFIT_vtx_BS", branch_plotinfo_dct=branch_plotinfo_dct,
#         #   draw_opt="colz1", dim=2, show_stats=False, normalize_col=False, printer=printer, outpath_pdf=outpath_pdf) )
#         rbe_ls.append(rbe)
#         # h2 = rbe.make_hist(tree=t, branch="D_bkg_kin:mass4lREFIT_vtx_BS", branch_plotinfo_dct=branch_plotinfo_dct, draw_opt="colz1", dim=2, show_stats=False, normalize_col=True, intern_name_suffix="_")
#     # End loop over relative mass error bins.
#     # NOTE: Appending a list to a list (i.e. makes a 2-D list):
#     data_df.append([fs] + integ_ls + [sum(integ_ls)])
# yc.make_yield_str()
# yc.write_txt(outpath_txt_yields)

# field_ls = [f"fs{delim}"]
# field_ls.extend([f"{x}{delim}" for x in relmassErr_bin_ls])
# field_ls.extend([f"Sum({relmassErr_bin_ls[0]}:{relmassErr_bin_ls[-1]})"])

# df = pd.DataFrame(data=data_df, columns=field_ls)  # data is a 2-D array.
# print(df.to_string(index=False))

# # Make inclusive hists.
# # rbe = RedBkgEstimator(finalstate_dct=finalstate_dct, fs="inclusive", relmass4lErr_bin_str=None)
# for cr in "2P2F 3P1F 3P1F_ZZ 4P0F".split():
#     rbe = RedBkgEstimator(finalstate_dct=finalstate_dct, fs="inclusive", relmass4lErr_bin_str=None)
#     h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, control_reg=cr, show_stats=1, printer=printer, outpath_pdf=outpath_pdf, verbose=1)  #70, 870, 40 bins
#     current_ymax = rt.gPad.GetUymax()
#     if cr in "4P0F":
#         current_ymax *= 2.0
#     for fs in "4mu 4e 2e2mu 2mu2e".split():
#         rbe = RedBkgEstimator(finalstate_dct=finalstate_dct, fs=fs, relmass4lErr_bin_str=None)
#         h = rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS", branch_plotinfo_dct=branch_plotinfo_dct, control_reg=cr, y_lim=[0, current_ymax], show_stats=1, printer=printer, outpath_pdf=outpath_pdf, verbose=1)  #70, 870, 40 bins

# printer.canv.Print(outpath_pdf + "]")
  
# #--- MAIN IDEA ---#
# # [X] rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS")
# # [X]  rbe.make_hist(tree=t, branch="mass4lREFIT_vtx_BS")
# # rbe.make_hist2d(branch_y="D_bkg_kin", branch_x="mass4lREFIT_vtx_BS", normalize_cols=True)
# # rbe.fit_m4l(hist=rbe.h_mass4lREFIT_vtx_BS, draw=True, canv=printer.canv)
# # rbe.save_rootfile(outpath="")