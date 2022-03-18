import os
import ROOT
import numpy as np
from ROOT import TColor
from helpers.analyzeZX import setCavasAndStyles, get_evt_weight
from constants.finalstates import (
    dct_finalstates_latex, dct_finalstates_str2int
    )
from constants.analysis_params import (
    LUMI_INT_2016_UL, LUMI_INT_2017_UL, LUMI_INT_2018_UL,
    dct_xs_jake,
    dct_sumgenweights_2016_UL,
    dct_sumgenweights_2017_UL,
    dct_sumgenweights_2018_UL
    )
from Utils_ROOT.ROOT_classes import make_TH1F, make_pave
from Utils_ROOT.Printer import CanvasPrinter
from Utils_Python.Utils_Files import check_overwrite, make_dirs
from Utils_Python.printing import announce

year = 2016
lumi = LUMI_INT_2016_UL  # 1/pb
dct_sumgenwgts = dct_sumgenweights_2016_UL
dct_xs = dct_xs_jake

x_lim = [70, 870.0]  # GeV.  [70.0, 170.0]
bin_width = 20  # GeV.

control_regions = ['3P1F']#, '2P2F']
final_states = ['4mu']#, '4e', '2e2mu', '2mu2e']

outfile_path = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/plots/test/data_2016_3p1f.pdf"
overwrite = 1

dct_samples = {
    "Data": "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/skim_osmethodnew_2016_Data.root",
}

dct_plot_info = {
    # AN-19-139v6 colors (p.64), AN-16-442 colors (p.44):
    # 2P2F extr.     = #ff0103 (red),        #fe01ff (hot pink)
    # WZ             = #ff50ff (hot pink),   #fe01ff (hot pink)
    # Zgammastar, ZZ = #00d0ce (sky blue),   #0497ff (deep sky blue)
    # Z + jets       = #009d00 (dark green), #85c2a2 (pastel green)
    # ttbar + jets   = #3f20ff (blue),       #5953d9 (violet)
    "Data" : {
        "label" : "Data",
        "fillcolor" : 4,  # Sky blue.
        "linecolor": 1,  # Dark blue.
        "leg_opts": "lp"
        },
    "ZZ" : {
        "label" : "#Z\\gamma^*, ZZ#",
        "fillcolor" : "#99ccff",  # Sky blue.
        "linecolor": "#000099",  # Dark blue.
        "leg_opts": "f"
        },
    "WZ" : {
        "label" : "#WZ#",
        "fillcolor" : "#cc0099",  # Dark pink.
        "linecolor" : "#990066",  # Another dark pink
        "leg_opts": "f"
        },
    "TT" : {
        "label" : "#t\\bar{t}+jets#",
        "fillcolor" : "#996666",  # Brown.
        "linecolor" : "#5f3f3f",  # Another brown.
        "leg_opts": "f"
        },
    "DY50" : {
        "label" : "#Z+jets#",
        "fillcolor" : "#669966",  # Army green.
        "linecolor" : "#003300",  # Super dark green.
        "leg_opts": "f"
        }
    # "Data" : Sample(
    #             filepath="/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/nolepFSRtocalc_mZ1/estimateZX_Data.root",
    #             label="Data",
    #             sample_type="Data",
    #             isData=True,
    #          ),
}

class Sample:

    def __init__(self, filepath, label, sample_type, isData):
        self.filepath = filepath
        self.label = label
        self.sample_type = sample_type
        self.isData = isData

class ControlRegPlot:
    """Makes a single mass4l plot with all samples drawn to same canvas.
    
    It should take in the following samples:
        - Data
        - WZ
        - ttbar
        - DY
        - ZZ
    """

    def __init__(
        self, controlreg, finalstate, year, lumi,
        dct_xs, dct_sumgenwgts,
        x_lim, bin_width,
        ):
        assert controlreg in ("2P2F", "3P1F", "4P0F")
        assert finalstate in ("", "4e", "4mu", "2e2mu", "2mu2e")
        assert year in (2016, 2017, 2018)

        self.controlreg = controlreg
        self.finalstate_str = finalstate
        self.finalstate = dct_finalstates_str2int[finalstate]
        self.finalstate_str_latex = dct_finalstates_latex[finalstate]
        self.year = year
        self.x_lim = x_lim
        self.bin_width = bin_width
        self.lumi = lumi
        self.dct_xs = dct_xs

        # Stack MC hists.
        self.h_stack = self.make_hstack()

        self.data_plot = None
        self.hist_ls = []
        self.label_ls = []

    def get_names_assoc_hists(self):
        """Return a list of strings of hist names associated with this CRP."""
        return [h.name for h in self.hist_ls]
        
    def make_hstack(self):
        """Return a THStack with a TH1 already set to it."""
        h_stack = ROOT.THStack(self.get_str_cr_fs_yr(), self.get_str_cr_fs_yr())
        h_addtostack = ROOT.TH1F(
            f"h_addtostack_{self.get_str_cr_fs_yr()}",  # Internal name.
            self.get_str_cr_fs_yr(title_friendly=True), # Title.
            100, 0, 2000
            )
        h_addtostack.SetMinimum(-5.608576)
        h_addtostack.SetMaximum(51.10072)
        h_addtostack.SetDirectory(0)
        h_addtostack.SetStats(0)
        h_addtostack.SetLineColor(TColor.GetColor("#000099"))  # Dark blue.
        h_addtostack.SetLineStyle(0)
        h_addtostack.SetMarkerStyle(20)  # Black data points.
        h_addtostack.GetXaxis().SetLabelFont(42)
        h_addtostack.GetXaxis().SetLabelOffset(0.007)
        h_addtostack.GetXaxis().SetLabelSize(0.05)
        h_addtostack.GetXaxis().SetTitleSize(0.06)
        h_addtostack.GetXaxis().SetTitleOffset(0.9)
        h_addtostack.GetXaxis().SetTitleFont(42)
        h_addtostack.GetYaxis().SetLabelFont(42)
        h_addtostack.GetYaxis().SetLabelOffset(0.007)
        h_addtostack.GetYaxis().SetLabelSize(0.05)
        h_addtostack.GetYaxis().SetTitleSize(0.06)
        h_addtostack.GetYaxis().SetTitleOffset(1.25)
        h_addtostack.GetYaxis().SetTitleFont(42)
        h_addtostack.GetZaxis().SetLabelFont(42)
        h_addtostack.GetZaxis().SetLabelOffset(0.007)
        h_addtostack.GetZaxis().SetLabelSize(0.05)
        h_addtostack.GetZaxis().SetTitleSize(0.06)
        h_addtostack.GetZaxis().SetTitleFont(42)

        h_stack.SetHistogram(h_addtostack)
        return h_stack

    def make_hist_from_sample(
        self, nickname, filepath, treepath='passedEvents',
        ):
        """Create and fill hist (either Data or MC) in CR and fs.
        
        Add MC hist to self.h_stack. Also append hist to self.hist_ls.
        """
        print(f"Opening file: {os.path.basename(filepath)}")
        f = ROOT.TFile.Open(filepath, 'read')
        t = f.Get(treepath)
        if not t:
            raise ValueError("Problem opening TTree.")
        x_min = self.x_lim[0]
        x_max = self.x_lim[1]
        n_bins = round((x_max - x_min) / bin_width)

        h_name = f"h_{self.get_str_cr_fs_yr()}"
        h_title = self.get_str_cr_fs_yr(title_friendly=True)
        h = make_TH1F(
            h_name, title="", n_bins=n_bins,
            xlabel=self.finalstate_str_latex, x_min=x_min, x_max=x_max,
            ylabel=None, y_min=None, y_max=None,
            units="GeV", sum_squared_weights=True
            )

        # print(f"{smpl_type} {Nickname}: {self.get_str_cr_fs_yr(title_friendly=True)}, integral = {hist.Integral()}")

        cr = self.controlreg
        fs = self.finalstate
        cuts = f"(is{cr} && finalState == {fs})"

        isData = (nickname == "Data")
        if isData:
            # Count raw 3P1F or 2P2F events.
            evtwgt = 1
        else:
            # MC so must weight each event using xs, L_int, and sumGenWgts.
            xs = self.dct_xs[nickname]
            n_exp = xs * self.lumi
            sum_gen_wgts = self.dct_sumgenwgts[nickname]
            evtwgt = f"eventWeight * {n_exp} / {sum_gen_wgts}"
            if nickname == "ZZ":
                evtwgt = f"{evtwgt} * k_qqZZ_qcd_M * k_qqZZ_ewk"
        
        print(f"h.Integral() before tree.Draw(): {h.Integral()}")
        print(f"Making hist with cuts and evtwgt:\n  {cuts}\n  {evtwgt}")
        print(f"{t.GetEntries(f'mass4l > 105 && mass4l < 140 &&  {cuts} ')}")
        t.Draw(
            f"mass4l >> {h_name}",
            f"({cuts}) * {evtwgt}",
            )
        h = ROOT.gDirectory.Get(h_name)
        h.SetDirectory(0)

        print(f"h.Integral() after tree.Draw(): {h.Integral()}")

        h.nickname = nickname
        self.hist_ls.extend(
            (h,)
            )
        if isData:
            h.SetMarkerStyle(20)
            self.data_plot = h
        else:
            self.h_stack.Add(h)

        # self.store_hist(h_rebin, dct_samples, nickname)

    def make_legend(self, canv):
        """
        Store a filled-out legend.

        canv : TCanvas
        """
        # TODO: Implement pave to have SetTextSize(0.04)
        # and show CR and FS info.
        # Legend text should be around 0.03.
        xmin = 0.5
        xmax = 0.90
        ymax_leg = 0.8
        # pave = make_pave(xmin=xmin, ymin=0.8, xmax=0.90, ymax=0.9)
        txt = (
            f"Control Region: {self.controlreg}\n"
            f"Final State: {self.finalstate_str_latex}"
        )
        top, bot = txt.split("\n")
        txt = "#splitline{" + top + "}{" + bot + "}"
        leg = ROOT.TLegend(xmin, 0.6, xmax, ymax_leg, txt)

        leg.SetBorderSize(0)
        leg.SetLineColor(1)
        leg.SetLineStyle(1)
        leg.SetLineWidth(1)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetTextSize(0.03)

        for h in self.hist_ls:
            nickname = h.nickname
            label_latex = dct_plot_info[nickname]["label"]
            leg_opts = dct_plot_info[nickname]["leg_opts"]
            fillcolor = dct_plot_info[nickname]["fillcolor"]

            entry = leg.AddEntry("NULL", label_latex, leg_opts)
            entry.SetFillColor(fillcolor)

        # entry.SetLineColor(1)
        # entry.SetLineStyle(1)
        # entry.SetLineWidth(1)
        # entry.SetMarkerColor(1)
        # entry.SetMarkerStyle(21)
        # entry.SetMarkerSize(1)
        # entry.SetTextFont(62)
        
        # # Data.
        # entry = leg.AddEntry("NULL", "Data", "LP")
        # # Z+jets.
        # entry.SetLineColor(1)
        # entry.SetLineStyle(1)
        # entry.SetLineWidth(1)
        # entry.SetMarkerColor(1)
        # entry.SetMarkerStyle(20)
        # entry.SetMarkerSize(1)
        # entry.SetTextFont(42)
        # entry = leg.AddEntry("NULL","Z + jets","F")
        
        # canv = TColor.GetColor("#669966")
        # entry.SetFillColor(canv)
        # entry.SetFillStyle(1001)
        # # ttbar.
        # canv = TColor.GetColor("#003300")
        # entry.SetLineColor(canv)
        # entry.SetLineStyle(1)
        # entry.SetLineWidth(1)
        # entry.SetMarkerColor(1)
        # entry.SetMarkerStyle(21)
        # entry.SetMarkerSize(1)
        # entry.SetTextFont(42)
        # entry=leg.AddEntry("NULL","t#bar{t} + jets","F")
        
        # canv = TColor.GetColor("#996666")
        # entry.SetFillColor(canv)
        # entry.SetFillStyle(1001)
        # # WZ.
        # canv = TColor.GetColor("#5f3f3f")
        # entry.SetLineColor(canv)
        # entry.SetLineStyle(1)
        # entry.SetLineWidth(1)
        # entry.SetMarkerColor(1)
        # entry.SetMarkerStyle(21)
        # entry.SetMarkerSize(1)
        # entry.SetTextFont(42)
        # entry=leg.AddEntry("NULL","WZ","F")
        
        # canv = TColor.GetColor("#cc0099")
        # entry.SetFillColor(canv)
        # entry.SetFillStyle(1001)
        # # Zgammastar, ZZ.
        # canv = TColor.GetColor("#990066")
        # entry.SetLineColor(canv)
        # entry.SetLineStyle(1)
        # entry.SetLineWidth(1)
        # entry.SetMarkerColor(1)
        # entry.SetMarkerStyle(21)
        # entry.SetMarkerSize(1)
        # entry.SetTextFont(42)
        # entry = leg.AddEntry("NULL","Z#gamma*,ZZ","F")
        
        # canv = TColor.GetColor("#99ccff")
        # entry.SetFillColor(canv)
        # entry.SetFillStyle(1001)
        
        # # If control region = 3P1F.
        # if "3P1F" in self.controlreg:
        #     canv = TColor.GetColor("#000099")
        #     entry.SetLineColor(canv)
        #     # entry.SetLineStyle(1)
        #     # entry.SetLineWidth(1)
        #     # entry.SetMarkerColor(1)
        #     # entry.SetMarkerStyle(21)
        #     # entry.SetMarkerSize(1)
        #     # entry.SetTextFont(42)
        #     entry=leg.AddEntry("NULL", "2P2F contribution", "F")
        #     entry.SetFillStyle(4000)
        #     entry.SetLineColor(6)
        #     entry.SetLineStyle(1)
        #     entry.SetLineWidth(2)
        #     entry.SetMarkerColor(1)
        #     entry.SetMarkerStyle(21)
        #     entry.SetMarkerSize(1)
        #     entry.SetTextFont(42)
        self.leg = leg

    def get_str_cr_fs_yr(self, title_friendly=False):
        """Return control region, final state, and year as a string."""
        words = f"{self.year}_{self.controlreg}_{self.finalstate}"
        words = words.rstrip("_")
        if title_friendly:
            words = words.replace("_", " ")
        return words
        
    def draw_data_plot(self):
        """Pretty up the Data hist and draw it to the open canvas.
        
        Parameters
        ----------
        x_lim : 2-elem list
            [x_min, x_max] for plotting.
        bin_width : float
        """
        data = self.data_plot

        data.SetFillColor(1)
        data.SetLineColor(1)
        data.SetFillStyle(0)
        data.SetMarkerStyle(20)
        # x axis.
        # data.GetXaxis().SetTitle("m_{4#font[12]{l}} (GeV)")
        # data.GetXaxis().SetRange(3,40)
        # data.GetXaxis().SetLabelFont(42)
        # data.GetXaxis().SetLabelSize(0.05)
        # data.GetXaxis().SetTitleSize(0.06)
        # data.GetXaxis().SetTitleOffset(0.9)
        # data.GetXaxis().SetTitleFont(42)
        # y axis.
        # data.GetYaxis().SetTitle(f"Events / ({bin_width} GeV)")
        # data.GetYaxis().SetLabelFont(42)
        # data.GetYaxis().SetLabelSize(0.05)
        # data.GetYaxis().SetTitleSize(0.06)
        # data.GetYaxis().SetTitleOffset(1.25)
        # data.GetYaxis().SetTitleFont(42)
        # z axis.
        # data.GetZaxis().SetLabelFont(42)
        # data.GetZaxis().SetLabelSize(0.035)
        # data.GetZaxis().SetTitleSize(0.035)
        # data.GetZaxis().SetTitleFont(42)
        
        # data.GetXaxis().SetRangeUser(50,800)
        data.GetXaxis().SetRangeUser(self.x_lim[0], self.x_lim[1])
        glb_max = max([h.GetMaximum() for h in self.hist_ls])
        data.GetYaxis().SetRangeUser(0, 1.2 * glb_max)
        # data.GetYaxis().SetRangeUser(0.5, 80000)
        # data.GetYaxis().SetRangeUser(0.5, 2*glb_max)
        data.Draw("e1")
        self.h_stack.Draw("hist same")
        data.Draw("same e1")
        ROOT.gPad.RedrawAxis()

    def draw_legend(self):
        """Draw `self.leg` and store TLatex object as `self.tex`."""
        ymax = 0.91

        opt = "same" #"same"
        self.leg.Draw(opt)

        tex1 = ROOT.TLatex(0.95, ymax, r"%.1f fb^{-1} (13 TeV)" % (self.lumi / 1000.0))
        tex1.SetNDC()
        tex1.SetTextAlign(31)
        tex1.SetTextFont(42)
        tex1.SetTextSize(0.03)
        tex1.SetLineWidth(2)
        tex1.Draw(opt)
        self.tex1 = tex1

        tex2 = ROOT.TLatex(0.15, ymax, "CMS")
        tex2.SetNDC()
        tex2.SetTextFont(61)
        tex2.SetTextSize(0.0375)
        tex2.SetLineWidth(2)
        tex2.Draw(opt)
        self.tex2 = tex2

        tex = ROOT.TLatex(0.24, ymax, "Preliminary")
        tex.SetNDC()
        tex.SetTextFont(52)
        tex.SetTextSize(0.0285)
        tex.SetLineWidth(2)
        tex.Draw(opt)
        self.tex = tex

    def add_2P2F_hist(self, estimateZX_Data_file):
        file2p2f = ROOT.TFile(estimateZX_Data_file, "READ")
        histname = f"h1D_m4l_Add_{self.get_str_cr_fs_yr()}"
        histPlot2p2f = file2p2f.Get(histname)
        print(f"2P2F contribution = {histPlot2p2f.Integral()}") 
        print("Adding ZZ and WZ to the 2P2F CR in 3P1F")
        histPlot2p2f.Add(self.hist_ls[1])  # This is sloppy. Fix later.
        histPlot2p2f.Add(self.hist_ls[2])
        histPlot2p2f.SetFillColor(TColor.GetColor("#ffffff"))  # White.
        histPlot2p2f.SetLineColor(TColor.GetColor("#ff00ff"))  # Pink.
        histPlot2p2f.SetLineWidth(2)
        histPlot2p2f.SetFillStyle(4000)
        histPlot2p2f.Smooth()
        histPlot2p2f.Draw("hist E1 same goff")

    # def make_plot_from_samples(self, canv, dct_samples, x_lim, bin_width, lumi, estimateZX_Data_file):
    def make_plot_from_samples(self, canv):
        """Draw all hists associated with this CRP. Makes 1 stack plot.

        If Data hist exists, then draws Data (not stacked) as black points.
        
        Parameters
        ----------
        canv
        dct_samples
        x_lim : 2-elem list
            [x_min, x_max] for plotting.
        bin_width : float
        lumi
        estimateZX_Data_file
        """
        # n_bins = int((x_lim[1] - x_lim[0]) / bin_width)
        # newbins = np.linspace(x_lim[0], x_lim[1], n_bins + 1)

        # self.h_stack = self.make_hstack()

        # for nickname in dct_samples.keys():
        #     h = self.get_hist(dct_samples, nickname)
        #     h_rebin = h.Rebin(len(newbins)-1, f"{h.GetName()}_rebin", newbins)
        #     self.store_hist(h_rebin, dct_samples, nickname)

        self.make_legend(canv)
        if self.data_plot is not None:
            self.draw_data_plot()
        # if "3P1F" in self.controlreg:
        #     self.add_2P2F_hist(estimateZX_Data_file=estimateZX_Data_file)
        self.draw_legend()

def show_obj_info(msg="", obj=None):
    print(f"[INFO] {msg}: obj={obj}, type={type(obj)}")

def make_pretty_canvas():
    """Return a prettied-up TCanvas."""
    ROOT.gROOT.SetBatch(True)
    c = ROOT.TCanvas("canv", "myPlots",0,67,600,600)
    setCavasAndStyles("canv",c,"")   
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    # canv.Range(-102.5,-10.38415,847.5,69.4939) 
    c.Range(0,-10.38415,847.5,69.4939)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetBorderSize(2)
    c.SetLeftMargin(0.15)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.13)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetTickx(1)
    c.SetTicky(1)
    c.SetLogy()
    return c

def make_pdf_osmethod_hists(
    control_regions, final_states,
    dct_samples, dct_xs, dct_sumgenwgts,
    outfile_path, year, lumi,
    x_lim,
    bin_width,
    overwrite=False,
    ):
    make_dirs(os.path.dirname(outfile_path))
    check_overwrite(outfile_path, overwrite=overwrite)

    # canv = make_pretty_canvas()
    prntr = CanvasPrinter(show_statsbox=False)
    # gROOT.ForceStyle()

    canv = prntr.canv
    canv.Print(outfile_path + "[")

    print(
        f"Year:            {year}\n"
        f"L_int:           {lumi / 1000.0}\n"
        f"Control Regions: {control_regions}\n"
        f"Final States:    {final_states}"
        )
    for cr in control_regions:
        for fs in final_states:
            announce(f"{cr} {fs}")
            crp = ControlRegPlot(
                controlreg=cr, finalstate=fs, year=year,
                x_lim=x_lim, bin_width=bin_width, lumi=lumi,
                dct_xs=dct_xs, dct_sumgenwgts=dct_sumgenwgts,
                )

            for nickname, filepath in dct_samples.items():
                assert str(year) in filepath
                crp.make_hist_from_sample(
                    nickname, filepath, treepath='passedEvents'
                    )
            # End loop over any samples provided.

            crp.make_plot_from_samples(canv=canv)
            # canv.UseCurrentStyle()
            canv.Print(outfile_path)
    canv.Print(outfile_path + "]")

if __name__ == "__main__":
    make_pdf_osmethod_hists(
        control_regions=control_regions, final_states=final_states,
        dct_samples=dct_samples, dct_xs=dct_xs, dct_sumgenwgts=dct_sumgenwgts,
        outfile_path=outfile_path, year=year, lumi=lumi,
        x_lim=x_lim,
        bin_width=bin_width,
        overwrite=overwrite,
        )

    # def get_hist(self, dct_samples, Nickname):
    #     """Return hist from infile. If hist is MC, make it pretty."""
    #     # infile = dct_samples[Nickname]["filepath"]
    #     # isData = dct_samples[Nickname]["isData"]
    #     f = ROOT.TFile(infile, "READ")

    #     histname = f"h1D_mass4l_{self.get_str_cr_fs_yr()}"
    #     if len(self.finalstate) == 0:
    #         histname += "_inclus"
    #     hist = f.Get(histname).Clone()
    #     hist.SetDirectory(0)
    #     lastbin = hist.GetNbinsX()
    #     lowedgelastbin = hist.GetBinLowEdge(lastbin)
    #     highedge = lowedgelastbin + hist.GetBinWidth(lastbin)
    #     print(f"Low_xbin={hist.GetBinLowEdge(1)}, High_xbin={highedge}") 

    #     if not isData:
    #         fillcolor = dct_samples[Nickname]["fillcolor"]
    #         linecolor = dct_samples[Nickname]["linecolor"]
    #         hist.SetFillColor(TColor.GetColor(fillcolor))
    #         hist.SetLineColor(TColor.GetColor(linecolor))
    #         hist.SetFillStyle(1001)
    #         hist.SetLineStyle(0)
    #         hist.SetMarkerStyle(20)
    #         # x axis.
    #         hist.GetXaxis().SetLabelFont(42)
    #         hist.GetXaxis().SetLabelOffset(0.007)
    #         hist.GetXaxis().SetLabelSize(0.05)
    #         hist.GetXaxis().SetTitleSize(0.06)
    #         hist.GetXaxis().SetTitleOffset(0.9)
    #         hist.GetXaxis().SetTitleFont(42)
    #         # y axis.
    #         hist.GetYaxis().SetLabelFont(42)
    #         hist.GetYaxis().SetLabelOffset(0.007)
    #         hist.GetYaxis().SetLabelSize(0.05)
    #         hist.GetYaxis().SetTitleSize(0.06)
    #         hist.GetYaxis().SetTitleOffset(1.25)
    #         hist.GetYaxis().SetTitleFont(42)
    #         # z axis.
    #         hist.GetZaxis().SetLabelFont(42)
    #         hist.GetZaxis().SetLabelOffset(0.007)
    #         hist.GetZaxis().SetLabelSize(0.05)
    #         hist.GetZaxis().SetTitleSize(0.06)
    #         hist.GetZaxis().SetTitleFont(42)
    #     f.Close()
    #     return hist