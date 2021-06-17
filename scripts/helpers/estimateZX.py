import ROOT
import math
import sys
from helpers.analyzeZX import get_evt_weight, setHistProperties
from constants.physics import xs_dct, MZ_PDG, LUMI_INT_2018_Jake

def getFR(lep_id, lep_pt, lep_eta, h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE):

    if ((math.fabs(lep_id) == 11) and (math.fabs(lep_eta) < 1.497)):
        return h1D_FRel_EB.GetBinContent(h1D_FRel_EB.FindBin(lep_pt))

    elif ((math.fabs(lep_id) == 11) and (math.fabs(lep_eta) > 1.497)):
        return h1D_FRel_EE.GetBinContent(h1D_FRel_EE.FindBin(lep_pt))

    elif ((math.fabs(lep_id) == 13) and (math.fabs(lep_eta) < 1.2)):
        return h1D_FRmu_EB.GetBinContent(h1D_FRmu_EB.FindBin(lep_pt))

    elif ((math.fabs(lep_id) == 13) and (math.fabs(lep_eta) > 1.2)):
        return h1D_FRmu_EE.GetBinContent(h1D_FRmu_EE.FindBin(lep_pt))

    return 0

def estimateZX(FakeRateFile, tree, Nickname, lumi=59700):
    # define dummy histogram for CRs
    var_plotHigh = 870.0
    var_plotLow = 70.0
    var_nBins = 40 #Using the same binning as in HIG-19-001

    h1D_dummyCR = ROOT.TH1D("dummyCR", "dummyCR", var_nBins, var_plotLow, var_plotHigh)

    varAxLabel = "m_{4l} [GeV]"

    binWidth = ((int) (100*(var_plotHigh - var_plotLow)/var_nBins))/100.
    setHistProperties(h1D_dummyCR,1,1,1,0,0,varAxLabel,"Events/"+str(binWidth)+" [GeV]")
    
    # define CR histograms
    h1D_m4l_SR_2P2F = ROOT.TH1D("h1D_m4l_SR_2P2F","h1D_m4l_SR_2P2F",var_nBins, var_plotLow, var_plotHigh)
    h1D_m4l_SR_2P2F.Sumw2()
    h1D_m4l_SR_3P1F = ROOT.TH1D("h1D_m4l_SR_3P1F","h1D_m4l_SR_3P1F",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_3P1F.Sumw2()
    h1D_m4l_Add_2P2F = ROOT.TH1D("h1D_m4l_Add_2P2F","h1D_m4l_Add_2P2F",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_Add_2P2F.Sumw2()
    
    # define CR histograms_4e
    h1D_m4l_SR_2P2F_4e = ROOT.TH1D("h1D_m4l_SR_2P2F_4e","h1D_m4l_SR_2P2F_4e",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_2P2F_4e.Sumw2()
    h1D_m4l_SR_3P1F_4e= ROOT.TH1D("h1D_m4l_SR_3P1F_4e","h1D_m4l_SR_3P1F_4e",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_3P1F_4e.Sumw2()
    h1D_m4l_Add_2P2F_4e = ROOT.TH1D("h1D_m4l_Add_2P2F_4e","h1D_m4l_Add_2P2F_4e",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_Add_2P2F_4e.Sumw2()
    
    # define CR histograms_4mu
    h1D_m4l_SR_2P2F_4mu = ROOT.TH1D("h1D_m4l_SR_2P2F_4mu","h1D_m4l_SR_2P2F_4mu",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_2P2F_4mu.Sumw2()
    h1D_m4l_SR_3P1F_4mu = ROOT.TH1D("h1D_m4l_SR_3P1F_4mu","h1D_m4l_SR_3P1F_4mu",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_3P1F_4mu.Sumw2()
    h1D_m4l_Add_2P2F_4mu = ROOT.TH1D("h1D_m4l_Add_2P2F_4mu","h1D_m4l_Add_2P2F_4mu",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_Add_2P2F_4mu.Sumw2()
    
    
    # define CR histograms_2e2mu
    h1D_m4l_SR_2P2F_2e2mu = ROOT.TH1D("h1D_m4l_SR_2P2F_2e2mu","h1D_m4l_SR_2P2F_2e2mu",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_2P2F_2e2mu.Sumw2()
    h1D_m4l_SR_3P1F_2e2mu = ROOT.TH1D("h1D_m4l_SR_3P1F_2e2mu","h1D_m4l_SR_3P1F_2e2mu",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_3P1F_2e2mu.Sumw2()
    h1D_m4l_Add_2P2F_2e2mu = ROOT.TH1D("h1D_m4l_Add_2P2F_2e2mu","h1D_m4l_Add_2P2F_2e2mu",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_Add_2P2F_2e2mu.Sumw2()
    
    # define CR histograms_2mu2e
    h1D_m4l_SR_2P2F_2mu2e = ROOT.TH1D("h1D_m4l_SR_2P2F_2mu2e","h1D_m4l_SR_2P2F_2mu2e",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_2P2F_2mu2e.Sumw2()
    h1D_m4l_SR_3P1F_2mu2e = ROOT.TH1D("h1D_m4l_SR_3P1F_2mu2e","h1D_m4l_SR_3P1F_2mu2e",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_SR_3P1F_2mu2e.Sumw2()
    h1D_m4l_Add_2P2F_2mu2e = ROOT.TH1D("h1D_m4l_Add_2P2F_2mu2e","h1D_m4l_Add_2P2F_2mu2e",var_nBins, var_plotLow, var_plotHigh) 
    h1D_m4l_Add_2P2F_2mu2e.Sumw2()


    # Read in the FRs 

    FR_file = ROOT.TFile(FakeRateFile, "READ")
 
    h1D_FRel_EB = FR_file.Get("Data_FRel_EB")
    h1D_FRel_EE = FR_file.Get("Data_FRel_EE")
    h1D_FRmu_EB = FR_file.Get("Data_FRmu_EB")
    h1D_FRmu_EE = FR_file.Get("Data_FRmu_EE")

    isData = ("Data" in Nickname)
    iEvt = -1
    nentries = tree.GetEntries()
    # lNEvents = setNEvents(Nickname)

    for iEvt, event in enumerate(tree):
        if (iEvt % 50000 == 0):
            print (f"Processing event: {iEvt}/{nentries}")
        # weight = event.eventWeight

        # if (isData):
        #     weight = 1
 
        # if not(isData):
        #     if (Nickname=="DY10"):
        #         weight *= 18610.0*lumi/lNEvents
                        
        #     if (Nickname=="DY50"):
        #         weight *= 6225.4*lumi/lNEvents

        #     if (Nickname=="TT"):
        #         weight *= 87.31*lumi/lNEvents

        #     if (Nickname=="WZ"):
        #         weight *= 4.67*lumi/lNEvents

        #     if (Nickname=="ZZ"):
        #         weight *= 1.256*lumi*event.k_qqZZ_qcd_M*event.k_qqZZ_ewk/lNEvents

        weight = get_evt_weight(isData, xs_dct, Nickname, lumi, event, nentries)

        if (event.passedZXCRSelection):
            lep_tight = []
            lep_iso = []
            idL = []
            pTL = []
            etaL = []
            # phiL = []
            # massL = []
            # dilep = ROOT.TLorentzVector()

            for k in range(4):
                lep_tight.append(event.lep_tightId[event.lep_Hindex[k]])
                lep_iso.append(event.lep_RelIsoNoFSR[event.lep_Hindex[k]])
                idL.append(event.lep_id[event.lep_Hindex[k]])
                lep = ROOT.TLorentzVector()
                lep.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[k]],event.lep_eta[event.lep_Hindex[k]],event.lep_phi[event.lep_Hindex[k]],event.lep_mass[event.lep_Hindex[k]])
                pTL.append(lep.Pt())
                etaL.append(lep.Eta())
                
            #Fix untill massZ1 flag is confirmed to be working again
            lep_1 = ROOT.TLorentzVector() 
            lep_2 = ROOT.TLorentzVector()
            lep_1.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[0]],event.lep_eta[event.lep_Hindex[0]],event.lep_phi[event.lep_Hindex[0]],event.lep_mass[event.lep_Hindex[0]])
            lep_2.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[1]],event.lep_eta[event.lep_Hindex[1]],event.lep_phi[event.lep_Hindex[1]],event.lep_mass[event.lep_Hindex[1]])
            
            massZ1 = (lep_1+lep_2).M()
            
            fr3 = getFR(idL[2], pTL[2], etaL[2], h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE)
            fr4 = getFR(idL[3], pTL[3], etaL[3], h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE)

            frShape= (fr3/(1-fr3)) * (fr4/(1-fr4))
            Fill_value = event.mass4l

            nFailedLeptons3 = not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35)))
            nFailedLeptons4 = not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))

            nFailedLeptonsZ2 = nFailedLeptons3 + nFailedLeptons4
            #nFailedLeptonsZ2 = not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35))) + not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))
            
            #Prepare the estimates
            if (nFailedLeptonsZ2 == 1):
                fr_bool_3 = (not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35))))
                fr_3 = fr_bool_3 * (fr3/(1-fr3))

                fr_bool_4 = (not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35))))
                fr_4 = fr_bool_4 * (fr4/(1-fr4))

                fr = fr_3 + fr_4
                #fr = (not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35))))*(fr3/(1-fr3)) + (not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35))))*(fr4/(1-fr4))
                
                h1D_m4l_SR_3P1F.Fill(event.mass4l, weight * fr)
                
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==44):
                
                    h1D_m4l_SR_3P1F_4e.Fill(event.mass4l, weight* fr)
                    
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==52):

                    h1D_m4l_SR_3P1F_4mu.Fill(event.mass4l, weight* fr)
                
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==48):
                    
                    
                    if ((abs(idL[2])+abs(idL[3]))== 26):
                        h1D_m4l_SR_3P1F_2e2mu.Fill(event.mass4l, weight* fr)

                    if ((abs(idL[2])+abs(idL[3]))== 22):
                        h1D_m4l_SR_3P1F_2mu2e.Fill(event.mass4l, weight* fr)
            
            elif (nFailedLeptonsZ2 == 2):

                fr= (fr3/(1-fr3)) * (fr4/(1-fr4))
                fr2 =(fr3/(1-fr3)) + (fr4/(1-fr4))
                
                # *Add_2P2F* represents 2P2F contribution in 3P1F
                h1D_m4l_Add_2P2F.Fill(event.mass4l, weight * fr2)
                h1D_m4l_SR_2P2F.Fill(event.mass4l, weight * fr)

                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==44):
                
                    h1D_m4l_SR_2P2F_4e.Fill(event.mass4l, weight* fr)
                    h1D_m4l_Add_2P2F_4e.Fill(event.mass4l, weight * fr2)
                    
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==52):
    
                    h1D_m4l_SR_2P2F_4mu.Fill(event.mass4l, weight* fr)
                    h1D_m4l_Add_2P2F_4mu.Fill(event.mass4l, weight * fr2)
                    
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==48):

                    if ((abs(idL[2])+abs(idL[3]))== 26):
                    
                        h1D_m4l_SR_2P2F_2e2mu.Fill(event.mass4l, weight* fr)
                        h1D_m4l_Add_2P2F_2e2mu.Fill(event.mass4l, weight * fr2)
                        
                    if ((abs(idL[2])+abs(idL[3]))== 22):

                        h1D_m4l_SR_2P2F_2mu2e.Fill(event.mass4l, weight* fr)
                        h1D_m4l_Add_2P2F_2mu2e.Fill(event.mass4l, weight * fr2)
                    
          
    SaveRootFile = ROOT.TFile(f"estimateZX_{Nickname}.root", "RECREATE")
        
    h1D_FRel_EB.SetName("h1D_FRel_EB")
    h1D_FRel_EB.Write()
    h1D_FRel_EE.SetName("h1D_FRel_EE") 
    h1D_FRel_EE.Write()
    h1D_FRmu_EB.SetName("h1D_FRmu_EB") 
    h1D_FRmu_EB.Write()
    h1D_FRmu_EE.SetName("h1D_FRmu_EE") 
    h1D_FRmu_EE.Write()

    h1D_m4l_SR_2P2F.SetName("h1D_m4l_SR_2P2F") 
    h1D_m4l_SR_2P2F.Write()
    h1D_m4l_SR_2P2F_4e.SetName("h1D_m4l_SR_2P2F_4e") 
    h1D_m4l_SR_2P2F_4e.Write()
    h1D_m4l_SR_2P2F_4mu.SetName("h1D_m4l_SR_2P2F_4mu") 
    h1D_m4l_SR_2P2F_4mu.Write()
    h1D_m4l_SR_2P2F_2e2mu.SetName("h1D_m4l_SR_2P2F_2e2mu") 
    h1D_m4l_SR_2P2F_2e2mu.Write()
    h1D_m4l_SR_2P2F_2mu2e.SetName("h1D_m4l_SR_2P2F_2mu2e") 
    h1D_m4l_SR_2P2F_2mu2e.Write()
    
    h1D_m4l_Add_2P2F.SetName("h1D_m4l_Add_2P2F") 
    h1D_m4l_Add_2P2F.Write()
    h1D_m4l_Add_2P2F_4e.SetName("h1D_m4l_Add_2P2F_4e") 
    h1D_m4l_Add_2P2F_4e.Write()
    h1D_m4l_Add_2P2F_4mu.SetName("h1D_m4l_Add_2P2F_4mu") 
    h1D_m4l_Add_2P2F_4mu.Write()
    h1D_m4l_Add_2P2F_2e2mu.SetName("h1D_m4l_Add_2P2F_2e2mu") 
    h1D_m4l_Add_2P2F_2e2mu.Write()
    h1D_m4l_Add_2P2F_2mu2e.SetName("h1D_m4l_Add_2P2F_2mu2e") 
    h1D_m4l_Add_2P2F_2mu2e.Write()
    
    h1D_m4l_SR_3P1F.SetName("h1D_m4l_SR_3P1F") 
    h1D_m4l_SR_3P1F.Write()
    h1D_m4l_SR_3P1F_4e.SetName("h1D_m4l_SR_3P1F_4e") 
    h1D_m4l_SR_3P1F_4e.Write()
    h1D_m4l_SR_3P1F_4mu.SetName("h1D_m4l_SR_3P1F_4mu") 
    h1D_m4l_SR_3P1F_4mu.Write()
    h1D_m4l_SR_3P1F_2e2mu.SetName("h1D_m4l_SR_3P1F_2e2mu") 
    h1D_m4l_SR_3P1F_2e2mu.Write()
    h1D_m4l_SR_3P1F_2mu2e.SetName("h1D_m4l_SR_3P1F_2mu2e") 
    h1D_m4l_SR_3P1F_2mu2e.Write()
    
    SaveRootFile.Close()

    #PAUZA ZA DANAS
            
    FR_file.Close()