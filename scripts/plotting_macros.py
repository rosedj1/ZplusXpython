import os
import ROOT
from ROOT import TColor
from helpers.analyzeZX import setCavasAndStyles

def CRPlot():
    ROOT.gROOT.SetBatch(True)
    indata_path = "../data/"
    c2 = ROOT.TCanvas()
    setCavasAndStyles("c2",c2,"")   
    
    histName = [
        "2P2F", "2P2F_4e", "2P2F_4mu", "2P2F_2e2mu", "2P2F_2mu2e",
        "3P1F", "3P1F_4e", "3P1F_4mu", "3P1F_2e2mu", "3P1F_2mu2e"
        ]
 #   Fillcolors = ["#cc0099","#99ccff","#996666","#669966"]
 #   Linecolors = ["#990066","#000099","#5f3f3f","#003300"]
    StackTitle = "Proba"
    #ProcessNames = ["Data","WZ","ZZ","TT","DY50"]
    #LabelNames = ["Data","#WZ#","#Z\\gamma^*,ZZ#","#t\\bar{t}+jets#","#Z+jets#"]

    Fillcolors = ["#99ccff","#cc0099","#996666","#669966"]
    Linecolors = ["#000099","#990066","#5f3f3f","#003300"]

    ProcessNames = ["Data", "ZZ", "WZ", "TT", "DY50"]
    # LabelNames = ["Data", "#Z\\gamma^*, ZZ#", "#WZ#", "#t\\bar{t}+jets#", "#Z+jets#"]

    fileSize = 5
    plotSize = 10
    variableN = "ptl3"
    for p in range(plotSize):
        # print( "Ulazi u plotting" ) 
        print( "Begin plotting." ) 
        leg = ROOT.TLegend(0.45,0.5,1.05,0.85)
        leg.SetBorderSize(0)
        leg.SetLineColor(1)
        leg.SetLineStyle(1)
        leg.SetLineWidth(1)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
    
        if (p>4):
            entry = leg.AddEntry("NULL","Control Region "+ histName[p] ,"h")
        else:
            entry = leg.AddEntry("NULL","Control Region "+ histName[p] ,"h")

        entry.SetLineColor(1)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(62)
        entry = leg.AddEntry("NULL","Data","LP")
        entry.SetLineColor(1)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(20)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry = leg.AddEntry("NULL","Z + jets","F")
        
        ci = TColor.GetColor("#669966")
        entry.SetFillColor(ci)
        entry.SetFillStyle(1001)
        
        ci = TColor.GetColor("#003300")
        entry.SetLineColor(ci)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry=leg.AddEntry("NULL","t#bar{t} + jets","F")
        
        ci = TColor.GetColor("#996666")
        entry.SetFillColor(ci)
        entry.SetFillStyle(1001)
        
        ci = TColor.GetColor("#5f3f3f")
        entry.SetLineColor(ci)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry=leg.AddEntry("NULL","WZ","F")
        
        ci = TColor.GetColor("#cc0099")
        entry.SetFillColor(ci)
        entry.SetFillStyle(1001)
        
        ci = TColor.GetColor("#990066")
        entry.SetLineColor(ci)
        entry.SetLineStyle(1)
        entry.SetLineWidth(1)
        entry.SetMarkerColor(1)
        entry.SetMarkerStyle(21)
        entry.SetMarkerSize(1)
        entry.SetTextFont(42)
        entry = leg.AddEntry("NULL","Z#gamma*,ZZ","F")
        
        ci = TColor.GetColor("#99ccff")
        entry.SetFillColor(ci)
        entry.SetFillStyle(1001)
        
        if (p>4):

            ci = TColor.GetColor("#000099")
            entry.SetLineColor(ci)
            entry.SetLineStyle(1)
            entry.SetLineWidth(1)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)
            entry=leg.AddEntry("NULL","2P2F contribution","F")
            entry.SetFillStyle(4000)
            entry.SetLineColor(6)
            entry.SetLineStyle(1)
            entry.SetLineWidth(2)
            entry.SetMarkerColor(1)
            entry.SetMarkerStyle(21)
            entry.SetMarkerSize(1)
            entry.SetTextFont(42)        
        
        A = ROOT.THStack(StackTitle,StackTitle)
        
        Proba_stack_5_stack_1 = ROOT.TH1F("Proba_stack_5_stack_1","Proba",100,0,2000)
        Proba_stack_5_stack_1.SetMinimum(-5.608576)
        Proba_stack_5_stack_1.SetMaximum(51.10072)
        Proba_stack_5_stack_1.SetDirectory(0)
        Proba_stack_5_stack_1.SetStats(0)
        Proba_stack_5_stack_1.SetLineColor(TColor.GetColor("#000099"))
        Proba_stack_5_stack_1.SetLineStyle(0)
        Proba_stack_5_stack_1.SetMarkerStyle(20)
        Proba_stack_5_stack_1.GetXaxis().SetLabelFont(42)
        Proba_stack_5_stack_1.GetXaxis().SetLabelOffset(0.007)
        Proba_stack_5_stack_1.GetXaxis().SetLabelSize(0.05)
        Proba_stack_5_stack_1.GetXaxis().SetTitleSize(0.06)
        Proba_stack_5_stack_1.GetXaxis().SetTitleOffset(0.9)
        Proba_stack_5_stack_1.GetXaxis().SetTitleFont(42)
        Proba_stack_5_stack_1.GetYaxis().SetLabelFont(42)
        Proba_stack_5_stack_1.GetYaxis().SetLabelOffset(0.007)
        Proba_stack_5_stack_1.GetYaxis().SetLabelSize(0.05)
        Proba_stack_5_stack_1.GetYaxis().SetTitleSize(0.06)
        Proba_stack_5_stack_1.GetYaxis().SetTitleOffset(1.25)
        Proba_stack_5_stack_1.GetYaxis().SetTitleFont(42)
        Proba_stack_5_stack_1.GetZaxis().SetLabelFont(42)
        Proba_stack_5_stack_1.GetZaxis().SetLabelOffset(0.007)
        Proba_stack_5_stack_1.GetZaxis().SetLabelSize(0.05)
        Proba_stack_5_stack_1.GetZaxis().SetTitleSize(0.06)
        Proba_stack_5_stack_1.GetZaxis().SetTitleFont(42)
        A.SetHistogram(Proba_stack_5_stack_1)
        
        _file = []
        histPlot = []
        for i in range(fileSize):

            if (i == 0):
                Title = "Data"
            else:
                Title = "MC"

            filename = f"../data/Hist_{Title}_{variableN}_{ProcessNames[i]}.root"
            indata_fullpath = os.path.join(indata_path, filename)
            _file.append(ROOT.TFile(indata_fullpath))
            
            if (i==0) :
                dataPlot = _file[i].Get("h1D_m4l_"+histName[p])
                histPlot.append(dataPlot)

                print( "Data " + histName[p]+ " := "  + str(dataPlot.Integral()) )
            else:
                histPlot.append(_file[i].Get("h1D_m4l_"+histName[p]))
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
                
                print( "MC: "+ histName[p] + " := "+ str( histPlot[i].Integral() ) )
                A.Add(histPlot[i])

        print ("Data status " + str(dataPlot))    
        c2 = ROOT.TCanvas("c2", "myPlots",0,67,600,600)
        ROOT.gStyle.SetOptFit(1)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)
        c2.Range(-102.5,-10.38415,847.5,69.4939)
        c2.SetFillColor(0)
        c2.SetBorderMode(0)
        c2.SetBorderSize(2)
        c2.SetTickx(1)
        c2.SetTicky(1)
        c2.SetLeftMargin(0.15)
        c2.SetRightMargin(0.05)
        c2.SetTopMargin(0.05)
        c2.SetBottomMargin(0.13)
        c2.SetFrameFillStyle(0)
        c2.SetFrameBorderMode(0)
        c2.SetFrameFillStyle(0)
        c2.SetFrameBorderMode(0)
        
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
        if ( p>4 ):
            _file2p2f = ROOT.TFile(os.path.join(indata_path, "estimateZX_Data.root"), "READ")
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

        leg.Draw("goff")
        
        tex = ROOT.TLatex(0.95, 0.96, "58.8 fb^{-1} (13 TeV)")  # Or is it 59.7 fb^{-1}?
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
        
        outfile_path = '../CR_plots'
        os.makedirs(outfile_path, exist_ok=True)
        c2.SaveAs(os.path.join(outfile_path, f"{histName[p]}_auto.pdf"))
        c2.SaveAs(os.path.join(outfile_path, f"m{histName[p]}_auto.C"))
        c2.SaveAs(os.path.join(outfile_path, f"{histName[p]}_auto.root"))

CRPlot()