"""Determine Fake Rates and OS Z+LL Control Regions

TODO: Finish code docstring.

This code selects events from Data/MC samples which pass either Z+L or Z+LL
control regions (CR), separating them by CRs.

The following histograms are produced:
- TODO

- Fake rates (the number of leptons which )

Use with MC samples:
    WZ, ttbar, DY (reducible backgrounds)

Syntax to run: `python <this_script>.py`
Author: Jake Rosenzweig
Original code: Vukasin Milosevic
Created: 2021-Mar-ish
Updated: 2022-02-09
"""
import os
import sys
import math
import ROOT as rt
import numpy as np
# from Utils_Python.Utils_Files import check_overwrite
from scripts.helpers.MC_composition import PartOrigin
from constants.analysis_params import dct_xs_jake, MZ_PDG, LUMI_INT_2018_Jake, n_sumgenweights_dataset_dct_jake
# from HiggsMassMeasurement.Utils_ROOT.ROOT_classes import make_TH1F
from Utils_ROOT.ROOT_classes import make_TH1F
from Utils_Python.Utils_Files import check_overwrite

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

def get_expected_n_evts(xs, lumi, isMCzz, event):
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
    if isMCzz:
        n_exp *= (event.k_qqZZ_qcd_M * event.k_qqZZ_ewk)
    return n_exp

def get_evt_weight(
    dct_xs,
    Nickname,
    lumi,
    event,
    n_dataset_tot,
    orig_evt_weight
    ):
    """
    Return the event weight of Data (1) or MC based on L_int collected.

    To weight MC events:
    new_weight = old_weight * (xs * L_int / N_events_from_MC)

    Parameters
    ----------
    dct_xs : dict
        key (str) => nickname of physics process
        val (float) => cross section
    Nickname : str
        Code name of data set.
    lumi : float
        Integrated luminosity (pb^{-1}).
    event : TTree event
        The event object from which you can extract kinematics.
        E.g., event.lep_pt
    n_dataset_tot : int
        The total number of events in the MC data set which you processed.
        Do: `crab report -d <dir>`.
    orig_evt_weight : float
        The original event weight.
        For a BBF NTuple, typically: tree.eventWeight.

    Elisa uses:
    n_events = _lumi * 1000 * xsec * _k_factor * overallEventWeight * L1prefiringWeight) / gen_sum_weights;

    NOTE:
    Jake's old 2018 Data, LUMI_INT = 57750.
    Filippo's 2018 Data, LUMI_INT = 59830
        (from: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVRun2LegacyAnalysis).
    """
    isData = 1 if Nickname in "Data" else 0
    isMCzz = 1 if Nickname in "ZZ" else 0
    if isData:
        return 1
    else:
        # Sample is Monte Carlo.
        xs = dct_xs[Nickname]
        n_exp = get_expected_n_evts(xs, lumi, isMCzz, event)
        # newweight/oldweight = n_exp/n_obs = (L_int * xs * eff) / n_obs
        new_weight = orig_evt_weight * (n_exp / n_dataset_tot)
        return new_weight

def check_which_Z2_leps_failed(zz_pair):
    """Return code telling which leptons from Z2 failed tight selection.

    Args:
        zz_pair (ZZPair): Contains quartet of MyLepton objects.
    
    NOTE:
        - zz_pair.z_sec should be the MyZboson which is assigned as Z2.
    
    Returns
    -------
    0, if neither lep from Z2 failed.
    2, if first lep from Z2 failed.
    3, if second lep from Z2 failed.
    5, if both leps from Z2 failed.
    """
    # See if leps 3 and 4 failed.
    lep3_failed = zz_pair.z_sec.mylep1.is_loose
    lep4_failed = zz_pair.z_sec.mylep2.is_loose

    if lep3_failed and (not lep4_failed):
        return 2
    elif (not lep3_failed) and lep4_failed:
        return 3
    elif lep3_failed and lep4_failed:
        return 5
    else:
        return 0

def make_hist_name(kinem, control_reg, fs):
    """
    Return the name (str) of a histogram based on a kinematic variable,
    control region, and final state.
    """
    return f"h1D_{kinem}_{control_reg}_{fs}"

def make_hist_dct(kinem_ls, kinem_info_dct):
    """Return a dict of kinem hists made for 5 final states and 3 Z+LL CRs.
    
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

    Parameters
    ----------
    event : ROOT.TTree event
    hist_dct : dict of empty TH1D
    kinem_ls : list of str
    control_reg : str
        Either: '3P1F' or '2P2F'
    finalstate_4L : float
        The sum of the abs(lep IDs) in the 4 lepton final state.
    finalstate_2L : float
        The sum of the abs(lep IDs) of the 2 leptons comprising the Z2.
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

def get_fakerate_and_error_mylep(
    mylep,
    h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
    eta_bound_elec=1.497, eta_bound_muon=1.2,
    verbose=False
    ):
    """Return the fake rate and error based on `mylep` kinematics.
    
    Returns:
        tuple(
            fake_rate (float),
            fake_rate_err (float)
            )
    NOTE: Get fake rates based on lep pT and eta WITHOUT reco!
    """
    fr, fr_err = get_fakerate_and_error(
        mylep.lid, mylep.lpt_NoFSR, mylep.leta_NoFSR,
        h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
        eta_bound_elec=eta_bound_elec,
        eta_bound_muon=eta_bound_muon,
        verbose=verbose,
        )
    return (fr, fr_err)

def get_fakerate_and_error(
    lep_id, lep_pt, lep_eta,
    h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
    eta_bound_elec=1.497, eta_bound_muon=1.2,
    verbose=False,
    ):
    """Return the fake rate and error based on lep ID, pT, and eta.
    
    Returns:
        tuple(
            fake_rate (float),
            fake_rate_err (float)
            )
    
    NOTE: Get fake rates based on lep pT and eta WITHOUT FSR!
    """
    if verbose:
        print("Retrieving fake rates.")
        # Prep info message.
        info = (
            f"  PART in REG region:\n"
            f"    pt_NoFSR={lep_pt:.6f}, "
            f"abs(eta_NoFSR)=abs({lep_eta:.6f}) SIGN BOUND gives"
            f" fakerate=FR +- ERR"
        )
    # Electrons.
    if abs(lep_id) == 11:
        if abs(lep_eta) < eta_bound_elec:
            bin_num = h1D_FRel_EB.FindBin(lep_pt)
            fr = h1D_FRel_EB.GetBinContent(bin_num)
            fr_err = h1D_FRel_EB.GetBinError(bin_num)
            if verbose:
                print(
                    info.replace("PART", "electron")
                        .replace("REG", "barrel")
                        .replace("SIGN", "<")
                        .replace("BOUND", f"{eta_bound_elec}")
                        .replace("FR", f"{fr:.6f}")
                        .replace("ERR", f"{fr_err:.6f}")
                    )
            return (fr, fr_err)
        else:
            bin_num = h1D_FRel_EE.FindBin(lep_pt)
            fr = h1D_FRel_EE.GetBinContent(bin_num)
            fr_err = h1D_FRel_EE.GetBinError(bin_num)
            if verbose:
                print(
                    info.replace("PART", "electron")
                        .replace("REG", "endcap")
                        .replace("SIGN", ">")
                        .replace("BOUND", f"{eta_bound_elec}")
                        .replace("FR", f"{fr:.6f}")
                        .replace("ERR", f"{fr_err:.6f}")
                    )
            return (fr, fr_err)
    # Muons.
    elif abs(lep_id) == 13:
        if abs(lep_eta) < eta_bound_muon:
            bin_num = h1D_FRmu_EB.FindBin(lep_pt)
            fr = h1D_FRmu_EB.GetBinContent(bin_num)
            fr_err = h1D_FRmu_EB.GetBinError(bin_num)
            if verbose:
                print(
                    info.replace("PART", "muon")
                        .replace("REG", "barrel")
                        .replace("SIGN", "<")
                        .replace("BOUND", f"{eta_bound_muon}")
                        .replace("FR", f"{fr:.6f}")
                        .replace("ERR", f"{fr_err:.6f}")
                    )
            return (fr, fr_err)
        else:
            bin_num = h1D_FRmu_EE.FindBin(lep_pt)
            fr = h1D_FRmu_EE.GetBinContent(bin_num)
            fr_err = h1D_FRmu_EE.GetBinError(bin_num)
            if verbose:
                print(
                    info.replace("PART", "muon")
                        .replace("REG", "endcap")
                        .replace("SIGN", ">")
                        .replace("BOUND", f"{eta_bound_muon}")
                        .replace("FR", f"{fr:.6f}")
                        .replace("ERR", f"{fr_err:.6f}")
                    )
            return (fr, fr_err)
    else:
        err_msg = (
            f"abs(lep_id) == {abs(lep_id)} "
            f"but should be either 11 or 13."
            )
        raise ValueError(err_msg)
    
def calc_fakerate_up(fr, fr_err):
    """Return the value: (fake rate) + (1 error bar)."""
    return fr + fr_err

def calc_fakerate_down(fr, fr_err):
    """Return the value: (fake rate) - (1 error bar)."""
    return fr - fr_err
    
def retrieve_FR_hists(infile):
    """Return a 4-tuple of fake rate TH1's."""
    # Get fake rate hists.
    f = rt.TFile(infile, "read")
    print("Retrieving fake rates...")
    h_FRe_bar = f.Get("Data_FRel_EB")
    h_FRe_end = f.Get("Data_FRel_EE")
    h_FRmu_bar = f.Get("Data_FRmu_EB")
    h_FRmu_end = f.Get("Data_FRmu_EE")
    # Let hists survive after their TFile is closed.
    h_FRe_bar.SetDirectory(0)
    h_FRe_end.SetDirectory(0)
    h_FRmu_bar.SetDirectory(0)
    h_FRmu_end.SetDirectory(0)
    f.Close()
    return (h_FRe_bar, h_FRe_end, h_FRmu_bar, h_FRmu_end)

def calc_wgt_3p1f_cr(
    fakelep_id, fakelep_pt, fakelep_eta,
    h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
    eta_bound_elec=1.497, eta_bound_muon=1.2,
    verbose=False,
    ):
    """Return the weighted contribution of this fake lepton to 3P1F CR.

    Args:
        fakelep_id (int): Lepton's PDG ID.
        fakelep_pt (float): Lepton's transverse momentum (GeV).
        fakelep_eta (float): Lepton's pseudorapidity.

    NOTE:
        * Specifically returns the quantity: f / (1-f)
            where f = fake rate of this lepton.
            Fake rate depends on lepton's pT and eta.
        * Only works for DATA right now.
            To work for ZZ, must account for previous event weight.
    """
    fr, fr_err = get_fakerate_and_error(
        lep_id=fakelep_id,
        lep_pt=fakelep_pt,
        lep_eta=fakelep_eta,
        h1D_FRel_EB=h1D_FRel_EB,
        h1D_FRel_EE=h1D_FRel_EE,
        h1D_FRmu_EB=h1D_FRmu_EB,
        h1D_FRmu_EE=h1D_FRmu_EE,
        eta_bound_elec=eta_bound_elec,
        eta_bound_muon=eta_bound_muon,
        verbose=verbose,
        )
    return calc_fr_ratio_3p1f(fr)

def calc_wgt_2p2f_cr(
    fakelep_id1, fakelep_pt1, fakelep_eta1,
    fakelep_id2, fakelep_pt2, fakelep_eta2,
    h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE,
    eta_bound_elec=1.497, eta_bound_muon=1.2,
    verbose=False,
    in_3P1F=False,
    ):
    """Return the weighted contribution of two fake leptons to 2P2F CR.

    Args:
        fakelep_id (int): Lepton's PDG ID.
        fakelep_pt (float): Lepton's transverse momentum (GeV).
        fakelep_eta (float): Lepton's pseudorapidity.

    NOTE:
        Depending on the in_3P1F flag, this function returns different values:
        If in_3P1F=True:
            Returns the total predicted 2P2F weight:
                (f_1 / (1-f_1)) * (f_2 / (1-f_2)),
                where
                f_1 = fake rate of lepton 1 and
                f_2 = fake rate of lepton 2.
                Fake rates depend on leptons' pT and eta.
        If in_3P1F=False:
            Returns the 2P2F pred contribution to the 3P1F region:
            (f_1 / (1-f_1)) + (f_2 / (1-f_2))
        FIXME:
        * Only works for DATA right now.
            To work for ZZ or other MC, must account for event weight.
    """
    fr1, fr1_err = get_fakerate_and_error(
        lep_id=fakelep_id1,
        lep_pt=fakelep_pt1,
        lep_eta=fakelep_eta1,
        h1D_FRel_EB=h1D_FRel_EB,
        h1D_FRel_EE=h1D_FRel_EE,
        h1D_FRmu_EB=h1D_FRmu_EB,
        h1D_FRmu_EE=h1D_FRmu_EE,
        eta_bound_elec=eta_bound_elec,
        eta_bound_muon=eta_bound_muon,
        verbose=verbose,
        )
    fr2, fr2_err = get_fakerate_and_error(
        lep_id=fakelep_id2,
        lep_pt=fakelep_pt2,
        lep_eta=fakelep_eta2,
        h1D_FRel_EB=h1D_FRel_EB,
        h1D_FRel_EE=h1D_FRel_EE,
        h1D_FRmu_EB=h1D_FRmu_EB,
        h1D_FRmu_EE=h1D_FRmu_EE,
        eta_bound_elec=eta_bound_elec,
        eta_bound_muon=eta_bound_muon,
        verbose=verbose,
        )
    if in_3P1F:
        return calc_fr_ratio_2p2f_sum(fr1, fr2)
    else:
        return calc_fr_ratio_2p2f_prod(fr1, fr2)

def calc_fr_ratio_3p1f(fr):
    """Return fr / (1-fr)"""
    return fr / (1-fr)
    
def calc_fr_ratio_2p2f_prod(fr1, fr2):
    """Return (fr1 / (1-fr1)) * (fr2 / (1-fr2))"""
    return (fr1 / (1-fr1)) * (fr2 / (1-fr2))
    
def calc_fr_ratio_2p2f_sum(fr1, fr2):
    """Return (fr1 / (1-fr1)) + (fr2 / (1-fr2)).
    
    This is the contribution of 2P2F to the 3P1F CR.
    """
    return (fr1 / (1-fr1)) + (fr2 / (1-fr2))

def analyzeZX(
    tree, Nickname, outfile_dir, suffix="", overwrite=0, lumi=59700, kinem_ls=[''],
    n_evts_to_process=-1
    ):
    """Analyze each event in sample `Nickname` and create histograms.

    Parameters
    ----------
    tree : ROOT.TTree
        The TTree which holds events in each "row".
        Must have branches corresponding to elements in `kinem_ls`.
    Nickname : str
        The shorthand name of the sample to-be processed.
    lumi : float
        The integrated luminosity of the Data sample.
    kinem_ls : list of str
        The names of the branches for which histograms will be made.
    """
    wgt_from_ntuple = False
    study_particle_origins = True
    # max_events = 1E5 #-1
        
    # Name the outfile and check for overwrite.
    isData = "Data" in Nickname
    filename = f"Hist_Data.root" if isData else f"Hist_MC_{Nickname}.root"
    if len(suffix) > 0:
        filename = filename.replace(".root", f"_{suffix}.root")
    os.makedirs(outfile_dir, exist_ok=True)
    outfile_path = os.path.join(outfile_dir, filename)
    check_overwrite(outfile_path, overwrite=overwrite)

    kinem_info_dct = {
        "mass4l" : {
            "n_bins" : 410,
            "x_label" : r'm_{4#ell}',
            "x_min" : 50,
            "x_max" : 870,
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
    
    if (varName == "mEt"):
        var_plotHigh = 50
        var_plotLow = 0
        var_nBins = 10
        varAxLabel = "E_{T,miss}"
    
    #initiate numerator and denominator histograms for FR computation

    binWidth = ((int) (100*(var_plotHigh - var_plotLow)/var_nBins))/100.
    sUnit = "GeV"
    
    # Make pT hists for non-prompt lepton that passes tight selection.
    # if (varName=="ptl3"):
    #     h1D_dummy = rt.TH1D("dummy", "dummy", len(PtlBins), PtlBins)
    #     setHistProperties(h1D_dummy,1,1,1,0,0,varAxLabel,"Misidentification rate")
        
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

    # else:
    #     # h1D_dummy = rt.TH1D("dummy", "dummy", var_nBins, var_plotLow, var_plotHigh)
    #     # setHistProperties(h1D_dummy,1,1,1,0,0,varAxLabel,"Misidentification rate")

    #     # define FR numerator histograms
    #     h1D_FRel_EB = rt.TH1D("h1D_FRel_EB","h1D_FRel_EB",var_nBins, var_plotLow, var_plotHigh)
    #     h1D_FRel_EE = rt.TH1D("h1D_FRel_EE","h1D_FRel_EE",var_nBins, var_plotLow, var_plotHigh)
    #     h1D_FRmu_EB = rt.TH1D("h1D_FRmu_EB","h1D_FRmu_EB",var_nBins, var_plotLow, var_plotHigh) 
    #     h1D_FRmu_EE = rt.TH1D("h1D_FRmu_EE","h1D_FRmu_EE",var_nBins, var_plotLow, var_plotHigh) 
    
    #     # define FR denominator histograms
    #     h1D_FRel_EB_d = rt.TH1D("h1D_FRel_EB_d","h1D_FRel_EB_d",var_nBins, var_plotLow, var_plotHigh) 
    #     h1D_FRel_EE_d = rt.TH1D("h1D_FRel_EE_d","h1D_FRel_EE_d",var_nBins, var_plotLow, var_plotHigh) 
    #     h1D_FRmu_EB_d = rt.TH1D("h1D_FRmu_EB_d","h1D_FRmu_EB_d",var_nBins, var_plotLow, var_plotHigh) 
    #     h1D_FRmu_EE_d = rt.TH1D("h1D_FRmu_EE_d","h1D_FRmu_EE_d",var_nBins, var_plotLow, var_plotHigh) 

    print("...Making kinematic hists in XPYF control regions.")
    hist_dct = make_hist_dct(kinem_ls, kinem_info_dct)

    # Propagate errors.
    for h in all_FR_hist_ls + list(hist_dct.values()):
        h.Sumw2()

    nentries = tree.GetEntries()
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
    
        if count < barrel_endcap_region.MB_n:  # MB_n = 4
            # Hists 0-3 are dedicated to electrons?
            Hist_conv.append(rt.TH1D("Hist_conv"+order[count] ,"Hist_conv"+order[count], len(PtlBins)-1, PtlBins))
            Hist_conv[count].Sumw2()

            Hist_prompt.append(rt.TH1D("Hist_prompt"+order[count],"Hist_prompt"+order[count], len(PtlBins)-1, PtlBins))
            Hist_prompt[count].Sumw2()

            Hist_fakes.append(rt.TH1D("Hist_fakes"+order[count],"Hist_fakes"+order[count], len(PtlBins)-1, PtlBins))
            Hist_fakes[count].Sumw2()

            Hist_BDfakes.append(rt.TH1D("Hist_BDfakes"+order[count],"Hist_BDfakes"+order[count], len(PtlBins)-1, PtlBins))
            Hist_BDfakes[count].Sumw2()

        elif count >= barrel_endcap_region.MB_n:
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

    n_passedZ1LSelection = 0
    n_passedmZ1window = 0
    n_passedmZ1window_and_MET = 0
    n_electron_barrel = 0
    n_electron_barrel_passtight = 0
    n_electron_endcap = 0
    n_electron_endcap_passtight = 0
    n_muon_barrel = 0
    n_muon_barrel_passtight = 0
    n_muon_endcap = 0
    n_muon_endcap_passtight = 0

    if n_evts_to_process == -1:
        n_evts_to_process = tree.GetEntries()
    # for iEvt, event in enumerate(tree):
    for iEvt in range(n_evts_to_process):

        tree.GetEntry(iEvt)
        
        if (iEvt % 1000000 == 0):
            print (f"Processing event: {iEvt}/{nentries}")
        # if iEvt == max_events:
        #     break
            
        # Get total number of events from MC/Data files.
        # Use the L_int and xs to determine n_expected and event weights.
        # n_dataset_tot = floa[Nickname])
        n_dataset_tot = float(n_sumgenweights_dataset_dct_jake[Nickname])
        weight = get_evt_weight(
                    dct_xs_jake,
                    Nickname,
                    lumi,
                    tree,
                    n_dataset_tot,
                    orig_evt_weight=tree.eventWeight
                    )
    
        #######################################
        #--- CR: Z+L for fake rate studies ---#
        #######################################
        if tree.passedZ1LSelection:
            n_passedZ1LSelection += 1
            # We got some kind of Z+L event.
            # It should only be from Z+jets or Zgamma+jets.
            # However WZ events produce a Z and a prompt lepton.
            # We will remove WZ later.
            # If lep3 passes tight selection, then it's likely a fake
            # (since we are only looking for 3 lep events right now).
            # How frequently does this happen, i.e. what is the fake rate?

            # First, reconstruct Z candidate.
            lep_1, lep_2 = reconstruct_Zcand_leptons(tree)
            lep_3 = rt.TLorentzVector()
            massZ1 = (lep_1 + lep_2).M()


            # Get info about third lepton, which is at least loose.
            ndx_loose = tree.lep_Hindex[2]
            lep_tight = tree.lep_tightId[ndx_loose]
            lep_iso = tree.lep_RelIsoNoFSR[ndx_loose]
            idL3 = tree.lep_id[ndx_loose]
            lep_3.SetPtEtaPhiM(tree.lep_pt[ndx_loose],
                             tree.lep_eta[ndx_loose],
                             tree.lep_phi[ndx_loose],
                             tree.lep_mass[ndx_loose])
            pTL3  = lep_3.Pt()
            etaL3 = lep_3.Eta()
            phiL3 = lep_3.Phi()
            
            lep_id = tree.lep_id
            lep_Hindex = tree.lep_Hindex
            if study_particle_origins:
                lep_matchedR03_PdgId = tree.lep_matchedR03_PdgId
                lep_matchedR03_MomId = tree.lep_matchedR03_MomId
                lep_matchedR03_MomMomId = tree.lep_matchedR03_MomMomId

            TestVar=False
            FillVar=0.
            
            # h1D_Z1L_mZ1.Fill(massZ1, weight)
            # h1D_Z1L_pTL1.Fill(lep_1.Pt(), weight)
            # h1D_Z1L_pTL2.Fill(lep_2.Pt(), weight)
            # h1D_Z1L_pTL3.Fill(lep_3.Pt(), weight)

            tight_mZ_window = math.fabs(massZ1 - MZ_PDG) < 7
            if tight_mZ_window:
                n_passedmZ1window += 1
            #     h1D_Z1L_mZ1_tightmZ.Fill(massZ1, weight)
            #     h1D_Z1L_pTL1_tightmZ.Fill(lep_1.Pt(), weight)
            #     h1D_Z1L_pTL2_tightmZ.Fill(lep_2.Pt(), weight)
            #     h1D_Z1L_pTL3_tightmZ.Fill(lep_3.Pt(), weight)
            low_MET = tree.met < 25

            TestVar = tight_mZ_window and low_MET
            if tight_mZ_window and low_MET:
                n_passedmZ1window_and_MET += 1
            #     h1D_Z1L_mZ1_tightmZ_lowMET.Fill(massZ1, weight)
            #     h1D_Z1L_pTL1_tightmZ_lowMET.Fill(lep_1.Pt(), weight)
            #     h1D_Z1L_pTL2_tightmZ_lowMET.Fill(lep_2.Pt(), weight)
            #     h1D_Z1L_pTL3_tightmZ_lowMET.Fill(lep_3.Pt(), weight)
            FillVar = pTL3

            # Sort lep3 if electron.
            if ((abs(idL3) == 11) and (math.fabs(etaL3) < 1.497) and TestVar):
                h1D_FRel_EB_d.Fill(FillVar, weight)
                if study_particle_origins:
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EB_d], Hist_fakes[barrel_endcap_region.EB_d], Hist_BDfakes[barrel_endcap_region.EB_d], Hist_conv[barrel_endcap_region.EB_d],False)
                # h1D_Z1L_e1_0eta1p497_pT.Fill(lep_1.Pt(), weight)
                # h1D_Z1L_e1_0eta1p497_eta.Fill(lep_1.Eta(), weight)
                # h1D_Z1L_e2_0eta1p497_pT.Fill(lep_2.Pt(), weight)
                # h1D_Z1L_e2_0eta1p497_eta.Fill(lep_2.Eta(), weight)
                # h1D_Z1L_e3_0eta1p497_pT.Fill(lep_3.Pt(), weight)  # This should be identical to h1D_FRel_EB_d.
                # h1D_Z1L_e3_0eta1p497_eta.Fill(lep_3.Eta(), weight)
                n_electron_barrel += 1
                if (lep_tight and TestVar):
                    if study_particle_origins:
                        PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EB_n], Hist_fakes[barrel_endcap_region.EB_n],Hist_BDfakes[barrel_endcap_region.EB_n],Hist_conv[barrel_endcap_region.EB_n],False)
                    h1D_FRel_EB.Fill(FillVar, weight)
                    n_electron_barrel_passtight += 1
                    # h1D_Z1L_e1_0eta1p497_pT.Fill(lep_1.Pt(), weight)
                    # h1D_Z1L_e1_0eta1p497_eta.Fill(lep_1.Eta(), weight)
                    # h1D_Z1L_e2_0eta1p497_pT.Fill(lep_2.Pt(), weight)
                    # h1D_Z1L_e2_0eta1p497_eta.Fill(lep_2.Eta(), weight)
                    # h1D_Z1L_e3_0eta1p497_pT.Fill(lep_3.Pt(), weight)  # This should be identical to h1D_FRel_EB_d.
                    # h1D_Z1L_e3_0eta1p497_eta.Fill(lep_3.Eta(), weight)

            if ((abs(idL3) == 11) and (math.fabs(etaL3) > 1.497) and TestVar):
                h1D_FRel_EE_d.Fill(FillVar, weight)
                if study_particle_origins:
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EE_d], Hist_fakes[barrel_endcap_region.EE_d],Hist_BDfakes[barrel_endcap_region.EE_d], Hist_conv[barrel_endcap_region.EE_d],False)
                n_electron_endcap += 1
                # h1D_Z1L_e1_0eta1p497_pT.Fill(lep_1.Pt(), weight)
                # h1D_Z1L_e1_0eta1p497_eta.Fill(lep_1.Eta(), weight)
                # h1D_Z1L_e2_0eta1p497_pT.Fill(lep_2.Pt(), weight)
                # h1D_Z1L_e2_0eta1p497_eta.Fill(lep_2.Eta(), weight)
                # h1D_Z1L_e3_0eta1p497_pT.Fill(lep_3.Pt(), weight)  # This should be identical to h1D_FRel_EB_d.
                # h1D_Z1L_e3_0eta1p497_eta.Fill(lep_3.Eta(), weight)
                
                if lep_tight and TestVar:
                    if study_particle_origins:
                        PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.EE_n], Hist_fakes[barrel_endcap_region.EE_n], Hist_BDfakes[barrel_endcap_region.EE_n], Hist_conv[barrel_endcap_region.EE_n],False)
                    h1D_FRel_EE.Fill(FillVar, weight)
                    n_electron_endcap_passtight += 1 

            # Sort lep3 if muon.
            if ((abs(idL3) == 13) and (math.fabs(etaL3) < 1.2) and TestVar):
                h1D_FRmu_EB_d.Fill(FillVar, weight)
                if study_particle_origins:
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.MB_d], Hist_fakes[barrel_endcap_region.MB_d], Hist_BDfakes[barrel_endcap_region.MB_d], Hist_conv[barrel_endcap_region.MB_d],False)
                n_muon_barrel += 1
                
                if (lep_tight and (lep_iso < 0.35) and TestVar):
                    if study_particle_origins:
                        PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.MB_n], Hist_fakes[barrel_endcap_region.MB_n],Hist_BDfakes[barrel_endcap_region.MB_n], Hist_conv[barrel_endcap_region.MB_n],False)
                    h1D_FRmu_EB.Fill(FillVar, weight)
                    n_muon_barrel_passtight += 1

            if ((abs(idL3) == 13) and (math.fabs(etaL3) > 1.2) and TestVar):
                h1D_FRmu_EE_d.Fill(FillVar, weight)
                if study_particle_origins:
                    PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.ME_d], Hist_fakes[barrel_endcap_region.ME_d],Hist_BDfakes[barrel_endcap_region.ME_d], Hist_conv[barrel_endcap_region.ME_d],False)
                n_muon_endcap += 1
                
                if (lep_tight and (lep_iso < 0.35) and TestVar):
                    #PartOrigin(lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[ME_n], Hist_fakes[ME_n],Hist_BDfakes[ME_n], Hist_conv[ME_n],false)
                    if study_particle_origins:
                        PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId,lep_Hindex,lep_id, FillVar,weight,Hist_prompt[barrel_endcap_region.ME_n], Hist_fakes[barrel_endcap_region.ME_n],Hist_BDfakes[barrel_endcap_region.ME_n], Hist_conv[barrel_endcap_region.ME_n],False)
                    h1D_FRmu_EE.Fill(FillVar, weight)
                    n_muon_endcap_passtight += 1

        #########################
        #--- CR: Z+LL (XPYF) ---#
        #########################
        elif tree.passedZXCRSelection:
            # Collect info about 4 leps from "H candidate".
            # We got at least 1 fake lepton.
            lep_tight = []
            lep_iso = []
            idL = []
            for k in range(4):
                lep_tight.append(tree.lep_tightId[tree.lep_Hindex[k]])
                lep_iso.append(tree.lep_RelIsoNoFSR[tree.lep_Hindex[k]])
                idL.append(tree.lep_id[tree.lep_Hindex[k]])

            #--- Not yet implemented. ---#
            # lep_3.SetPtEtaPhiM(tree.lep_pt[tree.lep_Hindex[2]], tree.lep_eta[tree.lep_Hindex[2]], tree.lep_phi[tree.lep_Hindex[2]], tree.lep_mass[tree.lep_Hindex[2]])
            # pTL3  = lep_3.Pt()
            # etaL3 = lep_3.Eta()
            # phiL3 = lep_3.Phi()

            # lep_4.SetPtEtaPhiM(tree.lep_pt[tree.lep_Hindex[3]], tree.lep_eta[tree.lep_Hindex[3]], tree.lep_phi[tree.lep_Hindex[3]], tree.lep_mass[tree.lep_Hindex[3]])
            # pTL4  = lep_4.Pt()
            # etaL4 = lep_4.Eta()
            # phiL4 = lep_4.Phi()
            # DR = math.sqrt((phiL3-phiL4)*(phiL3-phiL4) + (etaL3-etaL4)*(etaL3-etaL4))
            
            lep_1, lep_2 = reconstruct_Zcand_leptons(tree)
            massZ1 = (lep_1+lep_2).M()

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
                event=tree, weight=weight, hist_dct=hist_dct,
                kinem_ls=kinem_ls, control_reg=conreg,
                finalstate_4L=finalstate_4L, finalstate_2L=finalstate_2L)
                
    def print_cutflow_numbers(n_passedZ1LSelection,
                              n_passedmZ1window,
                              n_passedmZ1window_and_MET,
                              n_electron_barrel,
                              n_electron_barrel_passtight,
                              n_electron_endcap,
                              n_electron_endcap_passtight,
                              n_muon_barrel,
                              n_muon_barrel_passtight,
                              n_muon_endcap,
                              n_muon_endcap_passtight):
        lost_to_mz1 = n_passedZ1LSelection - n_passedmZ1window
        lost_to_MET = n_passedmZ1window - n_passedmZ1window_and_MET

        tot_events_left = (n_electron_barrel +
                         n_electron_endcap +
                         n_muon_barrel +
                         n_muon_endcap)
        tot_pass = (n_electron_barrel_passtight +
                         n_electron_endcap_passtight +
                         n_muon_barrel_passtight +
                         n_muon_endcap_passtight)
        tot_fail = tot_events_left - tot_pass

        print(
            f"Total number of events in Z+L CR,              {n_passedZ1LSelection}\n"
            f"Events lost after abs(Z1 - Z_PDG) < 7 GeV cut, {lost_to_mz1}\n"
            f"Events lost after MET < 25 GeV cut,            {lost_to_MET}\n"
            f"Total events left,                             {n_passedmZ1window_and_MET}\n"
            f"Passing selection,                             {tot_pass}\n"
            f"Failing selection,                             {tot_fail}\n"
            )

        # print(
        #     f"###################"
        #     f"#--- ELECTRONS ---#"
        #     f"###################"
        #     f"{'Passing,':>15}{'Failing,':>15}{'Total'}\n"
        #     f"{}"
        #     )
        print(f"n_electron_barrel,           {n_electron_barrel}")
        print(f"n_electron_barrel_passtight, {n_electron_barrel_passtight}")
        print(f"n_electron_endcap,           {n_electron_endcap}")
        print(f"n_electron_endcap_passtight, {n_electron_endcap_passtight}")
        print(f"n_muon_barrel,               {n_muon_barrel}")
        print(f"n_muon_barrel_passtight,     {n_muon_barrel_passtight}")
        print(f"n_muon_endcap,               {n_muon_endcap}")
        print(f"n_muon_endcap_passtight      {n_muon_endcap_passtight}")

        n_passedZ1LSelection_elisa = 4777075
        lost_to_mz1_elisa = 1218668
        lost_to_MET_elisa = 1520725
        n_passedmZ1window_and_MET_elisa = 948392
        tot_pass_elisa = 45971
        tot_fail_elisa = 902421

        tot_events_left_elisa = tot_pass_elisa + tot_fail_elisa
        tot_events_left_elisa_closetojake = 3235323
        print("#--- PRINTING ELISA'S NUMBERS ---#")
        print(
            f"Total number of events in Z+L CR,              {n_passedZ1LSelection_elisa}\n"
            f"Events lost after abs(Z1 - Z_PDG) < 7 GeV cut, {lost_to_mz1_elisa}\n"
            f"Events lost after MET < 25 GeV cut,            {lost_to_MET_elisa}\n"
            f"Total events left,                             {n_passedmZ1window_and_MET_elisa}\n"
            f"Passing selection,                             {tot_pass_elisa}\n"
            f"Failing selection,                             {tot_fail_elisa}\n"
            )

    print_cutflow_numbers(n_passedZ1LSelection,
                              n_passedmZ1window,
                              n_passedmZ1window_and_MET,
                            n_electron_barrel,
                            n_electron_barrel_passtight,
                            n_electron_endcap,
                            n_electron_endcap_passtight,
                            n_muon_barrel,
                            n_muon_barrel_passtight,
                            n_muon_endcap,
                            n_muon_endcap_passtight)

    # Save the plots.
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
    
    print(
        f"...Storing kinematic histograms in root file:\n"
        f"{outfile_path}"
        )
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