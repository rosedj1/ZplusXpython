import os
import ROOT
from ROOT import TColor
from helpers.analyzeZX import setCavasAndStyles
from physics import LUMI_INT_2018_Jake

ControlRegPlot(controlreg="2P2F", finalstate="4e")
ControlRegPlot(controlreg="3P1F", finalstate="2e2mu")

ControlRegPlot.

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
        assert controlreg in ("2P2F", "3P1F")
        assert finalstate in ("", "4e", "4mu", "2e2mu", "2mu2e")
        self.controlreg = controlreg
        self.finalstate = finalstate
        self.h_stack = None

    def make_title(self):
        return f"Control Region {self.controlreg} {self.finalstate}"

    def make_legend(self, ci):
        """
        Return a filled-out legend.

        ci : TCanvas
        """
        # CR.
        leg = ROOT.TLegend(0.45, 0.5, 1.05, 0.85)
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
        # Zgamma, ZZ.
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
        if self.controlreg in "3P1F":
            canv = TColor.GetColor("#000099")
            entry.SetLineColor(canv)
            entry.SetLineStyle(1)
            entry.SetLineWidth(1)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)
            entry=leg.AddEntry("NULL", "2P2F contribution","F")
            entry.SetFillStyle(4000)
            entry.SetLineColor(6)
            entry.SetLineStyle(1)
            entry.SetLineWidth(2)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)
        return leg

    def make_hstack(self):
        """"""
        h_stack = ROOT.THStack(f"{self.controlreg}_{self.finalstate}", "title")
        h_addtostack = ROOT.TH1F("h_addtostack","Proba",100,0,2000)
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
        h_stack.SetHistogram(h_addtostack.Clone())
        self.h_stack = h_stack

    def something():
            _file2p2f = ROOT.TFile(os.path.join(estimateZX_indir, "estimateZX_Data.root"), "READ")
            histPlot2p2f = _file2p2f.Get("h1D_m4l_Add_"+histName[p-5])
            print( "2P2F contr:= " + str(histPlot2p2f.Integral()) ) 
            print ("Adding "+ ProcessNames[1] + " and "+ ProcessNames[2] +" to the 2P2F Contr in 3P1F")
            histPlot2p2f.Add(histPlot[1])
            histPlot2p2f.Add(histPlot[2])
            histPlot2p2f.SetFillColor(TColor.GetColor("#ffffff"))
            histPlot2p2f.SetLineColor(TColor.GetColor("#ff00ff"))
            histPlot2p2f.SetLineWidth(2)
            histPlot2p2f.SetFillStyle(4000)
            histPlot2p2f.Smooth()
            histPlot2p2f.Draw("hist E1 same goff")

def make_CR_Plots():
    lumi = LUMI_INT_2018_Jake / 1000.0

    estimateZX_indir = "/blue/avery/rosedj1/ZplusXpython/data/controlreg_OS/"
    outfile_path = '/blue/avery/rosedj1/ZplusXpython/plots/hist_controlreg'
    os.makedirs(outfile_path, exist_ok=True)

    ROOT.gROOT.SetBatch(True)
    canv = ROOT.TCanvas()
    setCavasAndStyles("canv",canv,"")   
    
    # ProcessNames = ["Data", "ZZ", "WZ", "TT", "DY50"]
    # LabelNames = ["Data", "#Z\\gamma^*, ZZ#", "#WZ#", "#t\\bar{t}+jets#", "#Z+jets#"]
    file_dct = {
        "Data" : {
            "label" : "Data",
            "filepath" : ""
            },
        "ZZ" : {
            "label" : "#Z\\gamma^*, ZZ#",
            "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210721_alljake/Hist_MC_ZZ.root"
            },
        "WZ" : {
            "label" : "#WZ#",
            "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210721_alljake/Hist_MC_WZ-ext1-v2.root"
            },
        "TT" : {
            "label" : "#t\\bar{t}+jets#",
            "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210721_alljake/Hist_MC_TT.root"
            },
        "DY50" : {
            "label" : "#Z+jets#",
            "filepath" : "/blue/avery/rosedj1/ZplusXpython/data/20210721_alljake/Hist_MC_DY50.root"
            }
    }

    histName = [
        "2P2F", "2P2F_4e", "2P2F_4mu", "2P2F_2e2mu", "2P2F_2mu2e",
        "3P1F", "3P1F_4e", "3P1F_4mu", "3P1F_2e2mu", "3P1F_2mu2e",
        ]
 #   Fillcolors = ["#cc0099","#99ccff","#996666","#669966"]
 #   Linecolors = ["#990066","#000099","#5f3f3f","#003300"]
    # StackTitle = "Proba"
    #ProcessNames = ["Data","WZ","ZZ","TT","DY50"]
    #LabelNames = ["Data","#WZ#","#Z\\gamma^*,ZZ#","#t\\bar{t}+jets#","#Z+jets#"]

    Fillcolors = ["#99ccff","#cc0099","#996666","#669966"]
    Linecolors = ["#000099","#990066","#5f3f3f","#003300"]

    ProcessNames = tuple(file_dct.keys())
    fileSize = halfway_pt = len(ProcessNames) #5
    plotSize = 2 * fileSize #10
    for p in range(plotSize):
        # print( "Ulazi u plotting" ) 
        print("Begin plotting.")
        
        _file = []
        histPlot = []
        for i, (Nickname, info_dct) in enumerate(file_dct.items()):
            
            label = info_dct["label"]
            indata_fullpath = info_dct["filepath"]
            _file.append(ROOT.TFile(indata_fullpath))
            
            if "Data" in Nickname:
                dataPlot = _file[i].Get("h1D_mass4l_"+histName[p])
                histPlot.append(dataPlot)
                print( "Data " + histName[p]+ " integral = "  + str(dataPlot.Integral()) )
            else:
                # Add MC hists together.
                histPlot.append(_file[i].Get("h1D_mass4l_"+histName[p]))
                histPlot[i].SetFillColor(TColor.GetColor(Fillcolors[i-1]))
                histPlot[i].SetLineColor(TColor.GetColor(Linecolors[i-1]))
                histPlot[i].SetFillStyle(1001)
                histPlot[i].SetLineStyle(0)
                histPlot[i].SetMarkerStyle(20)
                histPlot[i].GetXaxis().SetLabelFont(42)
                histPlot[i].GetXaxis().SetLabelOffset(0.007)
                histPlot[i].GetXaxis().SetLabelSize(0.05)
                histPlot[i].GetXaxis().SetTitleSize(0.06)
                histPlot[i].GetXaxis().SetTitleOffset(0.9)
                histPlot[i].GetXaxis().SetTitleFont(42)
                histPlot[i].GetYaxis().SetLabelFont(42)
                histPlot[i].GetYaxis().SetLabelOffset(0.007)
                histPlot[i].GetYaxis().SetLabelSize(0.05)
                histPlot[i].GetYaxis().SetTitleSize(0.06)
                histPlot[i].GetYaxis().SetTitleOffset(1.25)
                histPlot[i].GetYaxis().SetTitleFont(42)
                histPlot[i].GetZaxis().SetLabelFont(42)
                histPlot[i].GetZaxis().SetLabelOffset(0.007)
                histPlot[i].GetZaxis().SetLabelSize(0.05)
                histPlot[i].GetZaxis().SetTitleSize(0.06)
                histPlot[i].GetZaxis().SetTitleFont(42)
                print( "MC: "+ histName[p] + "  integral = "+ str( histPlot[i].Integral() ) )
                A.Add(histPlot[i])
        # End loop over file_dct.

        print ("Data status " + str(dataPlot))    
        canv = ROOT.TCanvas("canv", "myPlots",0,67,600,600)
        ROOT.gStyle.SetOptFit(1)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)
        canv.Range(-102.5,-10.38415,847.5,69.4939)
        canv.SetFillColor(0)
        canv.SetBorderMode(0)
        canv.SetBorderSize(2)
        canv.SetTickx(1)
        canv.SetTicky(1)
        canv.SetLeftMargin(0.15)
        canv.SetRightMargin(0.05)
        canv.SetTopMargin(0.05)
        canv.SetBottomMargin(0.13)
        canv.SetFrameFillStyle(0)
        canv.SetFrameBorderMode(0)
        canv.SetFrameFillStyle(0)
        canv.SetFrameBorderMode(0)
        
        dataPlot.SetFillColor(TColor.GetColor("#000000"))
        dataPlot.SetLineColor(TColor.GetColor("#000000"))
        dataPlot.SetFillStyle(0)
        dataPlot.SetMarkerStyle(20)
        dataPlot.GetXaxis().SetTitle("m_{4#font[12]{l}} (GeV)")
        dataPlot.GetXaxis().SetRange(3,40)
        dataPlot.GetXaxis().SetLabelFont(42)
        dataPlot.GetXaxis().SetLabelSize(0.05)
        dataPlot.GetXaxis().SetTitleSize(0.06)
        dataPlot.GetXaxis().SetTitleOffset(0.9)
        dataPlot.GetXaxis().SetTitleFont(42)
        dataPlot.GetYaxis().SetTitle("Events / 20 GeV")
        dataPlot.GetYaxis().SetLabelFont(42)
        dataPlot.GetYaxis().SetLabelSize(0.05)
        dataPlot.GetYaxis().SetTitleSize(0.06)
        dataPlot.GetYaxis().SetTitleOffset(1.25)
        dataPlot.GetYaxis().SetTitleFont(42)
        dataPlot.GetZaxis().SetLabelFont(42)
        dataPlot.GetZaxis().SetLabelSize(0.035)
        dataPlot.GetZaxis().SetTitleSize(0.035)
        dataPlot.GetZaxis().SetTitleFont(42)
        
        dataPlot.GetXaxis().SetRangeUser(50,800)
        glb_max = max([h.GetMaximum() for h in histPlot])
        dataPlot.GetYaxis().SetRangeUser(0, 1.3 * glb_max)
        dataPlot.Draw("e1 goff")
        
        A.Draw("hist same")
        dataPlot.Draw("same e1 goff")


        leg.Draw("goff")
        tex = ROOT.TLatex(0.95, 0.96, r"{%.1f} fb^{-1} (13 TeV)" % lumi)  # Or is it 59.7 fb^{-1}?
        tex.SetNDC()
        tex.SetTextAlign(31)
        tex.SetTextFont(42)
        tex.SetTextSize(0.03)
        tex.SetLineWidth(2)
        tex.Draw("goff")
        tex = ROOT.TLatex(0.15,0.96,"CMS")
        tex.SetNDC()
        tex.SetTextFont(61)
        tex.SetTextSize(0.0375)
        tex.SetLineWidth(2)
        tex.Draw("goff")
        tex = ROOT.TLatex(0.23,0.96,"Preliminary")
        tex.SetNDC()
        tex.SetTextFont(52)
        tex.SetTextSize(0.0285)
        tex.SetLineWidth(2)
        tex.Draw("goff")

        os.makedirs(outfile_path, exist_ok=True)
        canv.SaveAs(os.path.join(outfile_path, f"{histName[p]}_auto.pdf"))
        canv.SaveAs(os.path.join(outfile_path, f"{histName[p]}_auto.C"))
        canv.SaveAs(os.path.join(outfile_path, f"{histName[p]}_auto.root"))
    # End loop over range(plotSize).

make_CR_Plots()