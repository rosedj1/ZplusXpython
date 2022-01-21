"""Make OS Method hists for RedBkg studies using CJLST or BBF NTuples.
==============================================================================
Author: Jake Rosenzweig
Created: 2022-01-19
Updated: 2022-01-21
Notes:
    * Need to do `voms-proxy-init` in shell before running this script.
    * Draws plots to PDF.
    * Prints out number of raw and predicted events in control regions.
==============================================================================
"""
import sys
from ROOT import TFile
from pprint import pprint

from Utils_ROOT.Printer import CanvasPrinter
from Utils_ROOT.ROOT_classes import make_pave, set_neg_bins_to_zero
from Utils_Python.printing import (
    print_periodic_evtnum, print_header_message
    )
from sidequests.data.filepaths import (
    infile_matteo_data2018_fromhpg,
    fakerates_WZremoved
    )
from sidequests.funcs.evt_loops import (
        fillhists_osmethod_bbfntuple,
        fillhists_osmethod_cjlstntuple
        )

# infile_path_data = infile_matteo_data2018_fromhpg
infile_path_data = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data.root"
infile_path_zz = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_2018_ZZ.root"
infile_fakerates = fakerates_WZremoved
outpdf_path = "../../plots/syncplotswithAN_2p2f_3p1f_ge2tightleps_bbfntuple_105m4l140_negbinremoval_DataZZ.pdf"

using_ntuple_bbf = 1
using_ntuple_cjlst = 0

m4l_window = (105, 140)
use_first_quartet = True
break_at = -1
print_every = 100000

def replace_4l_in_hist_title(hist, fs_latex):
    title = hist.GetXaxis().GetTitle()
    new_title = title.replace("4l", fs_latex)
    hist.GetXaxis().SetTitle(new_title)

def prettyup_and_drawhist(h, printer, outpdf_path, y_max):
    h.SetMarkerStyle(20)
    h.SetLineColor(1)
    h.GetYaxis().SetRangeUser(0, y_max)
    h.Draw()
    printer.canv.Print(outpdf_path)

def print_integral_dict_hist(dict_of_hists):
    for fs, h in dict_of_hists.items():
        print(f"finalstate = {fs}, integral = {h.Integral():.2f}")

def print_totalredbkg_estimate(
    h1_data_3p1fpred_m4l,
    h1_zz_3p1fpred_m4l,
    d_data_3p1fpred_fs_hists,
    d_data_2p2fpred_fs_hists,
    d_zz_3p1fpred_fs_hists,
    neg_bin_removal=True
    ):
    """Prints RedBkg estimate before and after negative bin removal.
    
    estimate = (3P1F - 2P2F -ZZ)
    """
    msg = "(3P1F - 2P2F - ZZ) Data Pred: before neg bin removal"
    if neg_bin_removal:
        msg = msg.replace("before", "AFTER")

    print_header_message(msg)
    h1_final_estimate = h1_data_3p1fpred_m4l.Clone()
    h1_final_estimate.Add(h1_data_2p2fpred_m4l, -1)
    print(f"total integral (3P1F - 2P2F) = {h1_final_estimate.Integral()}")
    h1_final_estimate.Add(h1_zz_3p1fpred_m4l, -1)
    if neg_bin_removal:
        h1_final_estimate = set_neg_bins_to_zero(h1_final_estimate)
        print(f"total integral (3P1F - 2P2F - ZZ) negbinremoval = {h1_final_estimate.Integral()}")
    else:
        print(f"total integral (3P1F - 2P2F - ZZ) = {h1_final_estimate.Integral()}")

    # Print each final state.
    for fs, h_3p1f, h_2p2f, h_3p1f_zz in zip(
            d_data_3p1fpred_fs_hists.keys(),
            d_data_3p1fpred_fs_hists.values(),
            d_data_2p2fpred_fs_hists.values(),
            d_zz_3p1fpred_fs_hists.values(),
            ):
        h1_final_estimate_fs = h_3p1f.Clone()
        h1_final_estimate_fs.Add(h_2p2f.Clone(), -1)
        h1_final_estimate_fs.Add(h_3p1f_zz.Clone(), -1)
        h1_final_estimate_fs_rmv = h1_final_estimate_fs.Clone()
        if neg_bin_removal:
            print("--- Negative bin removal ---")
            h1_final_estimate_fs_rmv = set_neg_bins_to_zero(h1_final_estimate_fs)
        print(
            f"finalstate = {fs}, "
            f"integral = {h1_final_estimate_fs_rmv.Integral():.2f}"
            )

if __name__ == '__main__':
    f_data = TFile.Open(infile_path_data, "read")
    f_zz = TFile.Open(infile_path_zz, "read")

    if using_ntuple_bbf:
        tree_name = "passedEvents"
    elif using_ntuple_cjlst:
        tree_name = "CRZLLTree/candTree"
    tree_data = f_data.Get(tree_name)
    tree_zz = f_zz.Get(tree_name)
    #####################
    #=== Event Loop. ===#
    #####################
    if using_ntuple_bbf:
        func_to_use = fillhists_osmethod_bbfntuple
    elif using_ntuple_cjlst:
        func_to_use = fillhists_osmethod_cjlstntuple

    # Fill Data hists.
    h1_data_2p2f_m4l, h1_data_3p1f_m4l, h1_data_2p2fpred_m4l, h1_data_3p1fpred_m4l, h1_data_2p2fin3p1f_m4l, d_data_2p2f_fs_hists, d_data_3p1f_fs_hists, d_data_2p2fpred_fs_hists, d_data_3p1fpred_fs_hists, d_data_2p2fin3p1f_fs_hists, _, _, _, _ = func_to_use(
        t=tree_data,
        name="Data",
        infile_fakerates=infile_fakerates,
        m4l_window=m4l_window,
        start_at=0, break_at=-1,
        print_every=print_every,
        use_first_quartet=use_first_quartet
        )

    # Fill ZZ hists.
    _, _, _, _, _, _, _, _, _, _, h1_zz_2p2fpred_m4l, h1_zz_3p1fpred_m4l, d_zz_3p1fpred_fs_hists, d_zz_2p2fpred_fs_hists = func_to_use(
        t=tree_zz,
        name="ZZ",
        infile_fakerates=infile_fakerates,
        m4l_window=m4l_window,
        start_at=0, break_at=-1,
        print_every=print_every,
        use_first_quartet=use_first_quartet
        )

    #####################
    #=== Draw plots. ===#
    #####################
    printer = CanvasPrinter(show_plots=False, show_statsbox=True, canv=None)
    printer.canv.Print(outpdf_path + "[")

    # Fix axis labels. 
    for fs, new_label in zip(
        (1, 2, 3, 4),
        (r"4#mu", r"4e", r"2e2#mu", r"2#mu2e")
        ):
        for d_hists in (
                d_data_2p2f_fs_hists,
                d_data_3p1f_fs_hists,
                d_data_2p2fpred_fs_hists,
                d_data_3p1fpred_fs_hists,
                d_data_2p2fin3p1f_fs_hists,
                d_zz_3p1fpred_fs_hists,
                d_zz_2p2fpred_fs_hists,
                ):
            replace_4l_in_hist_title(d_hists[fs], new_label)

    # Pretty up and draw hists.
    prettyup_and_drawhist(h1_data_3p1f_m4l, printer, outpdf_path, y_max=900.0)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (195.0, 315.0, 153.0, 465.0)
        ):
        prettyup_and_drawhist(d_data_3p1f_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    prettyup_and_drawhist(h1_data_2p2f_m4l, printer, outpdf_path, y_max=8100)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (895, 3105, 625, 4625)
        ):
        prettyup_and_drawhist(d_data_2p2f_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    prettyup_and_drawhist(h1_data_3p1fpred_m4l, printer, outpdf_path, y_max=240)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (100, 100, 100, 100)
        ):
        prettyup_and_drawhist(d_data_3p1fpred_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    prettyup_and_drawhist(h1_data_2p2fpred_m4l, printer, outpdf_path, y_max=120)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (50, 50, 50, 50)
        ):
        prettyup_and_drawhist(d_data_2p2fpred_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    # Need to draw 2P2F contribution to 3P1F.
    # prettyup_and_drawhist(h1_data_2p2fpred_m4l, printer, outpdf_path, y_max=120)
    # for fs, y_max in zip(
    #     (1, 2, 3, 4),
    #     (50, 50, 50, 50)
    #     ):
    #     prettyup_and_drawhist(d_data_2p2fpred_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    printer.canv.Print(outpdf_path + "]")

    print_header_message("3P1F Raw Data")
    # print(f"integral = {h1_data_3p1f_m4l.Integral():.2f}")
    print_integral_dict_hist(d_data_3p1f_fs_hists)

    print_header_message("2P2F Raw Data")
    # print(f"integral = {h1_data_2p2f_m4l.Integral():.2f}")
    print_integral_dict_hist(d_data_2p2f_fs_hists)

    print_header_message("3P1F Data Pred")
    # print(f"integral = {h1_data_3p1fpred_m4l.Integral():.2f}")
    print_integral_dict_hist(d_data_3p1fpred_fs_hists)

    print_header_message("2P2F Data Pred")
    # print(f"integral = {h1_data_2p2fpred_m4l.Integral():.2f}")
    print_integral_dict_hist(d_data_2p2fpred_fs_hists)

    print_totalredbkg_estimate(
        h1_data_3p1fpred_m4l,
        h1_zz_3p1fpred_m4l,
        d_data_3p1fpred_fs_hists,
        d_data_2p2fpred_fs_hists,
        d_zz_3p1fpred_fs_hists,
        neg_bin_removal=False
        )

    print_totalredbkg_estimate(
        h1_data_3p1fpred_m4l,
        h1_zz_3p1fpred_m4l,
        d_data_3p1fpred_fs_hists,
        d_data_2p2fpred_fs_hists,
        d_zz_3p1fpred_fs_hists,
        neg_bin_removal=True
        )

    print_header_message("2P2F Contribution to 3P1F Pred")
    # print(f"integral = {h1_data_2p2fin3p1f_m4l.Integral():.2f}")
    print_integral_dict_hist(d_data_2p2fin3p1f_fs_hists)
