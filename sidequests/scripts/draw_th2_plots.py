from ROOT import TFile, TCanvas, gStyle

from Utils_ROOT.ROOT_classes import make_pave

infile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/rootfiles/h2_cjlstevtsel_ge4leps_2p2f_3p1f.root"
outpdf = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/sidequests/plots/h2_cjlstevtsel_ge4leps_2p2f_3p1f.pdf"

f = TFile.Open(infile)
h1_n2p2f_combos = f.Get("h1_n2p2f_combos")
h1_n3p1f_combos = f.Get("h1_n3p1f_combos")
h2_n3p1fcombos_n2p2fcombos = f.Get("h2_n3p1fcombos_n2p2fcombos")

def draw_th2(h2, as_percent=False, z_max=10000, selec=""):
    # h2.GetXaxis().SetRangeUser(2, 5)
    # h2.GetYaxis().SetRangeUser(0, 3)
    # h2.GetXaxis().SetNdivisions(3)
    # h2.GetYaxis().SetNdivisions(3)
    h2.GetXaxis().CenterLabels(True)
    h2.GetYaxis().CenterLabels(True)
    gStyle.SetOptStat(0)
    h2.SetContour(100)
    h2.GetZaxis().SetRangeUser(0, z_max)
    h2.Draw("colz text")
    if as_percent:
        gStyle.SetPaintTextFormat(".2f%%")
    else:
        gStyle.SetPaintTextFormat(".0f")

#         gStyle.SetPaintTextFormat(".2g%%")

    pave = make_pave(xmin=0.6, ymin=0.70, xmax=0.88, ymax=0.88)
    pave.SetTextSize(0.03)
    pave.AddText("Selection:")
    if "cjlst" in selec.lower():
        pave.AddText("HIG-19-001 OS Method")
        pave.AddText(r"n_{leps} = 4")
    elif "relax" in selec.lower():
        pave.AddText(r"n_{leps} = 4")
        pave.AddText(r"#sum(charge) = #sum(flavor) = 0")
        pave.AddText(r"m_{4l} > 70 GeV")
    pave.Draw("same")
    return pave

if __name__ == '__main__':
    c = TCanvas()
    c.Print(outpdf + "[")
    for h in (h1_n2p2f_combos, h1_n3p1f_combos):
        h.GetXaxis().CenterLabels(True)
        h.Draw("hist")
        c.Print(outpdf)
    pave = draw_th2(h2_n3p1fcombos_n2p2fcombos, as_percent=False, z_max=10000, selec="")
    c.Print(outpdf)
    c.Print(outpdf + "]")
