"""Create new root file with copy of old TTree plus a few more branches.

New branches added:
- is2P2F : int
- is3P1F : int
- is3P1F_zz : int
- weight_fr : float
    For 3P1F: event.eventWeight * (fr / (1-fr))
    For 2P2F: event.eventWeight * (fr2 / (1-fr2)) * (fr3 / (1-fr3))
"""
import ROOT as rt
import os
from array import array
import numpy as np
import argparse
# Local modules.
from estimateZX import getFR
from analyzeZX import setNEvents
from Utils_Python.Utils_Files import check_overwrite

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--infile',            type=str, dest="infile", help="input root file")
parser.add_argument('-r', '--infile_fakerate',   type=str, dest="infile_fr", help="input root file")
parser.add_argument('-o', '--outfile',           type=str, dest="outfile", help="output rootfile")
parser.add_argument('-n', '--nickname',           type=str, dest="name", help="nickname of file/process")
parser.add_argument('-x', '--overwrite',         dest="overwrite", action="store_true", help="overwrite output file (1) or not (0)")
args = parser.parse_args()

# infile_data = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZLL_CR/Data_2018_NoDuplicates.root"
# infile_zz = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZLL_CR/Data_2018_NoDuplicates.root"
# infile_FR_wz_removed = "/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/nolepFSRtocalc_mZ1/Hist_Data_ptl3_WZremoved.root"
infile = args.infile
infile_FR_wz_removed = args.infile_fr
new_rootfile = args.outfile
overwrite = args.overwrite
name = args.name

is_zz = True if name in "ZZ" else False
os.makedirs(os.path.dirname(new_rootfile), exist_ok=True)

f = rt.TFile(infile)
t = f.Get("passedEvents")
print(f"Successfully opened infile:\n  {infile}")

def get_evt_weight(evt, is_zz, LUMI_INT=57750):
    """Return the event weight for MC based on Data collected.

    Generally:
    new_weight = old_weight * (xs * L_int / N_events_from_MC)
    
    """
    if name in "Data":
        # FIXME: In the future, use eventWeight?
        return 1
    wt = evt.eventWeight
    sum_weights = setNEvents(name)
    if is_zz:
        return wt * (1.256 * LUMI_INT) * evt.k_qqZZ_qcd_M * evt.k_qqZZ_ewk / sum_weights
    # if (name == "DY10"):
    #     return wt * 18610.0 * LUMI_INT/sum_weights
    # if (name == "DY50"):
    #     return wt * 6077.22 * LUMI_INT/sum_weights
    # if (name == "TT"):
    #     return wt * 87.31 * LUMI_INT/sum_weights
    # if (name == "WZ"):
    #     return wt * 4.42965 * LUMI_INT/sum_weights

def check_which_Z2_leps_failed(lep_tight, idL, lep_iso):
    """Return code telling which leptons from Z2 failed tight, iso selection.

    Parameters
    ----------
    lep_tight : list
    id_L : list
    lep_iso : list
    
    Returns
    -------
    0, if neither lep from Z2 failed.
    3 if first lep from Z2 failed.
    3, if second lep from Z2 failed.
    5, if both leps from Z2 failed.
    """
    # See if leps 3 and 4 failed.
    lep3_failed = not(lep_tight[2] and ((abs(idL[2])==11) or (abs(idL[2])==13 and lep_iso[2]<0.35)))
    lep4_failed = not(lep_tight[3] and ((abs(idL[3])==11) or (abs(idL[3])==13 and lep_iso[3]<0.35)))
    if lep3_failed and (not lep4_failed):
        return 2
    elif (not lep3_failed) and lep4_failed:
        return 3
    elif lep3_failed and lep4_failed:
        return 5
    else:
        return 0

# Get fake rate hists.
file_FR = rt.TFile(infile_FR_wz_removed)
print("Retrieving fake rates...")
h1D_FRel_EB = file_FR.Get("Data_FRel_EB")
h1D_FRel_EE = file_FR.Get("Data_FRel_EE")
h1D_FRmu_EB = file_FR.Get("Data_FRmu_EB")
h1D_FRmu_EE = file_FR.Get("Data_FRmu_EE")

# You must open/create your file before playing with the TTree.
check_overwrite(new_rootfile, overwrite=overwrite)
newfile = rt.TFile(new_rootfile, "recreate")

print("Cloning TTree...")
newtree = t.CloneTree(0)
# Make a pointer to store values. 
ptr_is2P2F = np.array([0], dtype=int)
ptr_is3P1F = np.array([0], dtype=int)
ptr_is3P1F_zz = np.array([0], dtype=int)
ptr_weight_fr = array('f', [0.])  # Use 'f' for floats, 'd':doubles, 'i':ints. 
ptr_fr2 = array('f', [0.])  # Use 'f' for floats, 'd':doubles, 'i':ints. 
ptr_fr3 = array('f', [0.])  # Use 'f' for floats, 'd':doubles, 'i':ints. 
# Make a branch in the TTree.
newtree.Branch("is2P2F", ptr_is2P2F, "is2P2F/I")
newtree.Branch("is3P1F", ptr_is3P1F, "is3P1F/I")
newtree.Branch("is3P1F_zz", ptr_is3P1F_zz, "is3P1F_zz/I")
newtree.Branch("weight_fr", ptr_weight_fr, "weight_fr/F")
newtree.Branch("fr2", ptr_fr2, "fr2/F")
newtree.Branch("fr3", ptr_fr3, "fr3/F")

# For each event, store new values in new tree.
print("Adding new branches...")
n_tot = t.GetEntries()
for ct, evt in enumerate(t, 1):
    if not evt.passedZXCRSelection: continue
    if (ct % 10000) == 0: print(f"  Event {ct}/{n_tot}")
    # if (ct % 10000) == 0: break
    # Get kinematics of 4 leptons from "Higgs mass candidate".
    lep_tight = []
    lep_iso = []
    idL = []
    pTL = []
    etaL = []
    for k in range(4):
        idL.append( evt.lep_id[evt.lep_Hindex[k]] )
        pTL.append( evt.lep_pt[evt.lep_Hindex[k]] )
        etaL.append( evt.lep_eta[evt.lep_Hindex[k]] )
        lep_tight.append( evt.lep_tightId[evt.lep_Hindex[k]] )
        lep_iso.append( evt.lep_RelIsoNoFSR[evt.lep_Hindex[k]] )
    # See which leptons from Z2 failed.
    n_fail_code = check_which_Z2_leps_failed(lep_tight=lep_tight, idL=idL, lep_iso=lep_iso)
    old_weight = get_evt_weight(evt, is_zz, LUMI_INT=57750)
    # 3P1F.
    if (n_fail_code == 2) or (n_fail_code == 3):
        is2P2F = 0
        is3P1F = 1
        is3P1F_zz = 1 if is_zz else 0
        if n_fail_code == 2:
            fr2 = getFR(
                idL[2], pTL[2], etaL[2],
                h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE
                )
            fr3 = 0
            new_weight = (fr2 / (1-fr2)) * old_weight
        else:
            fr2 = 0
            fr3 = getFR(
                idL[3], pTL[3], etaL[3],
                h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE
                )
            new_weight = (fr3 / (1-fr3)) * old_weight
    # 2P2F.
    elif n_fail_code == 5:  # Both leps failed.
        is2P2F = 1
        is3P1F = 0
        is3P1F_zz = 0
        fr2 = getFR(idL[2], pTL[2], etaL[2], h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE)
        fr3 = getFR(idL[3], pTL[3], etaL[3], h1D_FRel_EB, h1D_FRel_EE, h1D_FRmu_EB, h1D_FRmu_EE)
        new_weight = (fr2 / (1-fr2)) * (fr3 / (1-fr3)) * old_weight
    # Fill branches.
    ptr_is2P2F[0] = is2P2F
    ptr_is3P1F[0] = is3P1F
    ptr_is3P1F_zz[0] = is3P1F_zz
    ptr_weight_fr[0] = new_weight
    ptr_fr2[0] = fr2
    ptr_fr3[0] = fr3
    newtree.Fill()

newtree.Write()