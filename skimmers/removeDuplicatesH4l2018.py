"""
NOTE:
* This is the modified version of David's script.
* The 2017 version has not been updated like this one has.
* This code can skim individual data set types (e.g., only MuonEG).

HLT paths taken from the TWiki:
https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsZZ4lRunIILegacy#2018_AN1

diEle: = "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v*","HLT_DoubleEle25_CaloIdL_MW_v*"

diMu: = "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v*"

MuEle: = "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v*","HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v*","HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v*","HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v*","HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ_v*","HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ_v*",

triEle: = "" #One triple electron trigger that exists is prescaled

triMu: = "HLT_TripleMu_10_5_5_DZ_v*","HLT_TripleMu_12_10_5_v*"

SingleEle: = "HLT_Ele32_WPTight_Gsf_v*"

SingleMu: = "HLT_IsoMu24_v*" 

To avoid duplicate events from different primary datasets, events should be taken:

    from DoubleEG if they pass the diEle or triEle triggers,
    from DoubleMuon if they pass the diMuon or triMuon triggers and fail the diEle and triEle triggers,
    from MuEG if they pass the MuEle or MuDiEle or DiMuEle triggers and fail the diEle, triEle, diMuon and triMuon triggers,
    from SingleElectron if they pass the SingleEle trigger and fail all the above triggers,
    from SingleMuon if they pass the SingleMu trigger and fail all the above triggers.
"""
from ROOT import TFile
import os

# def passed_trigger(tree, hlt_paths):
#     """Return True if any HLT path is found in the trigger list."""
#     return any(path in str(tree.triggersPassed) for path in hlt_paths)

# indir_path = "/cms/data/store/user/t2/users/dsperka/Run2/HZZ4l/SubmitArea_13TeV/rootfiles_Data80X_hzz4lskim_M17_Feb21/"
# indir_path = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats"
indir_path = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats"
file_suffix = "_2018"

process_DoubleMu = 0
process_EG = 0
process_MuonEG = 1
process_SingleMuon = 0

def print_perc_dup(data_name, nentries_nodup, nentries):
    frac_nodup = nentries_nodup / float(nentries)
    perc_dup = (1 - frac_nodup) * 100.0
    print(f'{data_name}:')
    print(f'  {nentries_nodup} events kept.')
    print(f'  ({perc_dup:.2f}% were duplicates)\n')

def removeDuplicatesH4l(dirData):

    # hadd A-D of a single data set together first.
    # era = "Run2018-17Sep2018_hzz4l"
    
    input_file_doublemu = os.path.join(dirData, f"DoubleMuon{file_suffix}.root")
    f_DoubleMu = TFile(input_file_doublemu, "READ")
    t_DoubleMu = f_DoubleMu.Get("Ana/passedEvents")

    input_file_muonEG = os.path.join(dirData, f"MuonEG{file_suffix}.root")
    f_MuonEG = TFile(input_file_muonEG, "READ")
    t_MuonEG = f_MuonEG.Get("Ana/passedEvents")

    input_file_EG = os.path.join(dirData, f"EGamma{file_suffix}.root")
    f_EG = TFile(input_file_EG, "READ")
    t_EG = f_EG.Get("Ana/passedEvents")

    input_file_singlemu = os.path.join(dirData, f"SingleMuon{file_suffix}.root")
    f_SingleMuon = TFile(input_file_singlemu, "READ")
    t_SingleMuon = f_SingleMuon.Get("Ana/passedEvents")

    diEle = [
        "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v",
        "HLT_DoubleEle25_CaloIdL_MW_v"
        ]

    diMu = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v"]

    MuEle = [
        "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v",
        "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v",
        "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v",
        "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v",
        "HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ_v",
        "HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ_v"
        ]

    # We don't use this one here, but it's here for completion.
    # triEle = "" #One triple electron trigger that exists is prescaled

    triMu = [
        "HLT_TripleMu_10_5_5_DZ_v",
        "HLT_TripleMu_12_10_5_v"
        ]

    SingleEle = ["HLT_Ele32_WPTight_Gsf_v"]

    SingleMu = ["HLT_IsoMu24_v"]

    n_tot = 0
    n_tot_nodup = 0
    ##################
    #--- DoubleMu ---#
    ##################
    if process_DoubleMu:
        f_new_DoubleMu = TFile(input_file_doublemu.replace(".root", "_NoDuplicates.root"), "recreate")
        t_new_DoubleMu = t_DoubleMu.CloneTree(0)

        nentries = t_DoubleMu.GetEntries()
        n_tot += nentries
        nentries_nodup = 0
        for i in range(nentries):        
            # Grab DoubleMuon events if they pass the diMuon or triMuon triggers
            # and fail the diEle and triEle triggers,
            if (i%10000==0): print(i,"/",nentries,'DoubleMu')
            t_DoubleMu.GetEntry(i)

            event_triggers = str(t_DoubleMu.triggersPassed)
            passed_badtrig = any(path in event_triggers for path in diEle)
            if passed_badtrig:
                # We don't want this.
                continue
            passed_goodtrig = any(path in event_triggers for path in diMu + triMu)
            if passed_goodtrig:
                t_new_DoubleMu.Fill()
                nentries_nodup += 1
                n_tot_nodup += 1

        t_new_DoubleMu.AutoSave()
        del f_new_DoubleMu
        print_perc_dup('DoubleMu', nentries_nodup, nentries)
    
    ############
    #--- EG ---#
    ############
    if process_EG:
        f_new_EG = TFile(input_file_EG.replace(".root", "_NoDuplicates.root"), "recreate")
        t_new_EG = t_EG.CloneTree(0)

        nentries = t_EG.GetEntries()
        n_tot += nentries
        nentries_nodup = 0
        bad_triggers = diMu + triMu
        for i in range(nentries):
            # Grab events from MuEG if they pass the SingleEle or diEle
            # triggers and fail the diMuon and triMuon triggers.
            if (i%10000==0): print(i,"/",nentries,'EG')
            t_EG.GetEntry(i)

            event_triggers = str(t_EG.triggersPassed)
            passed_badtrig = any(path in event_triggers for path in bad_triggers)
            if passed_badtrig:
                # We don't want this.
                continue
            passed_goodtrig = any(path in event_triggers for path in SingleEle + diEle)
            if passed_goodtrig:
                t_new_EG.Fill()
                nentries_nodup += 1
                n_tot_nodup += 1

        t_new_EG.AutoSave()
        del f_new_EG
        print_perc_dup('EGamma', nentries_nodup, nentries)

    ################
    #--- MuonEG ---#
    ################
    if process_MuonEG:
        f_new_MuonEG = TFile(input_file_muonEG.replace(".root", "_NoDuplicates.root"), "recreate")
        t_new_MuonEG = t_MuonEG.CloneTree(0)

        nentries = t_MuonEG.GetEntries()
        n_tot += nentries
        nentries_nodup = 0
        bad_triggers = diEle + diMu + triMu
        for i in range(nentries):
            # Grab events from MuEG if they pass the MuEle or MuDiEle or DiMuEle
            # triggers and fail the diEle, triEle, diMuon and triMuon triggers.
            if (i%10000==0): print(i,"/",nentries,'MuonEG')
            t_MuonEG.GetEntry(i)        

            event_triggers = str(t_MuonEG.triggersPassed)
            passed_badtrig = any(path in event_triggers for path in bad_triggers)
            if passed_badtrig:
                # We don't want this.
                continue
            passed_goodtrig = any(path in event_triggers for path in MuEle)
            if passed_goodtrig:
                t_new_MuonEG.Fill()
                nentries_nodup += 1
                n_tot_nodup += 1

        t_new_MuonEG.AutoSave()
        del f_new_MuonEG
        print_perc_dup('MuonEG', nentries_nodup, nentries)

    ####################
    #--- SingleMuon ---#
    ####################
    if process_SingleMuon:
        f_new_SingleMuon = TFile(input_file_singlemu.replace(".root", "_NoDuplicates.root"), "recreate")
        t_new_SingleMuon = t_SingleMuon.CloneTree(0)

        nentries = t_SingleMuon.GetEntries()
        n_tot += nentries
        nentries_nodup = 0
        bad_triggers = diEle + diMu + MuEle + triMu + SingleEle
        for i in range(nentries):
            # Keep events from SingleMuon if they pass the SingleMu trigger and
            # fail all the above triggers.
            if (i%10000==0): print(i,"/",nentries,'SingleMuon')
            t_SingleMuon.GetEntry(i)        

            event_triggers = str(t_SingleMuon.triggersPassed)
            passed_badtrig = any(path in event_triggers for path in bad_triggers)
            if passed_badtrig:
                # We don't want this.
                continue
            passed_goodtrig = any(path in event_triggers for path in SingleMu)
            if passed_goodtrig:
                t_new_SingleMuon.Fill()
                nentries_nodup += 1
                n_tot_nodup += 1

        t_new_SingleMuon.AutoSave()
        del f_new_SingleMuon
        print_perc_dup('SingleMu', nentries_nodup, nentries)
        print_perc_dup('DoubleMu + MuonEG + EG + SingleMuon', n_tot_nodup, n_tot)

removeDuplicatesH4l(indir_path)