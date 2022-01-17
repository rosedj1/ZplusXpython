import ROOT
from pprint import pprint

from sidequests.containers.hists_th1 import (
    h1_data_2p2f_m4l,
    h1_data_3p1f_m4l,
    h1_data_2p2fin3p1f_m4l,
    h1_zz_3p1f_m4l,
    )
from Utils_ROOT.Printer import CanvasPrinter
from Utils_ROOT.ROOT_classes import make_pave
from Utils_Python.printing import print_periodic_evtnum

infile_root = "../../rootfiles/cjlstOSmethodevtsel_2p2plusf_3p1plusf_mass4lgt0_downupscale_uncorrFRs_2018_Data_ZZ.root"
outpdf_path = "../../plots/test/sync_2p2f_3p1f_plotswithAN_test05_ANsync_2P2F.pdf"

break_at = -1

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

f = ROOT.TFile.Open(infile_root, "read")
t = f.Get("passedEvents")

#=== How to draw hists with more control. MUCH slower. ===#
d_2p2f_fs_hists = make_fs_histdict_from_clone(h1_data_2p2f_m4l)
d_3p1f_fs_hists = make_fs_histdict_from_clone(h1_data_3p1f_m4l)
d_2p2fin3p1f_fs_hists = make_fs_histdict_from_clone(h1_data_2p2fin3p1f_m4l)

# Fix axis labels. 
for fs, new_label in zip(
    (1, 2, 3, 4),
    (r"4#mu", r"4e", r"2e2#mu", r"2#mu2e")
    ):
    replace_4l_in_hist_title(d_2p2f_fs_hists[fs], new_label)
    replace_4l_in_hist_title(d_3p1f_fs_hists[fs], new_label)

#####################
#=== Event Loop. ===#
#####################
n_tot = t.GetEntries()
for ct in range(n_tot):
    t.GetEntry(ct)
    if ct == break_at:
        break
    print_periodic_evtnum(ct, n_tot, print_every=100000)
    if t.isMCzz:
        continue

    # Only play with Data for now.
    m4l = t.mass4l
    fs = t.finalState
    if t.is3P1F:
        d_3p1f_fs_hists[fs].Fill(m4l, 1)
        # Inclusive.
        h1_data_3p1f_m4l.Fill(m4l, 1)
    elif t.is2P2F:
        d_2p2f_fs_hists[fs].Fill(m4l, 1)
        # Inclusive.
        h1_data_2p2f_m4l.Fill(m4l, 1)
        # Evaluate the contribution of 2P2F in the 3P1F CR.
        wgt_2p2f_in_3p1f = (t.fr2 / (1 - t.fr2)) + (t.fr3 / (1 - t.fr3))
        d_2p2fin3p1f_fs_hists[fs].Fill(m4l, wgt_2p2f_in_3p1f)
    else:
        raise ValueError(f"Event was neither 3P1F nor 2P2F.")

#####################
#=== Draw plots. ===#
#####################
printer = CanvasPrinter(show_plots=False, show_statsbox=True, canv=None)
printer.canv.Print(outpdf_path + "[")

# Pretty up and draw hists.
for fs, y_max in zip(
    (1, 2, 3, 4),
    (895, 3105, 625, 4625)
    ):
    prettyup_and_drawhist(d_2p2f_fs_hists[fs], printer, outpdf_path, y_max=y_max)
prettyup_and_drawhist(h1_data_2p2f_m4l, printer, outpdf_path, y_max=8100)

for fs, y_max in zip(
    (1, 2, 3, 4),
    (195.0, 315.0, 153.0, 465.0)
    ):
    prettyup_and_drawhist(d_3p1f_fs_hists[fs], printer, outpdf_path, y_max=y_max)
prettyup_and_drawhist(h1_data_3p1f_m4l, printer, outpdf_path, y_max=900.0)

printer.canv.Print(outpdf_path + "]")
