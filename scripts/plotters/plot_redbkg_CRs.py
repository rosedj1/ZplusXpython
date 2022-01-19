import sys
import ROOT
from pprint import pprint

from sidequests.containers.hists_th1 import (
    h1_data_2p2f_m4l,
    h1_data_3p1f_m4l,
    h1_data_2p2fpred_m4l,
    h1_data_3p1fpred_m4l,
    h1_data_2p2fin3p1f_m4l,
    h1_zz_3p1f_m4l,
    )
from Utils_ROOT.Printer import CanvasPrinter
from Utils_ROOT.ROOT_classes import make_pave
from Utils_Python.printing import (
    print_periodic_evtnum, print_header_message
    )

infile_root = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_downupscale_2ormoretightleps_2018_Data.root"
outpdf_path = "../../plots/syncplotswithAN_2p2f_3p1f_rawandpred_2ormoretightleps.pdf"

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

def make_fs_histdict_from_clone(h_to_clone):
    """Return a dict of hists for finalStates 1->4 made from a hist clone."""
    d = {}
    for fs in (1, 2, 3, 4):
        h = h_to_clone.Clone()
        name = f"{h.GetName()}_fs{fs}"
        h.SetName(name)
        d[fs] = h
    return d

def print_integral_dict_hist(dict_of_hists):
    for fs, h in dict_of_hists.items():
        print(f"finalstate = {fs}, integral = {h.Integral():.2f}")

f = ROOT.TFile.Open(infile_root, "read")
t = f.Get("passedEvents")

# Make dicts of hists to sort by final state.
d_2p2f_fs_hists = make_fs_histdict_from_clone(h1_data_2p2f_m4l)  # Raw Data events.
d_3p1f_fs_hists = make_fs_histdict_from_clone(h1_data_3p1f_m4l)  # Raw Data events.
d_2p2fpred_fs_hists = make_fs_histdict_from_clone(h1_data_2p2fpred_m4l)  # Predicted using FRs.
d_3p1fpred_fs_hists = make_fs_histdict_from_clone(h1_data_3p1fpred_m4l)  # Predicted using FRs.
d_2p2fin3p1f_fs_hists = make_fs_histdict_from_clone(h1_data_2p2fin3p1f_m4l)

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

#####################
#=== Event Loop. ===#
#####################
n_tot = t.GetEntries()
for ct in range(n_tot):

    # Loop control.
    t.GetEntry(ct)
    if ct == break_at:
        break
    print_periodic_evtnum(ct, n_tot, print_every=print_every)

    if t.isMCzz:
        continue
    # Only play with Data for now.
    m4l = t.mass4l
    fs = t.finalState
    wgt_fr = t.eventWeightFR

    if t.is3P1F and not t.isMCzz:
        d_3p1f_fs_hists[fs].Fill(m4l, 1)
        d_3p1fpred_fs_hists[fs].Fill(m4l, wgt_fr)
        # Inclusive.
        h1_data_3p1f_m4l.Fill(m4l, 1)
        h1_data_3p1fpred_m4l.Fill(m4l, wgt_fr)

    elif t.is2P2F and not t.isMCzz:
        d_2p2f_fs_hists[fs].Fill(m4l, 1)
        d_2p2fpred_fs_hists[fs].Fill(m4l, wgt_fr)
        # Inclusive.
        h1_data_2p2f_m4l.Fill(m4l, 1)
        h1_data_2p2fpred_m4l.Fill(m4l, wgt_fr)

        # Evaluate the contribution of 2P2F in the 3P1F CR.
        wgt_2p2f_in_3p1f = (t.fr2 / (1 - t.fr2)) + (t.fr3 / (1 - t.fr3))
        d_2p2fin3p1f_fs_hists[fs].Fill(m4l, wgt_2p2f_in_3p1f)
        h1_data_2p2fin3p1f_m4l.Fill(m4l, wgt_2p2f_in_3p1f)
    else:
        raise ValueError(f"Event was neither 3P1F nor 2P2F.")

#####################
#=== Draw plots. ===#
#####################
printer = CanvasPrinter(show_plots=False, show_statsbox=True, canv=None)
printer.canv.Print(outpdf_path + "[")

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
