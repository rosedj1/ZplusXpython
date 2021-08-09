"""
Apply WZ-removed fake rates to 3P1F and 2P2F control regions (CRs).

Syntax to run: `python <this_script>.py`
Author: Jake Rosenzweig
Original logic from: Vukasin Melosevic
Updated: 2021-07-23
"""
import ROOT
import math
import sys
import os
from scripts.helpers.analyzeZX import get_evt_weight, setHistProperties
from constants.physics import xs_dct, MZ_PDG, LUMI_INT_2018_Jake, n_sumgenweights_dataset_dct
from Utils_Python.Utils_Files import check_overwrite

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

def estimateZX(FakeRateFile, tree, Nickname, outfile_dir, suffix="",
               overwrite=0, lumi=59700):
    #-- User Parameters --#
    wgt_from_ntuple = False

    # Name the outfile and check for overwrite.
    isData = "Data" in Nickname
    filename = f"estimateZX_{Nickname}.root"
    outfile_path = os.path.join(outfile_dir, filename)
    check_overwrite(outfile_path, overwrite=overwrite)
    
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

    # Read in the FRs (with WZ removed).
    FR_file = ROOT.TFile(FakeRateFile, "READ")
    h1D_FRel_EB = FR_file.Get("Data_FRel_EB")
    h1D_FRel_EE = FR_file.Get("Data_FRel_EE")
    h1D_FRmu_EB = FR_file.Get("Data_FRmu_EB")
    h1D_FRmu_EE = FR_file.Get("Data_FRmu_EE")

    isData = "Data" in Nickname
    iEvt = -1
    n_evts_tree = tree.GetEntries()
    if isData:
        n_dataset_tot = n_evts_tree
    else:
        n_dataset_tot = float(n_sumgenweights_dataset_dct[Nickname])
    # lNEvents = setNEvents(Nickname)

    for iEvt, event in enumerate(tree):
        if (iEvt % 50000) == 0:
            print (f"Processing event: {iEvt}/{n_evts_tree}")
        # if iEvt > 50000:
        #     break

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
        weight = get_evt_weight(
            isData=isData, xs_dct=xs_dct, Nickname=Nickname, lumi=lumi,
            event=event, n_dataset_tot=n_dataset_tot, wgt_from_ntuple=wgt_from_ntuple)
        
        if event.passedZXCRSelection:
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
                lep.SetPtEtaPhiM(
                    event.lep_pt[event.lep_Hindex[k]],
                    event.lep_eta[event.lep_Hindex[k]],
                    event.lep_phi[event.lep_Hindex[k]],
                    event.lep_mass[event.lep_Hindex[k]])
                pTL.append(lep.Pt())
                etaL.append(lep.Eta())
                
            #Fix untill massZ1 flag is confirmed to be working again
            lep_1 = ROOT.TLorentzVector()
            lep_2 = ROOT.TLorentzVector()
            # print(f"Jake is it true that these two leps form the Z1?")
            lep_1.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[0]],event.lep_eta[event.lep_Hindex[0]],event.lep_phi[event.lep_Hindex[0]],event.lep_mass[event.lep_Hindex[0]])
            lep_2.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[1]],event.lep_eta[event.lep_Hindex[1]],event.lep_phi[event.lep_Hindex[1]],event.lep_mass[event.lep_Hindex[1]])
            
            massZ1 = (lep_1 + lep_2).M()
            
            # Apply FRs to leps 3 and 4.
            fr3 = getFR(idL[2], pTL[2], etaL[2], h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE)
            fr4 = getFR(idL[3], pTL[3], etaL[3], h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE)

            fr_lep3_odds = fr3 / (1 - fr3)
            fr_lep4_odds = fr4 / (1 - fr4)
            # 2P2F has only 2 signal leptons.
            # Contributing processes: Z+jets and ttbar.
            # Obtain their contribution to signal region by weighting
            # each event in the 2P2F region by this factor:
            fr_product = fr_lep3_odds * fr_lep4_odds
            # fr_sum = (fr3/(1-fr3)) + (fr4/(1-fr4))
            fr_sum = fr_lep3_odds + fr_lep4_odds

            # frShape = (fr3/(1-fr3)) * (fr4/(1-fr4))
            m4l = event.mass4l

            # failed lep = not (tight and good e/mu)
            iso_lep_2 = (abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35)
            iso_lep_3 = (abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)
            lep3_failed = not (lep_tight[2] and iso_lep_2)
            lep4_failed = not (lep_tight[3] and iso_lep_3)
            # lep3_failed = not (lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35)))
            # lep4_failed = not (lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))

            nFailedLeptonsZ2 = lep3_failed + lep4_failed
            #nFailedLeptonsZ2 = not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35))) + not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))
            
            # Prepare the estimates: 3P1F.
            if nFailedLeptonsZ2 == 1:
                # Apply fake rate odds from the lepton which failed full selection.
                fr = (lep3_failed * fr_lep3_odds) + (lep4_failed * fr_lep4_odds)
                # fr_bool_3 = not (lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35)))
                # fr_bool_3 = lep3_failed # 0 or 1.
                # fr_3 = fr_bool_3 * (fr3/(1-fr3))

                # fr_bool_4 = not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))
                # fr_bool_4 = lep4_failed
                # fr_4 = fr_bool_4 * (fr4/(1-fr4))
                # fr = fr_3 + fr_4
                #fr = (not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35))))*(fr3/(1-fr3)) + (not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35))))*(fr4/(1-fr4))
                
                # Fill hists based on final state.
                wgt_3p1f = weight * fr
                h1D_m4l_SR_3P1F.Fill(m4l, wgt_3p1f)
                # 4e.
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==44):
                    h1D_m4l_SR_3P1F_4e.Fill(m4l, wgt_3p1f)
                # 4mu.
                elif ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==52):
                    h1D_m4l_SR_3P1F_4mu.Fill(m4l, wgt_3p1f)
                # 2e2mu or 2mu2e.
                elif ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==48):
                    # 2e2mu.
                    if ((abs(idL[2])+abs(idL[3])) == 26):
                        h1D_m4l_SR_3P1F_2e2mu.Fill(m4l, wgt_3p1f)
                    # 2mu2e.
                    elif ((abs(idL[2])+abs(idL[3])) == 22):
                        h1D_m4l_SR_3P1F_2mu2e.Fill(m4l, wgt_3p1f)
            # 2P2F.
            elif nFailedLeptonsZ2 == 2:
                wgt_2p2f_sum  = weight * fr_sum
                wgt_2p2f_prod = weight * fr_product
                # Fill hists based on final state.
                # *Add_2P2F* represents 2P2F contribution in 3P1F
                h1D_m4l_Add_2P2F.Fill(m4l, wgt_2p2f_sum)
                h1D_m4l_SR_2P2F.Fill(m4l, wgt_2p2f_prod)
                # 4e.
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==44):
                    h1D_m4l_SR_2P2F_4e.Fill(m4l, wgt_2p2f_prod)
                    h1D_m4l_Add_2P2F_4e.Fill(m4l, wgt_2p2f_sum)
                # 4mu.
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==52):
                    h1D_m4l_SR_2P2F_4mu.Fill(m4l, wgt_2p2f_prod)
                    h1D_m4l_Add_2P2F_4mu.Fill(m4l, wgt_2p2f_sum)
                # 2e2mu or 2mu2e.
                if ((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==48):
                    # 2e2mu.
                    if ((abs(idL[2])+abs(idL[3]))== 26):
                        h1D_m4l_SR_2P2F_2e2mu.Fill(m4l, wgt_2p2f_prod)
                        h1D_m4l_Add_2P2F_2e2mu.Fill(m4l, wgt_2p2f_sum)
                    # 2mu2e.
                    if ((abs(idL[2])+abs(idL[3]))== 22):
                        h1D_m4l_SR_2P2F_2mu2e.Fill(m4l, wgt_2p2f_prod)
                        h1D_m4l_Add_2P2F_2mu2e.Fill(m4l, wgt_2p2f_sum)

    print()
    SaveRootFile = ROOT.TFile(outfile_path, "RECREATE")
        
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