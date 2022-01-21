"""Make OS Method hists for RedBkg studies using CJLST or BBF NTuples.
==============================================================================
Author: Jake Rosenzweig
Created: 2022-01-19
Updated: 2022-01-20
Notes:
    * Need to do `voms-proxy-init` in shell before running this script.
    * Will print out control region info.
==============================================================================
"""
import sys
from ROOT import TFile
from pprint import pprint

from Utils_ROOT.Printer import CanvasPrinter
from Utils_ROOT.ROOT_classes import make_pave
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

# infile_path = infile_matteo_data2018_fromhpg
infile_path = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_pTnoFSRforFRs_2018_Data.root"
infile_fakerates = fakerates_WZremoved
outpdf_path = "../../plots/test/syncplotswithAN_2p2f_3p1f_rawandpred_2ormoretightleps_test01_cjlstntuple.pdf"

using_ntuple_bbf = 1
using_ntuple_cjlst = 0

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

if __name__ == '__main__':
    f = TFile.Open(infile_path, "read")

    if using_ntuple_bbf:
        tree_name = "passedEvents"
    elif using_ntuple_cjlst:
        tree_name = "CRZLLTree/candTree"
    tree = f.Get(tree_name)
    #####################
    #=== Event Loop. ===#
    #####################
    if using_ntuple_bbf:
        func_to_use = fillhists_osmethod_bbfntuple
    elif using_ntuple_cjlst:
        func_to_use = fillhists_osmethod_cjlstntuple
    h1_data_2p2f_m4l, h1_data_3p1f_m4l, h1_data_2p2fpred_m4l, h1_data_3p1fpred_m4l, h1_data_2p2fin3p1f_m4l, d_2p2f_fs_hists, d_3p1f_fs_hists, d_2p2fpred_fs_hists, d_3p1fpred_fs_hists, d_2p2fin3p1f_fs_hists = func_to_use(
        t=tree,
        infile_fakerates=infile_fakerates,
        start_at=0, break_at=-1,
        print_every=print_every,
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
                d_2p2f_fs_hists,
                d_3p1f_fs_hists,
                d_2p2fpred_fs_hists,
                d_3p1fpred_fs_hists,
                d_2p2fin3p1f_fs_hists,
                ):
            replace_4l_in_hist_title(d_hists[fs], new_label)

    # Pretty up and draw hists.
    prettyup_and_drawhist(h1_data_3p1f_m4l, printer, outpdf_path, y_max=900.0)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (195.0, 315.0, 153.0, 465.0)
        ):
        prettyup_and_drawhist(d_3p1f_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    prettyup_and_drawhist(h1_data_2p2f_m4l, printer, outpdf_path, y_max=8100)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (895, 3105, 625, 4625)
        ):
        prettyup_and_drawhist(d_2p2f_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    prettyup_and_drawhist(h1_data_3p1fpred_m4l, printer, outpdf_path, y_max=240)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (100, 100, 100, 100)
        ):
        prettyup_and_drawhist(d_3p1fpred_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    prettyup_and_drawhist(h1_data_2p2fpred_m4l, printer, outpdf_path, y_max=120)
    for fs, y_max in zip(
        (1, 2, 3, 4),
        (50, 50, 50, 50)
        ):
        prettyup_and_drawhist(d_2p2fpred_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    # Need to draw 2P2F contribution to 3P1F.
    # prettyup_and_drawhist(h1_data_2p2fpred_m4l, printer, outpdf_path, y_max=120)
    # for fs, y_max in zip(
    #     (1, 2, 3, 4),
    #     (50, 50, 50, 50)
    #     ):
    #     prettyup_and_drawhist(d_2p2fpred_fs_hists[fs], printer, outpdf_path, y_max=y_max)

    printer.canv.Print(outpdf_path + "]")

    print_header_message("3P1F Raw Data")
    print(f"integral = {h1_data_3p1f_m4l.Integral():.2f}")
    print_integral_dict_hist(d_3p1f_fs_hists)

    print_header_message("2P2F Raw Data")
    print(f"integral = {h1_data_2p2f_m4l.Integral():.2f}")
    print_integral_dict_hist(d_2p2f_fs_hists)

    print_header_message("3P1F Data Pred")
    print(f"integral = {h1_data_3p1fpred_m4l.Integral():.2f}")
    print_integral_dict_hist(d_3p1fpred_fs_hists)

    print_header_message("2P2F Data Pred")
    print(f"integral = {h1_data_2p2fpred_m4l.Integral():.2f}")
    print_integral_dict_hist(d_2p2fpred_fs_hists)

    print_header_message("(3P1F - 2P2F) Data Pred")
    h1_data_3p1fminus2p2f = h1_data_3p1fpred_m4l.Clone()
    h1_data_3p1fminus2p2f.Add(h1_data_2p2fpred_m4l, -1)
    print(f"integral = {h1_data_3p1fminus2p2f.Integral():.2f}")
    for fs, h_3p1f, h_2p2f in zip(
            d_3p1fpred_fs_hists.keys(),
            d_3p1fpred_fs_hists.values(),
            d_2p2fpred_fs_hists.values(),
            ):
        h_3p1fminus2p2f = h_3p1f.Clone()
        h_3p1fminus2p2f.Add(h_2p2f, -1)
        print(f"finalstate = {fs}, integral = {h_3p1fminus2p2f.Integral():.2f}")

    print_header_message("2P2F Contribution to 3P1F Pred")
    print(f"integral = {h1_data_2p2fin3p1f_m4l.Integral():.2f}")
    print_integral_dict_hist(d_2p2fin3p1f_fs_hists)
