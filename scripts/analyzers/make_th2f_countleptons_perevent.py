"""TODO: Make sure script CAN run and runs as expected. Read through it once.
# ============================================================================
# Purpose: Make a PDF of TH2 distributions showing lepton counts:
#     - number of leps passing loose sel. + tightID vs. total number of leps
#     - number of tight leps (loose+tightID+RelIso) vs. total number of leps
#     It also gives TH2 plots normalized by column and by total integral.
# Created: 2021-11-09
# Updated: 2021-11-18
# Author:  Jake Rosenzweig
# ============================================================================
"""
from ROOT import TFile, TCanvas, gStyle, gPad
from Utils_ROOT.ROOT_classes import make_TH2F, normalize_TH2_per_column
from Utils_Python.Plot_Styles_ROOT.tdrstyle_official import setTDRStyle

save_th2fs_in_rootfile = 0
recover_th2fs_from_rootfile = 1

infile_root = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/filippo/rootfiles/Data_2018_03Nov.root"
# outpdf_path = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/filippo/test/test03_th2f_totalleps_vs_tightleps.pdf"
outpdf_path = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/filippo/test/allth2_totalleps_vs_tightleps_formatp2g.pdf"
infile_recover_th2fs = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/filippo/th2f_totalleps_vs_tightleps.root"
# ============================================================================
def make_two_emptyTH2_hists():
    z_min = 0
    z_max = 5.5E6
    x_label = r"Number of leptons per event"

    h2_ntightleps_vs_ntotleps = make_TH2F("h2_ntightleps_vs_ntotleps", title="",#"Number of events with loose+tightID leptons vs. total number of leptons", 
                n_binsx=10, x_label=x_label,
                x_units=None, x_min=2, x_max=12,
                n_binsy=8, y_label=r"Number of leptons (passing loose+tightID) per event",
                y_units=None, y_min=0, y_max=8,
                z_min=z_min, z_max=z_max, z_label_size=None,
                n_contour=100)
                
    h2_ntightandIsoleps_vs_ntotleps = make_TH2F("h2_ntightandIsoleps_vs_ntotleps", title="",#"Number of events with (tight & isolated) vs. total leptons", 
                n_binsx=10, x_label=x_label,
                x_units=None, x_min=2, x_max=12,
                n_binsy=8, y_label=r"Number of tight leptons per event",
                y_units=None, y_min=0, y_max=8,
                z_min=z_min, z_max=z_max, z_label_size=None,
                n_contour=100)

    return (h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps)

def make_two_filledTH2_hists(tree):
    h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps = make_two_emptyTH2_hists()

    # Event loop.
    n_tot_entries = tree.GetEntries()
    for ct, evt in enumerate(tree):
        if (ct % 500000) == 0:
            print(f"Event {ct}/{n_tot_entries}")

        lep_ls_id = list(evt.lep_id)
        lep_ls_tightId = list(evt.lep_tightId)
        lep_ls_RelIsoNoFSR = list(evt.lep_RelIsoNoFSR)
        n_tot_leps = len(lep_ls_id)

        # Check to see if each lepton is tight:
        n_tightId_per_event = 0
        n_tightId_and_RelIso_per_event = 0
        for ndx in range(n_tot_leps):
            is_tightID = lep_ls_tightId[ndx]
            if is_tightID:
                n_tightId_per_event += 1

                # If we have a muon, see if it passed RelIso:
                if abs(lep_ls_id[ndx]) == 13:
                    if lep_ls_RelIsoNoFSR[ndx] < 0.35:
                        n_tightId_and_RelIso_per_event += 1

        h2_ntightleps_vs_ntotleps.Fill(n_tot_leps, n_tightId_per_event, 1)
        h2_ntightandIsoleps_vs_ntotleps.Fill(n_tot_leps, n_tightId_and_RelIso_per_event, 1)
    return h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps

def make_pave_with_stats(h2, xmin=0.15, ymin=0.8, xmax=0.4, ymax=0.9):
    """Return a TPave with simple stats located at (xmin, ymin, xmax, ymax)."""
    pave = TPaveText(xmin, ymin, xmax, ymax, "NDC")  # NDC = normalized coord.
    pave.SetFillColor(0)
    pave.SetFillStyle(1001)  # Solid fill.
    pave.SetBorderSize(1) # Use 0 for no border.
    pave.SetTextAlign(11)
    pave.SetTextSize(0.02)
    pave.AddText(f"Entries: {h2.GetEntries():.3f}")
    pave.AddText(f"Integral: {h2.Integral():.3f}")
    # pave.Draw("same")
    return pave

def make_pdf_with_twoTH2Fs(th2_first, th2_sec, outpdf_path):
    hist_ls = [th2_first, th2_sec]

    canv = TCanvas()
    style = setTDRStyle(pad_right_margin=0.15)
    gStyle.SetPaintTextFormat(".3g")
    gStyle.SetOptStat(0)

    canv.Print(outpdf_path + "[")
    for h2 in hist_ls:
        h2.GetXaxis().CenterLabels()
        h2.GetYaxis().CenterLabels()
        h2.UseCurrentStyle()
        h2.Draw("colz text")
        gPad.Update()
        pave = make_pave_with_stats(h2, xmin=0.15, ymin=0.8, xmax=0.4, ymax=0.9)
        pave.Draw("same")
        # statsbox = h2.FindObject("stats")
        # statsbox.SetX1NDC(0.55)
        # statsbox.SetX2NDC(0.8)
        # statsbox.SetY1NDC(0.8)
        # statsbox.SetY2NDC(0.9)
        canv.Print(outpdf_path)
    canv.Print(outpdf_path + "]")

def make_pdf_with_sixTH2Fs(
    h2_ntightleps_vs_ntotleps,
    h2_ntightandIsoleps_vs_ntotleps,
    h2_ntightleps_vs_ntotleps_perc,
    h2_ntightandIsoleps_vs_ntotleps_perc,
    h2_norm_ntightleps_vs_ntotleps_perc,
    h2_norm_ntightandIsoleps_vs_ntotleps_perc
    ):
    """Make a PDF with all 6 two-D hists.

    Args:
        h2_ntightleps_vs_ntotleps (ROOT.TH2): First TH2.
        h2_ntightandIsoleps_vs_ntotleps (ROOT.TH2): [description]
        h2_ntightleps_vs_ntotleps_perc (ROOT.TH2): [description]
        h2_ntightandIsoleps_vs_ntotleps_perc (ROOT.TH2): [description]
        h2_norm_ntightleps_vs_ntotleps_perc (ROOT.TH2): [description]
        h2_norm_ntightandIsoleps_vs_ntotleps_perc (ROOT.TH2): [description]
    """
    markersize = 0.8  # 0.1, 0.01
    style = setTDRStyle()
    style.cd()
    style.SetPadRightMargin(0.15)

    canv = TCanvas()
    gStyle.SetOptStat(0)

    canv.Print(outpdf_path + "[")
    for h in (h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps):
        gStyle.SetPaintTextFormat(".2g")
        h.UseCurrentStyle()
        h.SetMarkerSize(markersize)
        h.GetZaxis().SetRangeUser(0, 5.5E6)
        h.Draw("colz text")
        pave = make_pave_with_stats(h, xmin=0.15, ymin=0.8, xmax=0.4, ymax=0.9)
        pave.Draw("same")
        canv.Print(outpdf_path)

    for h in (h2_ntightleps_vs_ntotleps_perc, h2_ntightandIsoleps_vs_ntotleps_perc):
        gStyle.SetPaintTextFormat(".2g%%")
        h.SetMarkerSize(markersize)
        h.GetZaxis().SetRangeUser(0, 85.0)
        h.Draw("colz text")
        pave = make_pave_with_stats(h, xmin=0.15, ymin=0.8, xmax=0.4, ymax=0.9)
        pave.Draw("same")
        canv.Print(outpdf_path)

    for h in (h2_norm_ntightleps_vs_ntotleps_perc, h2_norm_ntightandIsoleps_vs_ntotleps_perc):
        gStyle.SetPaintTextFormat(".2g%%")
        h.SetMarkerSize(markersize)
        h.GetZaxis().SetRangeUser(0, 100.0)
        h.Draw("colz text")
        pave = make_pave_with_stats(h, xmin=0.15, ymin=0.8, xmax=0.4, ymax=0.9)
        pave.Draw("same")
        canv.Print(outpdf_path)
    canv.Print(outpdf_path + "]")

def normalize_th2fs(h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps):
    """Return 4 more TH2 dists normalized by columns or by integral.

    Args:
        h2_ntightleps_vs_ntotleps (ROOT.TH2): First TH2.
        h2_ntightandIsoleps_vs_ntotleps (ROOT.TH2): Second TH2.

    Returns:
        4-tuple: (h2_ntightleps_vs_ntotleps_perc,
                  h2_ntightandIsoleps_vs_ntotleps_perc,
                  h2_norm_ntightleps_vs_ntotleps_perc,
                  h2_norm_ntightandIsoleps_vs_ntotleps_perc
                  )
    """
    #--- Convert to percent of all entries in TH2. ---#
    h2_ntightleps_vs_ntotleps_perc = h2_ntightleps_vs_ntotleps.Clone()
    h2_ntightleps_vs_ntotleps_perc.Scale(100.0/h2_ntightleps_vs_ntotleps.Integral())
    title = h2_ntightleps_vs_ntotleps_perc.GetTitle()
    h2_ntightleps_vs_ntotleps_perc.SetTitle(f"{title} (as % of total integral)")

    h2_ntightandIsoleps_vs_ntotleps_perc = h2_ntightandIsoleps_vs_ntotleps.Clone()
    h2_ntightandIsoleps_vs_ntotleps_perc.Scale(100.0/h2_ntightandIsoleps_vs_ntotleps.Integral())
    title = h2_ntightandIsoleps_vs_ntotleps_perc.GetTitle()
    h2_ntightandIsoleps_vs_ntotleps_perc.SetTitle(f"{title} (as % of total integral)")

    #--- Already normalized per column so just convert to a percentage. ---#
    h2_norm_ntightleps_vs_ntotleps = normalize_TH2_per_column(h2_ntightleps_vs_ntotleps)
    h2_norm_ntightleps_vs_ntotleps_perc = h2_norm_ntightleps_vs_ntotleps.Clone()
    h2_norm_ntightleps_vs_ntotleps_perc.Scale(100.0)
    title = h2_norm_ntightleps_vs_ntotleps_perc.GetTitle()
    h2_norm_ntightleps_vs_ntotleps_perc.SetTitle(f"{title} (as % of total column)")

    h2_norm_ntightandIsoleps_vs_ntotleps = normalize_TH2_per_column(h2_ntightandIsoleps_vs_ntotleps)
    h2_norm_ntightandIsoleps_vs_ntotleps_perc = h2_norm_ntightandIsoleps_vs_ntotleps.Clone()
    h2_norm_ntightandIsoleps_vs_ntotleps_perc.Scale(100.0)
    title = h2_norm_ntightandIsoleps_vs_ntotleps_perc.GetTitle()
    h2_norm_ntightandIsoleps_vs_ntotleps_perc.SetTitle(f"{title} (as % of total column)")

    #--- Final hists from here: ---#
    # h2_ntightleps_vs_ntotleps_perc, h2_ntightandIsoleps_vs_ntotleps_perc
    # h2_norm_ntightleps_vs_ntotleps_perc, h2_norm_ntightandIsoleps_vs_ntotleps_perc
    return (
        h2_ntightleps_vs_ntotleps_perc,
        h2_ntightandIsoleps_vs_ntotleps_perc,
        h2_norm_ntightleps_vs_ntotleps_perc,
        h2_norm_ntightandIsoleps_vs_ntotleps_perc
        )

def write_th2fs(outpdf_path, h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps):
    """Save precious hists in a root file.

    Args:
        outpdf_path (str): Absolute path of output root file.
        h2_ntightleps_vs_ntotleps (ROOT.TH2): First TH2 to be written.
        h2_ntightandIsoleps_vs_ntotleps (ROOT.TH2): Second TH2 to be written.
    """
    outrootfile = outpdf_path.replace(".pdf", "_nleps2to12.root")
    f_new = TFile.Open(outrootfile, "recreate")
    h2_ntightleps_vs_ntotleps.Write()
    h2_ntightandIsoleps_vs_ntotleps.Write()
    f_new.Close()

def restore_th2fs(infile):
    """Open `infile` and return the two TH2Fs.

    Args:
        infile (str): Absolute file path of root file containing TH2Fs.

    Returns:
        2-tuple: (TH2F_first, TH2F_second)
    """
    f_hists = TFile(infile, "read")
    h2_ntightleps_vs_ntotleps = f_hists.Get("h2_ntightleps_vs_ntotleps")
    h2_ntightandIsoleps_vs_ntotleps = f_hists.Get("h2_ntightandIsoleps_vs_ntotleps")
    return h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps

if __name__ == '__main__':
    f_filippo_data2018 = TFile.Open(infile_root)
    t_filippo_data2018 = f_filippo_data2018.Get("passedEvents")

    h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps = make_two_filledTH2_hists(t_filippo_data2018)

    # make_pdf_with_twoTH2Fs(th2_first, th2_sec, outpdf_path)

    if save_th2fs_in_rootfile:
        write_th2fs(outpdf_path, h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps)

    if recover_th2fs_from_rootfile:
        h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps = restore_th2fs(infile_recover_th2fs)

    h2_ntightleps_vs_ntotleps_perc, h2_ntightandIsoleps_vs_ntotleps_perc, h2_norm_ntightleps_vs_ntotleps_perc, h2_norm_ntightandIsoleps_vs_ntotleps_perc = normalize_th2fs(h2_ntightleps_vs_ntotleps, h2_ntightandIsoleps_vs_ntotleps)
    
    make_pdf_with_sixTH2Fs(
        h2_ntightleps_vs_ntotleps,
        h2_ntightandIsoleps_vs_ntotleps,
        h2_ntightleps_vs_ntotleps_perc,
        h2_ntightandIsoleps_vs_ntotleps_perc,
        h2_norm_ntightleps_vs_ntotleps_perc,
        h2_norm_ntightandIsoleps_vs_ntotleps_perc
        )