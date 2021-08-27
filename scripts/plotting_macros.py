import os
import ROOT
import numpy as np
from ROOT import TColor
from helpers.analyzeZX import setCavasAndStyles
from constants.physics import LUMI_INT_2018_Jake
from Utils_Python.Utils_Files import check_overwrite

x_lim = [70.0, 170.0]  # GeV.
bin_width = 5  # GeV.
lumi = LUMI_INT_2018_Jake / 1000.0
overwrite = 0

estimateZX_Data_file = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/estimateZX_Data.root"
# outfile_path = "/blue/avery/rosedj1/ZplusXpython/plots/hist_controlreg/CR_OS_2P2F_4e.pdf"
outfile_path = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/plots/CR_OS_2P2F_4e.pdf"

sample_dct = {
    # Nickname : {"filepath", "label", "fillcolor", "linecolor", "isData"}
    "Data" : {
        "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210723_alljake/Hist_Data.root",
        "label" : "Data",
        "sample" : "Data",
        "isData" : True,
        },
    "ZZ" : {
        "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210723_alljake/Hist_MC_ZZ.root",
        "label" : "#Z\\gamma^*, ZZ#",
        "fillcolor" : "#99ccff",  # Sky blue.
        "linecolor" : "#000099",  # Dark blue.
        "sample" : "MC",
        "isData" : False,
        },
    "WZ" : {
        "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210723_alljake/Hist_MC_WZ-ext1-v2.root",
        "label" : "#WZ#",
        "fillcolor" : "#cc0099",  # Dark pink.
        "linecolor" : "#990066",  # Another dark pink
        "sample" : "MC",
        "isData" : False,
        },
    "TT" : {
        "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210723_alljake/Hist_MC_TT.root",
        "label" : "#t\\bar{t}+jets#",
        "fillcolor" : "#996666",  # Brown.
        "linecolor" : "#5f3f3f",  # Another brown.
        "sample" : "MC",
        "isData" : False,
        },
    "DY50" : {
        "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210723_alljake/Hist_MC_DY50.root",
        "label" : "#Z+jets#",
        "fillcolor" : "#669966",  # Army green.
        "linecolor" : "#003300",  # Super dark green.
        "sample" : "MC",
        "isData" : False,
        }
}

class ControlRegPlot:
    """Makes a single mass4l plot with all samples drawn to same canvas.
    
    It should take in the following samples:
    - Data
    - WZ
    - ttbar
    - DY
    - ZZ
    """

    def __init__(self, controlreg, finalstate=""):
        assert controlreg in ("2P2F", "3P1F", "4P0F")
        assert finalstate in ("", "4e", "4mu", "2e2mu", "2mu2e")
        self.controlreg = controlreg
        self.finalstate = finalstate
        self.h_stack = None
        self.dataPlot = None
        self.hist_ls = []

    def make_title(self):
        return f"Control Region {self.get_cr_fs_str(title_friendly=True)}"

    def make_legend(self, canv):
        """
        Store a filled-out legend.

        canv : TCanvas
        """
        # CR.
        # leg = ROOT.TLegend(0.45, 0.53, 1.05, 0.93)
        leg = ROOT.TLegend(0.2, 0.53, 0.80, 0.93)
        leg.SetBorderSize(0)
        leg.SetLineColor(1)
        leg.SetLineStyle(1)
        leg.SetLineWidth(1)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        entry = leg.AddEntry("NULL", self.make_title(), "h")
        # Data.
        entry.SetLineColor(1)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(62)
        entry = leg.AddEntry("NULL","Data","LP")
        # Z+jets.
        entry.SetLineColor(1)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(20)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry = leg.AddEntry("NULL","Z + jets","F")
        
        canv = TColor.GetColor("#669966")
        entry.SetFillColor(canv)
        entry.SetFillStyle(1001)
        # ttbar.
        canv = TColor.GetColor("#003300")
        entry.SetLineColor(canv)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry=leg.AddEntry("NULL","t#bar{t} + jets","F")
        
        canv = TColor.GetColor("#996666")
        entry.SetFillColor(canv)
        entry.SetFillStyle(1001)
        # WZ.
        canv = TColor.GetColor("#5f3f3f")
        entry.SetLineColor(canv)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry=leg.AddEntry("NULL","WZ","F")
        
        canv = TColor.GetColor("#cc0099")
        entry.SetFillColor(canv)
        entry.SetFillStyle(1001)
        # Zgammastar, ZZ.
        canv = TColor.GetColor("#990066")
        entry.SetLineColor(canv)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry = leg.AddEntry("NULL","Z#gamma*,ZZ","F")
        
        canv = TColor.GetColor("#99ccff")
        entry.SetFillColor(canv)
        entry.SetFillStyle(1001)
        
        # If control region = 3P1F.
        if "3P1F" in self.controlreg:
            canv = TColor.GetColor("#000099")
            entry.SetLineColor(canv)
            # entry.SetLineStyle(1)
            # entry.SetLineWidth(1)
            # entry.SetMarkerColor(1)
            # entry.SetMarkerStyle(21)
            # entry.SetMarkerSize(1)
            # entry.SetTextFont(42)
            entry=leg.AddEntry("NULL", "2P2F contribution", "F")
            entry.SetFillStyle(4000)
            entry.SetLineColor(6)
            entry.SetLineStyle(1)
            entry.SetLineWidth(2)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)
        self.leg = leg

        # If control region = 4P0F.
        if "4P0F" in self.controlreg:
            canv = TColor.GetColor("#000099")
            entry.SetLineColor(canv)
            entry.SetLineStyle(1)
            entry.SetLineWidth(1)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)
            entry=leg.AddEntry("NULL", "2P2F contribution", "F")
            entry.SetFillStyle(4000)
            entry.SetLineColor(6)
            entry.SetLineStyle(1)
            entry.SetLineWidth(2)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)
        self.leg = leg

    def get_cr_fs_str(self, title_friendly=False):
        """Return control region and final state as a string."""
        words = f"{self.controlreg}_{self.finalstate}"
        words = words.rstrip("_")
        if title_friendly:
            words = words.replace("_", " ")
        return words
        
    def make_hstack(self):
        """Return a THStack with a TH1 already set to it."""
        h_stack = ROOT.THStack(self.get_cr_fs_str(), self.get_cr_fs_str())
        h_addtostack = ROOT.TH1F(
            f"h_addtostack_{self.get_cr_fs_str()}", self.get_cr_fs_str(title_friendly=True),
            100, 0, 2000)
        h_addtostack.SetMinimum(-5.608576)
        h_addtostack.SetMaximum(51.10072)
        h_addtostack.SetDirectory(0)
        h_addtostack.SetStats(0)
        h_addtostack.SetLineColor(TColor.GetColor("#000099"))
        h_addtostack.SetLineStyle(0)
        h_addtostack.SetMarkerStyle(20)
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

    def get_hist(self, sample_dct, Nickname):
        """Return hist from infile. If hist is MC, make it pretty."""
        infile = sample_dct[Nickname]["filepath"]
        isData = sample_dct[Nickname]["isData"]

        f = ROOT.TFile(infile, "READ")

        histname = f"h1D_mass4l_{self.get_cr_fs_str()}"
        if len(self.finalstate) == 0:
            histname += "_inclus"
        hist = f.Get(histname).Clone()
        hist.SetDirectory(0)
        lastbin = hist.GetNbinsX()
        lowedgelastbin = hist.GetBinLowEdge(lastbin)
        highedge = lowedgelastbin + hist.GetBinWidth(lastbin)
        print(f"Low_xbin={hist.GetBinLowEdge(1)}, High_xbin={highedge}") 

        if not isData:
            fillcolor = sample_dct[Nickname]["fillcolor"]
            linecolor = sample_dct[Nickname]["linecolor"]
            hist.SetFillColor(TColor.GetColor(fillcolor))
            hist.SetLineColor(TColor.GetColor(linecolor))
            hist.SetFillStyle(1001)
            hist.SetLineStyle(0)
            hist.SetMarkerStyle(20)
            # x axis.
            hist.GetXaxis().SetLabelFont(42)
            hist.GetXaxis().SetLabelOffset(0.007)
            hist.GetXaxis().SetLabelSize(0.05)
            hist.GetXaxis().SetTitleSize(0.06)
            hist.GetXaxis().SetTitleOffset(0.9)
            hist.GetXaxis().SetTitleFont(42)
            # y axis.
            hist.GetYaxis().SetLabelFont(42)
            hist.GetYaxis().SetLabelOffset(0.007)
            hist.GetYaxis().SetLabelSize(0.05)
            hist.GetYaxis().SetTitleSize(0.06)
            hist.GetYaxis().SetTitleOffset(1.25)
            hist.GetYaxis().SetTitleFont(42)
            # z axis.
            hist.GetZaxis().SetLabelFont(42)
            hist.GetZaxis().SetLabelOffset(0.007)
            hist.GetZaxis().SetLabelSize(0.05)
            hist.GetZaxis().SetTitleSize(0.06)
            hist.GetZaxis().SetTitleFont(42)
        f.Close()
        return hist

    def store_hist(self, hist, sample_dct, Nickname):
        """Add MC hist to self.h_stack. Also append hist to self.hist_ls."""
        self.hist_ls.append(hist)

        smpl_type = sample_dct[Nickname]["sample"]
        isData = sample_dct[Nickname]["isData"]
        print(f"{smpl_type} {Nickname}: {self.get_cr_fs_str(title_friendly=True)}, integral = {hist.Integral()}")

        if isData:
            self.dataPlot = hist
        else:
            self.h_stack.Add(hist)

    def draw_dataplot(self, x_lim, bin_width):
        """Pretty up the Data hist and draw it to the open canvas.
        
        Parameters
        ----------
        x_lim : 2-elem list
            [x_min, x_max] for plotting.
        bin_width : float
        """
        dataPlot = self.dataPlot

        dataPlot.SetFillColor(1)
        dataPlot.SetLineColor(1)
        dataPlot.SetFillStyle(0)
        dataPlot.SetMarkerStyle(20)
        # x axis.
        dataPlot.GetXaxis().SetTitle("m_{4#font[12]{l}} (GeV)")
        dataPlot.GetXaxis().SetRange(3,40)
        dataPlot.GetXaxis().SetLabelFont(42)
        dataPlot.GetXaxis().SetLabelSize(0.05)
        dataPlot.GetXaxis().SetTitleSize(0.06)
        dataPlot.GetXaxis().SetTitleOffset(0.9)
        dataPlot.GetXaxis().SetTitleFont(42)
        # y axis.
        dataPlot.GetYaxis().SetTitle(f"Events / ({bin_width} GeV)")
        dataPlot.GetYaxis().SetLabelFont(42)
        dataPlot.GetYaxis().SetLabelSize(0.05)
        dataPlot.GetYaxis().SetTitleSize(0.06)
        dataPlot.GetYaxis().SetTitleOffset(1.25)
        dataPlot.GetYaxis().SetTitleFont(42)
        # z axis.
        dataPlot.GetZaxis().SetLabelFont(42)
        dataPlot.GetZaxis().SetLabelSize(0.035)
        dataPlot.GetZaxis().SetTitleSize(0.035)
        dataPlot.GetZaxis().SetTitleFont(42)
        
        # dataPlot.GetXaxis().SetRangeUser(50,800)
        dataPlot.GetXaxis().SetRangeUser(x_lim[0], x_lim[1])
        glb_max = max([h.GetMaximum() for h in self.hist_ls])
        # dataPlot.GetYaxis().SetRangeUser(0, 1.3 * glb_max)
        dataPlot.GetYaxis().SetRangeUser(0.5, 80000)
        # dataPlot.GetYaxis().SetRangeUser(0.5, 2*glb_max)
        dataPlot.Draw("e1 goff")
        self.h_stack.Draw("hist same")
        dataPlot.Draw("same e1 goff")
        ROOT.gPad.RedrawAxis()

    def draw_legend(self, lumi):
        """Draw `self.leg` and store TLatex object as `self.tex`."""
        opt = "goff" #"same"
        self.leg.Draw(opt)

        tex = ROOT.TLatex(0.95, 0.96, r"{%.1f} fb^{-1} (13 TeV)" % lumi)  # Or is it 59.7 fb^{-1}?
        tex.SetNDC()
        tex.SetTextAlign(31)
        tex.SetTextFont(42)
        tex.SetTextSize(0.03)
        tex.SetLineWidth(2)
        tex.Draw(opt)

        tex = ROOT.TLatex(0.15,0.96,"CMS")
        tex.SetNDC()
        tex.SetTextFont(61)
        tex.SetTextSize(0.0375)
        tex.SetLineWidth(2)
        tex.Draw(opt)

        tex = ROOT.TLatex(0.23,0.96,"Preliminary")
        tex.SetNDC()
        tex.SetTextFont(52)
        tex.SetTextSize(0.0285)
        tex.SetLineWidth(2)
        tex.Draw(opt)
        self.tex = tex

    def add_2P2F_hist(self, estimateZX_Data_file):
        file2p2f = ROOT.TFile(estimateZX_Data_file, "READ")
        histname = f"h1D_m4l_Add_{self.get_cr_fs_str()}"
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

    def make_plot_from_samples(self, canv, sample_dct, x_lim, bin_width, lumi, estimateZX_Data_file):
        """Make 1 plot of stacked hists.
        
        Parameters
        ----------
        canv
        sample_dct
        x_lim : 2-elem list
            [x_min, x_max] for plotting.
        bin_width : float
        lumi
        estimateZX_Data_file
        """
        n_bins = int((x_lim[1] - x_lim[0]) / bin_width)
        newbins = np.linspace(x_lim[0], x_lim[1], n_bins + 1)

        self.h_stack = self.make_hstack()

        for Nickname in sample_dct.keys():
            h = self.get_hist(sample_dct, Nickname)
            h_rebin = h.Rebin(len(newbins)-1, f"{h.GetName()}_rebin", newbins)
            self.store_hist(h_rebin, sample_dct, Nickname)

        self.make_legend(canv)

        self.draw_dataplot(x_lim=x_lim, bin_width=bin_width)
        # if "3P1F" in self.controlreg:
        #     self.add_2P2F_hist(estimateZX_Data_file=estimateZX_Data_file)
        self.draw_legend(lumi=lumi)

def checktype(msg="", obj=None):
    print(f"[INFO] {msg}: obj={obj}, type={type(obj)}")

if __name__ == "__main__":
    # ControlRegPlot(controlreg="3P1F", finalstate="2e2mu")
    ROOT.gROOT.SetBatch(True)
    canv = ROOT.TCanvas("canv", "myPlots",0,67,600,600)
    setCavasAndStyles("canv",canv,"")   
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    # canv.Range(-102.5,-10.38415,847.5,69.4939) 
    canv.Range(0,-10.38415,847.5,69.4939)
    canv.SetFillColor(0)
    canv.SetBorderMode(0)
    canv.SetBorderSize(2)
    canv.SetLeftMargin(0.15)
    canv.SetRightMargin(0.05)
    canv.SetTopMargin(0.05)
    canv.SetBottomMargin(0.13)
    canv.SetFrameFillStyle(0)
    canv.SetFrameBorderMode(0)
    canv.SetFrameFillStyle(0)
    canv.SetFrameBorderMode(0)
    canv.SetTickx(1)
    canv.SetTicky(1)
    canv.SetLogy()

    os.makedirs(os.path.dirname(outfile_path), exist_ok=True)
    check_overwrite(outfile_path, overwrite=overwrite)

    canv.Print(outfile_path + "[")

    # for fs in "4e 4mu 2e2mu 2mu2e".split():
        
    crp = ControlRegPlot(controlreg="2P2F", finalstate="4e")
    crp.make_plot_from_samples(
        canv=canv,
        sample_dct=sample_dct,
        x_lim=x_lim,
        bin_width=bin_width,
        lumi=LUMI_INT_2018_Jake,
        estimateZX_Data_file=estimateZX_Data_file)
    canv.Print(outfile_path)
    # for fs in finalstate_ls:
    #     for cr in controlreg_ls:
            # Make a plot boi.
            # canv.Print(outfile_path)
    canv.Print(outfile_path + "]")

    # for h in self.hist_ls:
    #     canv.SaveAs(os.path.join(outfile_dir, f"{h.GetName()}.root"))

    # canv.SaveAs(os.path.join(outfile_dir, f"{histName[p]}_auto.pdf"))
    # canv.SaveAs(os.path.join(outfile_dir, f"{histName[p]}_auto.C"))
    # canv.SaveAs(os.path.join(outfile_dir, f"{histName[p]}_auto.root"))