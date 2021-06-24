"""Determine Fake Rates and OS Z+LL Control Regions

Syntax to run: `python this_script.py`
Original Author: Vukasin Milosevic
Modified by: Jake Rosenzweig
Updated: 2021-06-18
"""
import os
import sys
import math
import ROOT as rt
import numpy as np
# from Utils_Python.Utils_Files import check_overwrite
from helpers.MC_composition import PartOrigin
from constants.physics import xs_dct, MZ_PDG, LUMI_INT_2018_Jake, n_totevts_dataset_dct
# from HiggsMassMeasurement.Utils_ROOT.ROOT_classes import make_TH1F
from Utils_ROOT.ROOT_classes import make_TH1F

class barrel_endcap_region():
    EB_n = 0
    EB_d = 1
    EE_n = 2
    EE_d = 3
    MB_n = 4
    MB_d = 5
    ME_n = 6
    ME_d = 7

class type_of_fake():
    Prom = 0
    Fake = 1
    Conv = 2
    BDfake = 3

class CRregion():
    _2P2F = 0
    _2P2F_4e = 1
    _2P2F_4mu = 2
    _2P2F_2e2mu = 3
    _2P2F_2mu2e = 4
    _3P1F = 5
    _3P1F_4e = 6
    _3P1F_4mu = 7
    _3P1F_2e2mu = 8
    _3P1F_2mu2e = 9

q_e = 11
q_mu = 13
finalstate_dct = {
    "4e" : int(4 * q_e),
    "4mu" : int(4 * q_mu),
    "2e2mu" : int(2 * q_e + 2 * q_mu),
    "2mu2e" : int(2 * q_e + 2 * q_mu),
    "2e" : int(2 * q_e),
    "2mu" : int(2 * q_mu)
    }

def get_sum_absIDs(id_ls):
    """Return the sum of abs(IDs) of all leptons in id_ls."""
    return sum([abs(ID) for ID in id_ls])

def setCavasAndStyles(canvasName, c, stat):
    #setup canvas
    # c = rt.TCanvas(canvasName,"myPlots",0,0,800,600)
    c.cd(1)
    c.SetLogy(0)
    rt.gStyle.SetOptStat(stat)
    rt.gStyle.SetPalette(1)

def setHistProperties(hist, lineWidth, lineStyle, lineColor, fillStyle, fillColor, xAxisTitle, yAxisTitle):
    if not(hist):
        return -1
    hist.SetLineWidth(lineWidth)
    hist.SetLineStyle(lineStyle)
    hist.SetLineColor(lineColor)
    # fill
    hist.SetFillStyle(fillStyle)
    hist.SetFillColor(fillColor)
    # divisions, offsets, sizes
    hist.GetXaxis().SetNdivisions(510)
    hist.GetYaxis().SetNdivisions(510)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.2)
    # titles
    if (xAxisTitle!="skip"):
        hist.GetXaxis().SetTitle(xAxisTitle)
    if (yAxisTitle!="skip"):
        hist.GetYaxis().SetTitle(yAxisTitle)
    # return
    return 0

def get_expected_n_evts(xs, lumi, name, event):
    """
    Return the expected number of events based on cross section, integrated
    luminosity, and the physics process.
    
    Parameters
    ----------
    xs : float
        Cross section of the physics process.
    lumi : float
        Luminosity (pb^{-1}).
    name : str
        Shorthand name of physics process (e.g. 'ZZ').
    event : TTree event obj
    """
    n_exp = xs * lumi
    if "ZZ" in name:
        n_exp *= (event.k_qqZZ_qcd_M * event.k_qqZZ_ewk)
    return n_exp

def get_evt_weight(isData, xs_dct, Nickname, lumi, event, n_obs_tot):
    """
    Return the corrected weight of event for MC based on data.

    Generally:
    new_weight = old_weight * (xs * L_int / N_events_from_MC)

    Parameters
    ----------
    isData : bool
    xs_dct : dict
        key (str) => nickname of physics process
        val (float) => cross section
    Nickname : str
        Code name of data set.
    lumi : float
        Integrated luminosity (pb^{-1}).
    event : TTree event
    n_obs_tot : int
        The total number of events in the data set which you processed.
        Do: `crab report -d <dir>`.
    """
    if isData:
        return 1
    else:
        # Sample is Monte Carlo.
        xs = xs_dct[Nickname]
        n_exp = get_expected_n_evts(xs, lumi, Nickname, event)
        old_weight = event.eventWeight
        new_weight = old_weight * (n_exp / n_obs_tot)
        return new_weight

def make_hist_name(kinem, control_reg, fs):
    """
    Return the name (str) of a histogram based on a kinematic variable,
    control region, and final state.
    """
    return f"h1D_{kinem}_{control_reg}_{fs}"

def make_hist_dct(kinem_ls, kinem_info_dct):
    """
    Return a dict of kinem hists made for 5 final states and 3 Z+LL CRs.
    
    Example of key, val pair:
    h1D_m4l_2P2F : rt.TH1D("h1D_m4l_2P2F_4mu", "h1D_m4l_2P2F_4mu",
                           n_bins, x_min, x_max)

    Parameters
    ----------
    kinem_ls : list of str
    kinem_info_dct : dict
        Contains binning info for kinematics distributions.
    """
    hist_d = {}
    for control_reg in "3P1F 2P2F".split():
        for fs in "inclus 4e 4mu 2e2mu 2mu2e".split():
            for kinem in kinem_ls:
                name = make_hist_name(kinem=kinem, control_reg=control_reg, fs=fs)
                n_bins = kinem_info_dct[kinem]["n_bins"]
                xlabel = kinem_info_dct[kinem]["x_label"]
                x_min = kinem_info_dct[kinem]["x_min"]
                x_max = kinem_info_dct[kinem]["x_max"]
                units = kinem_info_dct[kinem]["units"]
                h = make_TH1F(name, title=name,
                                    n_bins=n_bins, xlabel=xlabel,
                                    x_min=x_min, x_max=x_max, units=units)
                hist_d[name] = h.Clone()
    return hist_d

def fill_hists(event, weight, hist_dct, kinem_ls, control_reg, fs):
    """
    Fill the hists in `hist_dct` for this `event` for the
    specified kinematic vars in `kinem_ls`, for the given final state `fs`,
    for the given control region `control_reg`.
    """
    for kinem in kinem_ls:
        name = make_hist_name(kinem=kinem, control_reg=control_reg, fs=fs)
        h = hist_dct[name]
        val = getattr(event, kinem)
        h.Fill(val, weight)

def fill_hists_in_controlreg(event, weight, hist_dct, kinem_ls,
                                control_reg, finalstate_4L, finalstate_2L):
    """Fill inclusive and `finalstate_4L` kinematic hists.
    
    NOTE: finalstate_2L is used to determine whether 2e2mu or 2mu2e.
    """
    fill_hists(
        event=event, weight=weight, hist_dct=hist_dct,
        kinem_ls=kinem_ls, control_reg=control_reg, fs="inclus")

    if finalstate_4L == finalstate_dct["4e"]:
        fill_hists(
            event=event, weight=weight, hist_dct=hist_dct,
            kinem_ls=kinem_ls, control_reg=control_reg, fs="4e")

    elif finalstate_4L == finalstate_dct["4mu"]:
        fill_hists(
            event=event, weight=weight, hist_dct=hist_dct,
            kinem_ls=kinem_ls, control_reg=control_reg, fs="4mu")

    elif finalstate_4L == finalstate_dct["2e2mu"]:
        # Did Z_2 produce 2e or 2mu?
        if finalstate_2L == finalstate_dct["2e"]:
            fill_hists(
                event=event, weight=weight, hist_dct=hist_dct,
                kinem_ls=kinem_ls, control_reg=control_reg, fs="2mu2e")

        elif finalstate_2L == finalstate_dct["2mu"]:
            fill_hists(
                event=event, weight=weight, hist_dct=hist_dct,
                kinem_ls=kinem_ls, control_reg=control_reg, fs="2e2mu")

def reconstruct_Zcand_leptons(event):
    """Return (lep_1, lep_2) which make Z1 from event."""
    lep_1 = rt.TLorentzVector()
    lep_2 = rt.TLorentzVector()
    ndx0 = event.lep_Hindex[0]
    ndx1 = event.lep_Hindex[1]
    lep_1.SetPtEtaPhiM(event.lep_pt[ndx0], event.lep_eta[ndx0], event.lep_phi[ndx0], event.lep_mass[ndx0])
    lep_2.SetPtEtaPhiM(event.lep_pt[ndx1], event.lep_eta[ndx1], event.lep_phi[ndx1], event.lep_mass[ndx1])
    return (lep_1, lep_2)

def analyzeZX(fTemplateTree, Nickname, varName="ptl3", lumi=59700, kinem_ls):
    """

    TODO: Update docstring.

    Parameters
    ----------
    kinem_ls : list of str
    """
    
    study_particle_origins = False
    max_events = -1
        
    kinem_info_dct = {
        "mass4l" : {
            "n_bins" : 100,
            "x_label" : r'm_{4#ell}',
            "x_min" : 70,
            "x_max" : 170,
            "units" : "GeV",
            },
        "mass4lREFIT" : {
            "n_bins" : 100,
            "x_label" : r'm_{4#ell}^{refit}',
            "x_min" : 70,
            "x_max" : 170,
            "units" : "GeV",
            },
        "mass4lREFIT_vtx_BS" : {
            "n_bins" : 100,
            "x_label" : r'm_{4#ell}^{refit, VX+BS}',
            "x_min" : 70,
            "x_max" : 170,
            "units" : "GeV",
            },
        "mass4lErr" : {
            "n_bins" : 80,
            "x_label" : r'#deltam_{4#ell}',
            "x_min" : 0,
            "x_max" : 8,
            "units" : "GeV",
            },
        "mass4lErrREFIT" : {
            "n_bins" : 80,
            "x_label" : r'#deltam_{4#ell}^{refit}',
            "x_min" : 0,
            "x_max" : 8,
            "units" : "GeV",
            },
        "mass4lErrREFIT_vtx_BS" : {
            "n_bins" : 80,
            "x_label" : r'#deltam_{4#ell}^{refit, VX+BS}',
            "x_min" : 0,
            "x_max" : 8,
            "units" : "GeV",
            },
        "met" : {
            "n_bins" : 100,
            "x_label" : r'MET',
            "x_min" : 0,
            "x_max" : 50,
            "units" : "GeV",
            },
        "D_bkg_kin" : {
            "n_bins" : 10,
            "x_label" : r'D^{kin}_{bkg}',
            "x_min" : 0,
            "x_max" : 1,
            "units" : None,
            },
        "D_bkg_kin_vtx_BS" : {
            "n_bins" : 10,
            "x_label" : r'D^{kin, VX+BS}_{bkg}',
            "x_min" : 0,
            "x_max" : 1,
            "units" : None,
            },
    }

    lineWidth = 2
    leg_xl = 0.50
    leg_xr = 0.90
    leg_yb = 0.72 
    leg_yt = 0.90

    CR_var_plotHigh = 870.0
    CR_var_plotLow = 70.0
    CR_var_nBins = 40

    var_plotHigh = 120
    var_plotLow = 60
    var_nBins = 20
    varAxLabel = "m_{Z1}"

    PtlBins = np.array([       7.0, 10.0, 20.0, 30.0, 40.0, 50.0, 80.0])  # Electrons.
    PtlBinsMu = np.array([5.0, 7.0, 10.0, 20.0, 30.0, 40.0, 50.0, 80.0])  # Muons.

    print ("--- Initiating the analyzeZX procedure for file nicknamed as: "+ Nickname +".")
    
    if (varName=="mEt"):
        var_plotHigh = 50
        var_plotLow = 0
        var_nBins = 10
        varAxLabel = "E_{T,miss}"
    
    #initiate numerator and denominator histograms for FR computation

    binWidth = ((int) (100*(var_plotHigh - var_plotLow)/var_nBins))/100.
    sUnit = "GeV"
    
    # Make pT hists for loose lepton.
    if (varName=="ptl3"):
        # h1D_dummy = rt.TH1D("dummy", "dummy", len(PtlBins), PtlBins)
        # setHistProperties(h1D_dummy,1,1,1,0,0,varAxLabel,"Misidentification rate")
        
        # Define FR numerator histograms.
        h1D_FRel_EB = rt.TH1D("h1D_FRel_EB","h1D_FRel_EB", len(PtlBins)-1, PtlBins) 
        h1D_FRel_EE = rt.TH1D("h1D_FRel_EE","h1D_FRel_EE", len(PtlBins)-1, PtlBins) 
        h1D_FRmu_EB = rt.TH1D("h1D_FRmu_EB","h1D_FRmu_EB", len(PtlBinsMu)-1, PtlBinsMu) 
        h1D_FRmu_EE = rt.TH1D("h1D_FRmu_EE","h1D_FRmu_EE", len(PtlBinsMu)-1, PtlBinsMu) 
        
        # Define FR denominator histograms.
        h1D_FRel_EB_d = rt.TH1D("h1D_FRel_EB_d","h1D_FRel_EB_d", len(PtlBins)-1, PtlBins) 
        h1D_FRel_EE_d = rt.TH1D("h1D_FRel_EE_d","h1D_FRel_EE_d", len(PtlBins)-1, PtlBins) 
        h1D_FRmu_EB_d = rt.TH1D("h1D_FRmu_EB_d","h1D_FRmu_EB_d", len(PtlBinsMu)-1, PtlBinsMu) 
        h1D_FRmu_EE_d = rt.TH1D("h1D_FRmu_EE_d","h1D_FRmu_EE_d", len(PtlBinsMu)-1, PtlBinsMu) 

        all_FR_hist_ls = [
            h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
            h1D_FRel_EB_d, h1D_FRel_EE_d, h1D_FRmu_EB_d, h1D_FRmu_EE_d
            ]
    else:
        # h1D_dummy = rt.TH1D("dummy", "dummy", var_nBins, var_plotLow, var_plotHigh)
        # setHistProperties(h1D_dummy,1,1,1,0,0,varAxLabel,"Misidentification rate")

        # define FR numerator histograms
        h1D_FRel_EB = rt.TH1D("h1D_FRel_EB","h1D_FRel_EB",var_nBins, var_plotLow, var_plotHigh)
        h1D_FRel_EE = rt.TH1D("h1D_FRel_EE","h1D_FRel_EE",var_nBins, var_plotLow, var_plotHigh)
        h1D_FRmu_EB = rt.TH1D("h1D_FRmu_EB","h1D_FRmu_EB",var_nBins, var_plotLow, var_plotHigh) 
        h1D_FRmu_EE = rt.TH1D("h1D_FRmu_EE","h1D_FRmu_EE",var_nBins, var_plotLow, var_plotHigh) 
    
        # define FR denominator histograms
        h1D_FRel_EB_d = rt.TH1D("h1D_FRel_EB_d","h1D_FRel_EB_d",var_nBins, var_plotLow, var_plotHigh) 
        h1D_FRel_EE_d = rt.TH1D("h1D_FRel_EE_d","h1D_FRel_EE_d",var_nBins, var_plotLow, var_plotHigh) 
        h1D_FRmu_EB_d = rt.TH1D("h1D_FRmu_EB_d","h1D_FRmu_EB_d",var_nBins, var_plotLow, var_plotHigh) 
        h1D_FRmu_EE_d = rt.TH1D("h1D_FRmu_EE_d","h1D_FRmu_EE_d",var_nBins, var_plotLow, var_plotHigh) 

    print("...Making kinematic hists in XPYF control regions.")
    hist_dct = make_hist_dct(kinem_ls, kinem_info_dct)

    # Propagate errors.
    for h in all_FR_hist_ls + list(hist_dct.values()):
        h.Sumw2()

    isData = "Data" in Nickname
    nentries = fTemplateTree.GetEntries()
    n_tot_failedleps = 0

    # Begin: Define histograms for uncertainty studies (separating fakes per type of fake) 
    order = [
        "EB_n", "EB_d", "EE_n", "EE_d",
        "MB_n", "MB_d", "ME_n", "ME_d"
        ]
    CRSection = [
        "2P2F", "2P2F4e", "2P2F4mu", "2P2F2e2mu", "2P2F2mu2e",
        "3P1F", "3P1F4e", "3P1F4mu", "3P1F2e2mu", "3P1F2mu2e"
        ]

    ID = {"Prom", "Fake", "Conv", "BDfake"}

    ## Define CR histograms for Prompt/Fake/Conversion and BDfakes    
    CR = []  # list of lists of hists.
    CR_Prom = []
    CR_Fake = []
    CR_Conv = []
    CR_BDfake = []

    for count in range(CRregion._3P1F_2mu2e + 1): # _3P1F_2e2mu = 8
        CR_Prom.append(rt.TH1D("h1D_m4l_Prom_"+CRSection[count], "h1D_m4l_Prom_"+CRSection[count], CR_var_nBins, CR_var_plotLow, CR_var_plotHigh))
        CR_Prom[count].Sumw2()

        CR_Fake.append(rt.TH1D("h1D_m4l_Fake_"+CRSection[count], "h1D_m4l_Fake_"+CRSection[count], CR_var_nBins, CR_var_plotLow, CR_var_plotHigh))
        CR_Fake[count].Sumw2()

        CR_Conv.append(rt.TH1D("h1D_m4l_Conv_"+CRSection[count], "h1D_m4l_Conv_"+CRSection[count], CR_var_nBins, CR_var_plotLow, CR_var_plotHigh))
        CR_Conv[count].Sumw2()

        CR_BDfake.append(rt.TH1D("h1D_m4l_BDfake_"+CRSection[count], "h1D_m4l_BDfake_"+CRSection[count], CR_var_nBins, CR_var_plotLow, CR_var_plotHigh))
        CR_BDfake[count].Sumw2()

    CR.append(CR_Prom)
    CR.append(CR_Fake)
    CR.append(CR_Conv)
    CR.append(CR_BDfake)

    ## Define numerator/denominator histograms for Prompt/Fake/Conversion and BDfakes in Z+L region.
    Hist_conv = []
    Hist_prompt = []
    Hist_fakes = []
    Hist_BDfakes = []

    for count in range(barrel_endcap_region.ME_d+1):  # ME_d = 7
    
        if (varName=="ptl3") and (count < barrel_endcap_region.MB_n):  # MB_n = 4
            # Hists 0-3 are dedicated to electrons?
            Hist_conv.append(rt.TH1D("Hist_conv"+order[count] ,"Hist_conv"+order[count], len(PtlBins)-1, PtlBins))
            Hist_conv[count].Sumw2()

            Hist_prompt.append(rt.TH1D("Hist_prompt"+order[count],"Hist_prompt"+order[count], len(PtlBins)-1, PtlBins))
            Hist_prompt[count].Sumw2()

            Hist_fakes.append(rt.TH1D("Hist_fakes"+order[count],"Hist_fakes"+order[count], len(PtlBins)-1, PtlBins))
            Hist_fakes[count].Sumw2()

            Hist_BDfakes.append(rt.TH1D("Hist_BDfakes"+order[count],"Hist_BDfakes"+order[count], len(PtlBins)-1, PtlBins))
            Hist_BDfakes[count].Sumw2()

        elif (varName=="ptl3") and (count >= barrel_endcap_region.MB_n):
            # Hists 0-3 are dedicated to muons?
            Hist_conv.append(rt.TH1D("Hist_conv"+order[count] ,"Hist_conv"+order[count], len(PtlBinsMu)-1, PtlBinsMu))
            Hist_conv[count].Sumw2()

            Hist_prompt.append(rt.TH1D("Hist_prompt"+order[count],"Hist_prompt"+order[count], len(PtlBinsMu)-1, PtlBinsMu))
            Hist_prompt[count].Sumw2()

            Hist_fakes.append(rt.TH1D("Hist_fakes"+order[count],"Hist_fakes"+order[count], len(PtlBinsMu)-1, PtlBinsMu))
            Hist_fakes[count].Sumw2()

            Hist_BDfakes.append(rt.TH1D("Hist_BDfakes"+order[count],"Hist_BDfakes"+order[count], len(PtlBinsMu)-1, PtlBinsMu))
            Hist_BDfakes[count].Sumw2()
        
        #--- Don't think will trigger.
        # else:
        #     Hist_conv.append(rt.TH1D("Hist_conv"+order[count] ,"Hist_conv"+order[count],var_nBins, var_plotLow, var_plotHigh))
        #     Hist_conv[count].Sumw2()

        #     Hist_prompt.append(rt.TH1D("Hist_prompt"+order[count],"Hist_prompt"+order[count],var_nBins, var_plotLow, var_plotHigh))
        #     Hist_prompt[count].Sumw2()

        #     Hist_fakes.append(rt.TH1D("Hist_fakes"+order[count],"Hist_fakes"+order[count],var_nBins, var_plotLow, var_plotHigh))
        #     Hist_fakes[count].Sumw2()

        #     Hist_BDfakes.append(rt.TH1D("Hist_BDfakes"+order[count],"Hist_BDfakes"+order[count],var_nBins, var_plotLow, var_plotHigh))
        #     Hist_BDfakes[count].Sumw2()
    # End: Define histograms for uncertainty studies (separating fakes per type of fake) 

    for iEvt, event in enumerate(fTemplateTree):
        if (iEvt % 50000 == 0):
            print (f"Processing event: {iEvt}/{nentries}")
        # if iEvt == max_events:
        #     break
            
        # Get total number of events from MC/Data files.
        # Use the L_int and xs to determine n_expected and event weights.
        n_obs_tot = float(n_totevts_dataset_dct[Nickname])
        weight = get_evt_weight(isData, xs_dct, Nickname, lumi, event, n_obs_tot)

        #######################################
        #--- CR: Z+L for fake rate studies ---#
        #######################################
        if event.passedZ1LSelection:
            # We got some kind of Z+L event.
            # It should only be from Z+jets or Zgamma+jets.
            # However WZ events produce a Z and a prompt lepton.
            # We will remove WZ later.
            # If lep3 passes tight selection, then it's likely a fake
            # since we are only looking for 3 lep events right now.
            # How frequently does this happen? I.e. what is the fake rate?

            # First, reconstruct Z candidate.
            lep_1, lep_2 = reconstruct_Zcand_leptons(event)
            lep_3 = rt.TLorentzVector()
            massZ1 = (lep_1 + lep_2).M()

            # Get info about third lepton, which is at least loose.
            ndx_loose = event.lep_Hindex[2]
            lep_tight = event.lep_tightId[ndx_loose]
            lep_iso = event.lep_RelIsoNoFSR[ndx_loose]
            idL3 = event.lep_id[ndx_loose]
            lep_3.SetPtEtaPhiM(event.lep_pt[ndx_loose],
                             event.lep_eta[ndx_loose],
                             event.lep_phi[ndx_loose],
                             event.lep_mass[ndx_loose])
            pTL3  = lep_3.Pt()
            etaL3 = lep_3.Eta()
            phiL3 = lep_3.Phi()
            
            lep_matchedR03_PdgId = event.lep_matchedR03_PdgId
            lep_matchedR03_MomId = event.lep_matchedR03_MomId
            lep_matchedR03_MomMomId = event.lep_matchedR03_MomMomId
            lep_id = event.lep_id
            lep_Hindex = event.lep_Hindex

            TestVar=False
            FillVar=0.
            
            #--- Currently not used. ---#
            # if (varName=="mZ1"):
            #     TestVar= 1
            #     FillVar= massZ1
            
            # if (varName=="mEt"):
            #     TestVar= 1
            #     FillVar= event.met
            
            if varName=="ptl3":
                tight_mZ_window = math.fabs(massZ1 - MZ_PDG) < 7
                low_MET = event.met < 25
                TestVar = tight_mZ_window and low_MET
                FillVar = pTL3

            # Sort lep3 if electron.
            if ((abs(idL3) == 11) and (math.fabs(etaL3) < 1.497) and TestVar):
                h1D_FRel_EB_d.Fill(FillVar, weight)
                PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EB_d], Hist_fakes[barrel_endcap_region.EB_d], Hist_BDfakes[barrel_endcap_region.EB_d], Hist_conv[barrel_endcap_region.EB_d],False)
                if (lep_tight and TestVar):
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EB_n], Hist_fakes[barrel_endcap_region.EB_n],Hist_BDfakes[barrel_endcap_region.EB_n],Hist_conv[barrel_endcap_region.EB_n],False)
                    h1D_FRel_EB.Fill(FillVar, weight)

            if ((abs(idL3) == 11) and (math.fabs(etaL3) > 1.497) and TestVar):
                h1D_FRel_EE_d.Fill(FillVar, weight)
                PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EE_d], Hist_fakes[barrel_endcap_region.EE_d],Hist_BDfakes[barrel_endcap_region.EE_d], Hist_conv[barrel_endcap_region.EE_d],False)
                
                if lep_tight and TestVar:
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EE_n], Hist_fakes[barrel_endcap_region.EE_n], Hist_BDfakes[barrel_endcap_region.EE_n], Hist_conv[barrel_endcap_region.EE_n],False)
                    h1D_FRel_EE.Fill(FillVar, weight)

            # Sort lep3 if muon.
            if ((abs(idL3) == 13) and (math.fabs(etaL3) < 1.2) and TestVar):
                h1D_FRmu_EB_d.Fill(FillVar, weight)
                PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.MB_d], Hist_fakes[barrel_endcap_region.MB_d], Hist_BDfakes[barrel_endcap_region.MB_d], Hist_conv[barrel_endcap_region.MB_d],False)
                
                if (lep_tight and (lep_iso < 0.35) and TestVar):
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.MB_n], Hist_fakes[barrel_endcap_region.MB_n],Hist_BDfakes[barrel_endcap_region.MB_n], Hist_conv[barrel_endcap_region.MB_n],False)
                    h1D_FRmu_EB.Fill(FillVar, weight)

            if ((abs(idL3) == 13) and (math.fabs(etaL3) > 1.2) and TestVar):
                h1D_FRmu_EE_d.Fill(FillVar, weight)
                PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.ME_d], Hist_fakes[barrel_endcap_region.ME_d],Hist_BDfakes[barrel_endcap_region.ME_d], Hist_conv[barrel_endcap_region.ME_d],False)
                
                if (lep_tight and (lep_iso < 0.35) and TestVar):
                    #PartOrigin(lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[ME_n], Hist_fakes[ME_n],Hist_BDfakes[ME_n], Hist_conv[ME_n],false)
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.ME_n], Hist_fakes[barrel_endcap_region.ME_n],Hist_BDfakes[barrel_endcap_region.ME_n], Hist_conv[barrel_endcap_region.ME_n],False)
                    h1D_FRmu_EE.Fill(FillVar, weight)

        #########################
        #--- CR: Z+LL (XPYF) ---#
        #########################
        elif event.passedZXCRSelection and varName == "ptl3":
            # We got at least 1 fake lepton.

            # Collect info about 4 leps from "H candidate".
            lep_tight = []
            lep_iso = []
            idL = []
            for k in range(4):
                lep_tight.append(event.lep_tightId[event.lep_Hindex[k]])
                lep_iso.append(event.lep_RelIsoNoFSR[event.lep_Hindex[k]])
                idL.append(event.lep_id[event.lep_Hindex[k]])

            #--- Not yet implemented. ---#
            # lep_3.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[2]], event.lep_eta[event.lep_Hindex[2]], event.lep_phi[event.lep_Hindex[2]], event.lep_mass[event.lep_Hindex[2]])
            # pTL3  = lep_3.Pt()
            # etaL3 = lep_3.Eta()
            # phiL3 = lep_3.Phi()

            # lep_4.SetPtEtaPhiM(event.lep_pt[event.lep_Hindex[3]], event.lep_eta[event.lep_Hindex[3]], event.lep_phi[event.lep_Hindex[3]], event.lep_mass[event.lep_Hindex[3]])
            # pTL4  = lep_4.Pt()
            # etaL4 = lep_4.Eta()
            # phiL4 = lep_4.Phi()
            # DR = math.sqrt((phiL3-phiL4)*(phiL3-phiL4) + (etaL3-etaL4)*(etaL3-etaL4))
            
            lep_1, lep_2 = reconstruct_Zcand_leptons(event)
            massZ1 = (lep_1+lep_2).M()

            assert len(list(lep_tight)) < 5
            # failed lep = not (tight and good e/mu)
            nFailedLeptons1 = not (lep_tight[0] and ((abs(idL[0])==11) or (abs(idL[0])==13 and lep_iso[0]<0.35)))
            nFailedLeptons2 = not (lep_tight[1] and ((abs(idL[1])==11) or (abs(idL[1])==13 and lep_iso[1]<0.35)))
            nFailedLeptonsZ1 = nFailedLeptons1 + nFailedLeptons2

            nFailedLeptons3 = not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35)))
            nFailedLeptons4 = not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))
            nFailedLeptonsZ2 = nFailedLeptons3 + nFailedLeptons4
            
            nFailedLeptons = nFailedLeptonsZ1 + nFailedLeptonsZ2

            #nFailedLeptonsZ1 = not (lep_tight[0] and ((abs(idL[0])==11) or (abs(idL[0])==13 and lep_iso[0]<0.35))) + not (lep_tight[1] and ((abs(idL[1])==11) or (abs(idL[1])==13 and lep_iso[1]<0.35)))
            #nFailedLeptonsZ2 = not (lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35))) + not (lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))          
            #nFailedLeptons = nFailedLeptonsZ1 + nFailedLeptonsZ2

            # 4e = 44, 4mu = 52, 2e2mu or 2mu2e = 48
            finalstate_4L = get_sum_absIDs(idL)
            finalstate_2L = get_sum_absIDs(idL[2:])  # Final 2 leps.

            # Fill appropriate XPYF m4l hist.
            if nFailedLeptons == 1:
                conreg = "3P1F"
            elif nFailedLeptons == 2:
                conreg = "2P2F"
            else:
                msg = f"nFailedLeptons={nFailedLeptons} but should be 1 or 2."
                raise ValueError(msg)

            fill_hists_in_controlreg(
                event=event, weight=weight, hist_dct=hist_dct,
                kinem_ls=kinem_ls, control_reg=conreg,
                finalstate_4L=finalstate_4L, finalstate_2L=finalstate_2L)
                
    # Save the plots.
    Data_string = "Data" if isData else "MC"
    outfile_path = f"../data/Hist_{Data_string}_{varName}_{Nickname}.root"
    # check_overwrite(outfile_path, overwrite=False)
    suffix = 0
    while os.path.exists(outfile_path):
        print(f"#--- Renaming: {outfile_path}")
        outfile_path = f"""{outfile_path.rstrip('.root')}_{suffix}.root"""
        suffix += 1

    SaveRootFile = rt.TFile(outfile_path, "RECREATE")
    
    h1D_FRel_EE_n = h1D_FRel_EE.Clone()
    h1D_FRmu_EE_n = h1D_FRmu_EE.Clone()
    h1D_FRel_EB_n = h1D_FRel_EB.Clone()
    h1D_FRmu_EB_n = h1D_FRmu_EB.Clone()
    
    # divide hists to get the fake rates
    h1D_FRel_EB_n.Divide(h1D_FRel_EB_d)
    h1D_FRel_EE_n.Divide(h1D_FRel_EE_d)
    h1D_FRmu_EB_n.Divide(h1D_FRmu_EB_d)
    h1D_FRmu_EE_n.Divide(h1D_FRmu_EE_d)
    
    h1D_FRel_EB_n.GetYaxis().SetRangeUser(0.01, 0.35) 
    h1D_FRel_EE_n.GetYaxis().SetRangeUser(0.01, 0.35)
    h1D_FRmu_EB_n.GetYaxis().SetRangeUser(0.04, 0.35)
    h1D_FRmu_EE_n.GetYaxis().SetRangeUser(0.04, 0.35)
    #Save histograms in .root file
    
    h1D_FRel_EB.SetName("Data_FRel_EB_n")
    h1D_FRel_EB.Write()
    h1D_FRel_EE.SetName("Data_FRel_EE_n") 
    h1D_FRel_EE.Write()
    h1D_FRmu_EB.SetName("Data_FRmu_EB_n") 
    h1D_FRmu_EB.Write()
    h1D_FRmu_EE.SetName("Data_FRmu_EE_n") 
    h1D_FRmu_EE.Write()
    
    h1D_FRel_EB_d.SetName("Data_FRel_EB_d") 
    h1D_FRel_EB_d.Write()
    h1D_FRel_EE_d.SetName("Data_FRel_EE_d") 
    h1D_FRel_EE_d.Write()
    h1D_FRmu_EB_d.SetName("Data_FRmu_EB_d") 
    h1D_FRmu_EB_d.Write()
    h1D_FRmu_EE_d.SetName("Data_FRmu_EE_d") 
    h1D_FRmu_EE_d.Write()
    
    h1D_FRel_EB_n.SetName("Data_FRel_EB") 
    h1D_FRel_EB_n.Write()
    h1D_FRel_EE_n.SetName("Data_FRel_EE") 
    h1D_FRel_EE_n.Write()
    h1D_FRmu_EB_n.SetName("Data_FRmu_EB") 
    h1D_FRmu_EB_n.Write()
    h1D_FRmu_EE_n.SetName("Data_FRmu_EE") 
    h1D_FRmu_EE_n.Write()
    
    print("...Storing kinematic histograms in '.root' file.")
    for h in hist_dct.values():
        h.Write()
    
    SaveRootFile.Close()

    # Storing the plots per type of fakes.
    if study_particle_origins:
        SaveRootFile_Types_of_fake = rt.TFile("Hist_ID_"+varName+"_"+Nickname+".root", "RECREATE")

        for count in range(CRregion._3P1F_2mu2e+1):    
            for t in range(type_of_fake.BDfake+1): 
                CR_Prom[count].Write()
                CR_Fake[count].Write()
                CR_Conv[count].Write()
                CR_BDfake[count].Write()

        for count in range(barrel_endcap_region.ME_d+1):
                Hist_conv[count].Write()
                Hist_prompt[count].Write()
                Hist_fakes[count].Write()
                Hist_BDfakes[count].Write()

        SaveRootFile_Types_of_fake.Close()