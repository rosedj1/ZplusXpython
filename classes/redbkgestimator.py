import ROOT as rt
from constants.mass4lErr_binedges import RelMassErrBinEdges, finalstate_dct
from Utils_ROOT.ROOT_classes import make_TH1F, make_TH2F
from pprint import pprint

redbkg_SR_formula_str         = r"N_{SR}^{RedBkg}"
redbkg_SR_formula_str_3P1F    = r"#sum_{i}^{N_{3P1F}^{Data}}#frac{f^{i}}{1-f^{i}}"
redbkg_SR_formula_str_3P1F_ZZ = r"w_{ZZ}#sum_{j}^{N_{3P1F}^{ZZ}}#frac{f^{j}}{1-f^{j}}"
# redbkg_SR_formula_str_2P2F    = r"#sum_{k}^{N_{2P2F}^{Data}}#left(#frac{f^{k}_{3}}{1-f^{k}_{3}}#right)"
# redbkg_SR_formula_str_2P2F   += r"#left(#frac{f^{k}_{4}}{1-f^{k}_{4}}#right)"
redbkg_SR_formula_str_2P2F    = r"#sum_{k}^{N_{2P2F}^{Data}}#frac{f^{k}_{3}}{1-f^{k}_{3}}"
redbkg_SR_formula_str_2P2F   += r"#frac{f^{k}_{4}}{1-f^{k}_{4}}"
redbkg_SR_formula_str_tot = (
    f"{redbkg_SR_formula_str} = {redbkg_SR_formula_str_3P1F}"
    f" - {redbkg_SR_formula_str_3P1F_ZZ}"
    f" - {redbkg_SR_formula_str_2P2F}"
    )

class RedBkgEstimator:
    """A class to make hists, rootfiles, and fits of reducible background."""

    def __init__(self, finalstate_dct, fs, relmass4lErr_bin_str=None):
        """
        TODO: Finish docstring.

        Parameters
        ----------
        fs : str
            Final state of 4l. Must be one of:
            '4e', '4mu', '2e2mu', '2mu2e'
        relmass4lErr_bin_str : str or Nonetype
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'
        """
        assert fs in finalstate_dct.keys()
        self.fs = fs
        self.fs_latex = fs.replace(r"mu", r"#mu")
        self.fs_code = finalstate_dct[self.fs]
        self.hist_ls = []
        self.relmass4lErr_bin_str = relmass4lErr_bin_str
        # Make a bin edge manager to parse bins, because it's confusing.
        if relmass4lErr_bin_str is not None:
            binedge_boi = RelMassErrBinEdges()
            self.binedge_tup = binedge_boi.get_edges_mass4lErr_bin(
                finalstate_dct, fs_str=fs, fs_int=None, relm4lErr_bin_code=relmass4lErr_bin_str
                )
            
    def make_hist_name(self, branch, dim=1):
        """Return an internal name of hist specific to this estimator."""
        name = f"h{dim}_{branch}_{self.fs}_relm4lerrbin{self.relmass4lErr_bin_str}"
        name = name.replace("/", "DivBy")
        name = name.replace(".", "p")
        name = name.replace(":", "_vs_")
        return name

    def make_cut_str_finalstate(self):
        """Return a string where (`finalState == self.finalstate_code)`."""
        return f"finalState == {int(self.fs_code)}"

    def make_cut_str_relmasserr(self, branch_numer, branch_denom):
        """Return a string where (`finalState == self.finalstate_code)`."""
        m4lErr_cut_lo = f"{self.binedge_tup[0]} <= {branch_numer}/{branch_denom}"
        m4lErr_cut_hi = f"{branch_numer}/{branch_denom} < {self.binedge_tup[1]}"        
        return f"""({m4lErr_cut_lo}) * ({m4lErr_cut_hi})"""

    # def make_relmasserr_bin_str(self, weight="1", no_relm4l_cuts=False):
    #     """Return a string of cuts to apply per event.
        
    #     Parameters
    #     ----------
    #     weight
    #     """
    #     weight = "is3P1F*weight_fr - is3P1F_zz*weight_fr - is2P2F*weight_fr"

    #     # weight_gteq_zero = f"({weight}) >= 0"

    #     # ^This `>= 0` cut was not applied correctly.
    #     # We SHOULD keep negative weights per event.
    #     # AFTER the hist is filled, then set negative weights to 0.
    #     # fs_cut = f"finalState == {int(self.fs_code)}"
    #     if no_relm4l_cuts:
    #         # return f"""({weight}) * ({weight_gteq_zero}) * ({fs_cut})"""
    #         return f"""({weight}) * ({fs_cut})"""
    #     m4lErr_cut_lo = f"{self.binedge_tup[0]} <= mass4lErrREFIT_vtx_BS/mass4lREFIT_vtx_BS"
    #     m4lErr_cut_hi = f"mass4lErrREFIT_vtx_BS/mass4lREFIT_vtx_BS < {self.binedge_tup[1]}"
    #     # return f"""({weight}) * ({weight_gteq_zero}) * ({fs_cut}) * ({m4lErr_cut_lo}) * ({m4lErr_cut_hi})"""
    #     return f"""({weight}) * ({fs_cut}) * ({m4lErr_cut_lo}) * ({m4lErr_cut_hi})"""

    def make_hist(self, tree, branch, branch_plotinfo_dct, dim=1, intern_name_suffix=None, per_event_weight="1",
                  draw_hist=True, draw_opt="hist", cut_on_finalstate=True, cut_on_relmasserrbin=True,
                  n_bins=None, x_lim=None, x_max_last_bin=False, show_stats=True,
                  normalize_col=False, set_negweights_to_zero=True, verbose=False,
                  printer=None, outpath_pdf=None):
        """Return a filled TH1F from selected events in `tree`, `branch`.
        
        TODO: Finish docstring.

        Parameters
        ----------
        tree : TTree
        branch : str
            Branch in TTree.
        plotting_info : dict
            Example:
            {"title":None, "n_bins":70,
            "xlabel":r"m_{4l}^{refit}", "x_min":105, "x_max":140, "ylabel":None, "y_min":None, "y_max":None, "units":"GeV"}
        per_event_weight : str
            Default weight is 1. You can use logical expressions here to
            weight each event. Example:
                "(is3P1F * weightwithFRratios) - ((is3P1F && isMCzz) * weightwithFRratios) - (is2P2F * weightwithFRratios)"
        x_lim : 2-elem list
            [x_min, x_max] for plotting.
            If None, will default to values in `branch_plotinfo_dct`.
        x_max_last_bin : bool
            If True, then set the x_max for plotting at the right edge of the
            last bin.
        # x_min : float
        #     Min x-val to plot.
        #     If None, then will default to value in `branch_plotinfo_dct`.
        # x_max : float
        #     Max x-val to plot.
        #     If None, then will default to value in `branch_plotinfo_dct`.
        no_relm4l_cuts : bool
            If False, then apply relative m4l error cut per event.
        dim : int
            The dimension of the histogram to return.
            1 : 1-D hist (TH1F)
            2 : 2-D hist (TH2F)
        """
        plotting_info = branch_plotinfo_dct[branch]
        if cut_on_finalstate:
            per_event_weight += f" * ({self.make_cut_str_finalstate()})"
        if cut_on_relmasserrbin:
            relmasserr_cut = self.make_cut_str_relmasserr(branch_numer="mass4lErrREFIT_vtx_BS", branch_denom="mass4lREFIT_vtx_BS")
            per_event_weight += f" * ({relmasserr_cut})"
        if x_lim is None:
            # Use defaults for this branch.
            x_min = plotting_info["x_min"]
            x_max = plotting_info["x_max"]
        else:
            x_min = x_lim[0]
            x_max = x_lim[1]
        if n_bins is None:
            n_bins = plotting_info["n_bins"]
        internal_name = f"{self.make_hist_name(branch, dim=1)}_xmin{x_min}_x_max{x_max}"
        xlabel = plotting_info["xlabel"]
        xlabel = xlabel.replace("4l", self.fs_latex)
        if verbose:
            print("plotting info:")
            pprint(plotting_info)
            print(f"per_event_weight: {per_event_weight}")
            print(f"x_min, x_max: {(x_min, x_max)}")
            print(f"internal_name: {internal_name}")
        if intern_name_suffix is not None:
            internal_name += intern_name_suffix
        title  = f"{self.binedge_tup[0]:.4f} < "
        title += r'#deltam_{4l}/m_{4l} '
        title = title.replace('4l', f'{self.fs_latex}')
        title += f"< {self.binedge_tup[1]:.4f} "
        title += f"(bin {self.relmass4lErr_bin_str})"
        if dim == 1:
            h = make_TH1F(internal_name=internal_name, title=title, n_bins=n_bins,
                        xlabel=xlabel, x_min=x_min, x_max=x_max,
                        ylabel=plotting_info["ylabel"], y_min=plotting_info["y_min"], y_max=plotting_info["y_max"], units=plotting_info["units"])
        elif dim == 2:
            h = make_TH2F(internal_name, title=title,
                        n_binsx=plotting_info["n_bins_x"], x_label=xlabel,
                        x_units=plotting_info["x_units"],  x_min=x_min, x_max=x_max,
                        n_binsy=plotting_info["n_bins_y"], y_label=plotting_info["ylabel"],
                        y_units=plotting_info["y_units"],  y_min=plotting_info["y_min"], y_max=plotting_info["y_max"],
                        z_min=None, z_max=None, z_label_size=None,
                        n_contour=100)
            # if normalize_col:
            #     # Make TH1D of y-bins for a Indicate x-bin range.
            #     h_proj = h.ProjectionY(f"{internal_name}_proj", 1, plotting_info["n_bins_x"], "e")

                # rt.gInterpreter.ProcessLine(cpp_str_normalize_th2f_col)  # or try: gInterpreter.Declare(cpp_code)
                # rt.TH2F_treatment(h)  # Returns 9.
        if not show_stats:
            h.SetStats(0)
        # if not draw_hist:
        draw_opt = f"{draw_opt} goff"
        tree.Draw(f"{branch}>>{internal_name}", per_event_weight, draw_opt)
        # Now that hist is filled, set negative weights to zero.
        if set_negweights_to_zero:
            for bin_num in range(1, h.GetNbinsX()+1):
                if h.GetBinContent(bin_num) < 0:
                    h.SetBinContent(bin_num, 0)
        if draw_hist:
            h.Draw(draw_opt)
        integ = h.Integral()
        tex = rt.TLatex()
        tex.SetNDC()
        tex.SetTextSize(0.02)
        # tex.SetTextColor(rt.kRed)
        integ_info = r"%s: %.3f events" % (redbkg_SR_formula_str_2P2F, integ)
        tex.DrawLatex(0.5, 0.85, integ_info)
        if x_max_last_bin:
            # Set the x_max for plotting equal to the right edge of last bin.
            last_bin_num = h.FindLastBinAbove(0)
            # Move one bin over to include last filled bin.
            x_val_right_edge = h.GetBinLowEdge(last_bin_num + 1)
            h.GetXaxis().SetRangeUser(x_min, x_val_right_edge)
        if draw_hist:
            printer.canv.Print(outpath_pdf)
        return h
