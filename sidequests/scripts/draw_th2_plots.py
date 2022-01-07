import os
from ROOT import TFile, TCanvas, gStyle

from Utils_ROOT.ROOT_classes import make_pave

indir = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/"
# infile = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/h2_cjlstevtsel_2p2f_3p1f_widebins_includepassfullsel.root"
infile = os.path.join(indir, "sidequests/rootfiles/h2_cjlstOSmethodevtsel_2p2plusf_3p1plusf.root")
# outpdf = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/plots/h2_cjlstevtsel_ge4leps_2p2f_3p1f.pdf"
outpdf = os.path.join(indir, "sidequests/plots/cjlstOSmethodevtsel_2p2plusf_3p1plusf.pdf")

show_ntot_2p2f_3p1f = True
show_selections = False

def draw_th2(h2, as_percent=False, z_max=10000, selec="",
             show_ntot_2p2f_3p1f=False, show_selections=False):
    # h2.GetXaxis().SetRangeUser(2, 5)
    # h2.GetYaxis().SetRangeUser(0, 3)
    h2.GetXaxis().SetNdivisions(11)
    h2.GetYaxis().SetNdivisions(11)
    h2.GetXaxis().CenterLabels(True)
    h2.GetYaxis().CenterLabels(True)
    h2.GetXaxis().SetTitle(new_xtitle)
    h2.GetYaxis().SetTitle(new_ytitle)
    gStyle.SetOptStat(0)
    h2.SetContour(100)
    h2.GetZaxis().SetRangeUser(0, z_max)
    h2.Draw("colz text")
    if as_percent:
        gStyle.SetPaintTextFormat(".2f%%")
    else:
        gStyle.SetPaintTextFormat(".0f")

        # gStyle.SetPaintTextFormat(".2g%%")

    pave = make_pave(xmin=0.6, ymin=0.70, xmax=0.88, ymax=0.88)

    if show_ntot_2p2f_3p1f:
        pave.SetTextSize(0.05)
        ntot_2p2f = get_ntot_2p2f_evts(h2)
        ntot_3p1f = get_ntot_3p1f_evts(h2)
        pave.AddText(r"N_{2P2F} = %.0f" % ntot_2p2f)
        pave.AddText(r"N_{3P1F} = %.0f" % ntot_3p1f)
    if show_selections:
        pave.SetTextSize(0.03)
        pave.AddText("Selection:")
        if "cjlst" in selec.lower():
            pave.AddText("HIG-19-001 OS Method")
            pave.AddText(r"n_{leps} = 4")
        elif "relax" in selec.lower():
            pave.AddText(r"n_{leps} = 4")
            pave.AddText(r"#sum(charge) = #sum(flavor) = 0")
            pave.AddText(r"m_{4l} > 70 GeV")
    if show_ntot_2p2f_3p1f or show_selections:
        pave.Draw("same")
    return pave

def get_ntot_2p2f_evts(h2, verbose=False):
    """Return the sum of entries of columns from bin 1->last.
    
    This corresponds to the total number of 2P2F events in this h2.
    """
    n_tot = 0
    last_bin = h2.GetNbinsX()
    if verbose: print(f"Last bin x: {last_bin}")
    # Bin 0 = underflow. Bin 1 is number of events with 0 2P2F/3P1F combos.
    # So start at bin 2.
    for bin_x in range(2, h2.GetNbinsX()+1):
        proj_y = h2.ProjectionY(f"proj_y_{bin_x}", bin_x, bin_x)
        this_entries = proj_y.GetEntries()
        if verbose: print(f"col={bin_x} has {this_entries} events")
        n_tot += this_entries
        del proj_y
    if verbose: print(f"n_tot={n_tot}")
    return n_tot

def get_ntot_3p1f_evts(h2, verbose=False):
    """Return the sum of entries of rows from bin 1->last.
    
    This corresponds to the total number of 3P1F events in this h2.
    """
    n_tot = 0
    last_bin = h2.GetNbinsY()
    if verbose: print(f"Last bin y: {last_bin}")
    for bin_y in range(2, last_bin + 1):
        proj_x = h2.ProjectionX(f"proj_y_{bin_y}", bin_y, bin_y)
        this_entries = proj_x.GetEntries()
        if verbose: print(f"row={bin_y} has {this_entries} events")
        n_tot += this_entries
        del proj_x
    if verbose: print(f"n_tot={n_tot}")
    return n_tot

if __name__ == '__main__':
    f = TFile.Open(infile)
    h1_n2p2f_combos = f.Get("h1_n2p2f_combos")
    h1_n3p1f_combos = f.Get("h1_n3p1f_combos")
    h2_n3p1fcombos_n2p2fcombos = f.Get("h2_n3p1fcombos_n2p2fcombos")

    c = TCanvas()
    c.Print(outpdf + "[")
    for h in (h1_n2p2f_combos, h1_n3p1f_combos):
        h.GetXaxis().CenterLabels(True)
        h.Draw("hist text")
        c.SetLogy(True)
        c.Print(outpdf)
    c.SetLogy(False)
    pave = draw_th2(h2_n3p1fcombos_n2p2fcombos, as_percent=False,
                    z_max=10000, selec="", show_ntot_2p2f_3p1f=show_ntot_2p2f_3p1f,
                    show_selections=show_selections)
    c.Print(outpdf)
    c.Print(outpdf + "]")