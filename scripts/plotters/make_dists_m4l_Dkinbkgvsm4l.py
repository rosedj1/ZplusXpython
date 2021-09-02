"""Draw distributions for RedBkg studies.

Author: Jake Rosenzweig
Created: 2021-08-30
Updated: 2021-09-02
"""
import os
import ROOT as rt
# Local modules.
from Utils_ROOT.ROOT_classes import make_TH1F, make_TH2F
from Utils_ROOT.Printer import CanvasPrinter
from Utils_Python.Utils_Files import check_overwrite
from constants.mass4lErr_binedges import RelMassErrBinEdges, finalstate_dct

# infile = "./data/ZLL_CR_FRapplied/Data.root"
infile = "./data/ZLL_CR_FRapplied/Data_and_ZZ.root"
outpath_pdf = "/blue/avery/rosedj1/ZplusXpython/plots/m4l_Dkinvsm4l/test/test13_data_and_zz_branchdict.pdf"
overwrite = 1

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
        # tex.DrawLatex(0.6, 0.7, f"Integral = {integ:.1f}")
    bin_end = h.FindBin(x_max * 0.99999)
    bin_beg = h.FindBin(x_min * 1.00001)
    t.Draw(f"{branch}>>{hist_internal_name}", weight, "hist")
    integ = h.Integral(bin_beg, bin_end)
    print_str = (
        f"branch = {branch:<25}, x_min = {x_min:<13}, x_max = {x_max:<13}, integral = {integ:.6f}"
    )
    print(print_str)
    printer.canv.Print(outpath_pdf)

printer = CanvasPrinter(show_plots=False, show_statsbox=1, canv=None)
printer.canv.Print(outpath_pdf + "[")

class RedBkgEstimator:
    """A class to make hists, rootfiles, and fits of reducible background."""

    def __init__(self, finalstate_dct, fs, mass4lErr_bin_str):
        """
        TODO: Finish docstring.

        Parameters
        ----------
        fs : str
            Final state of 4l. Must be one of:
            '4e', '4mu', '2e2mu', '2mu2e'
        mass4lErr_bin_str : str
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'
        """
        assert fs in finalstate_dct.keys()
        self.fs = fs
        self.fs_code = finalstate_dct[self.fs]
        self.mass4lErr_bin_str = mass4lErr_bin_str
        # Make a bin edge manager to parse bins, because it's confusing.
        binedge_boi = RelMassErrBinEdges()
        self.binedge_tup = binedge_boi.get_edges_mass4lErr_bin(
            finalstate_dct, fs_str=fs, fs_int=None, m4lErr_bin_code=mass4lErr_bin_str
            )

    def make_hist_name(self, branch, dim=1):
        """Return an internal name of hist specific to this estimator."""
        return f"h{dim}_{branch}_{self.fs}_{self.mass4lErr_bin_str}"

    def make_cut_str(self):
        """Return a string of all cuts applied per event."""
        weight = "is3P1F*weight_fr - is3P1F_zz*weight_fr - is2P2F*weight_fr"
        weight_gteq_zero = f"{weight} >= 0"
        fs_cut = f"finalState == {self.fs_code}"
        m4lErr_cut = f"{self.binedge_tup[0]} <= mass4lErrREFIT_vtx_BS < {self.binedge_tup[1]}"
        # formula_alwayspos = f"({weight}) * ({weight}>=0)"
        return f"({weight}) && ({weight_gteq_zero}) && ({fs_cut}) && ({m4lErr_cut})"

    def make_hist(self, tree, branch, title=None, n_bins=70,
                  xlabel=None, x_min=105, x_max=140,
                  ylabel=None, y_min=None, y_max=None, units=None,
                  draw_hist=True, opt=""):
        """
        Return a filled TH1F from the events in `tree`, `branch` with
        `cuts` applied.
        """
        cuts = self.make_cut_str()
        internal_name = self.make_hist_name(branch, dim=1)
        h = make_TH1F(internal_name=internal_name, title=title, n_bins=n_bins,
                      xlabel=xlabel, x_min=x_min, x_max=x_max,
                      ylabel=ylabel, y_min=y_min, y_max=y_max, units=units)
        if not draw_hist:
            opt = "goff"
        tree.Draw(f"{branch}>>{internal_name}", cuts, f"hist {opt}")
        return h

rbe = RedBkgEstimator(finalstate_dct=finalstate_dct, fs="4mu", mass4lErr_bin_str="B")

# RESUME HERE.
bin_end = h.FindBin(x_max * 0.99999)
bin_beg = h.FindBin(x_min * 1.00001)
integ = h.Integral(bin_beg, bin_end)
print_str = (
    f"branch = {branch:<25}, x_min = {x_min:<13}, x_max = {x_max:<13}, integral = {integ:.6f}"
)
print(print_str)

tree, branch, title=None, n_bins=70,
                  xlabel=None, x_min=105, x_max=140,
                  ylabel=None, y_min=None, y_max=None, units=None,
                  draw_hist=True, opt=""

rbe.hist_ls = [rbe.make_hist(tree=t, branch=br, cuts=weight_alwayspos) for br in branch_dct.keys()]
rbe.make_hist(tree=t, branch="mass4l_vtxFSR_BS")
rbe.make_hist(tree=t, branch="mass4lREFIT_vtx_BS")
rbe.make_hist2d(branch_y="D_bkg_kin", branch_x="mass4lREFIT_vtx_BS", normalize_cols=True)
rbe.fit_m4l(hist=rbe.h_mass4lREFIT_vtx_BS, draw=True, canv=printer.canv)
rbe.save_rootfile(outpath="")
# for br in branch_dct.keys():
#     if ("mass4l" in br) and not ("Err" in br):
#         make_hist_draw_tree(branch=br, hist_internal_name=f"h_{br}_wide", n_bins=125, xlabel=branch_dct[br], x_min=70, x_max=570, ylabel=None, y_min=0.0, y_max=10.0, weight=weight_alwayspos)
# for br in branch_dct.keys():
#     if ("mass4l" in br) and not ("Err" in br):
#         make_hist_draw_tree(branch=br, hist_internal_name=f"h_{br}_higgswindow", n_bins=70, xlabel=branch_dct[br], x_min=105, x_max=140, ylabel=None, y_min=0.0, y_max=3.0, weight=weight_alwayspos)
# for br in branch_dct.keys():
#     if ("mass4l" in br) and not ("Err" in br):
#         make_hist_draw_tree(branch=br, hist_internal_name=f"h_{br}_higgswindow_narrow", n_bins=24, xlabel=branch_dct[br], x_min=118, x_max=130, ylabel=None, y_min=0.0, y_max=3.0, weight=weight_alwayspos)


# make_hist_draw_tree(branch="mass4lREFIT_vtx_BS", hist_internal_name="h_mass4lREFIT_vtx_BS_wide", n_bins=125, xlabel=xlabel_m4l_vtxFSR_BS, x_min=70, x_max=570, ylabel=None, y_min=None, y_max=None, weight=weight_alwayspos)
# make_hist_draw_tree(branch="mass4lREFIT_vtx_BS", hist_internal_name="h_mass4lREFIT_vtx_BS_higgswindow", n_bins=70, xlabel=xlabel_m4l_vtxFSR_BS, x_min=105, x_max=140, ylabel=None, y_min=0.0, y_max=None, weight=weight_alwayspos)
# make_hist_draw_tree(branch="mass4lREFIT_vtx_BS", hist_internal_name="h_mass4lREFIT_vtx_BS_higgswindow_narrow", n_bins=24, xlabel=xlabel_m4l_vtxFSR_BS, x_min=118, x_max=130, ylabel=None, y_min=0.0, y_max=None, weight=weight_alwayspos)

# t.Draw("D_bkg_kin:mass4lREFIT>>h2", weight_alwayspos, "colz1")
# printer.canv.Print(outpath_pdf)

printer.canv.Print(outpath_pdf + "]")