import ROOT
from helpers.estimateZX import estimateZX

# file_WZremoved = "Hist_Data_ptl3_WZremoved.root"
file_fakerates_WZremoved = "../data/Hist_Data_ptl3_Data_WZremoved.root"

filename_dct = {
    # "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
    # "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v2_smallerstats.root"
    "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_CRs/Data_2018.root",
    "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root"
}

# fileList = [
#     "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
#     "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v2_smallerstats.root"
#     ]

# RootNickNames = ["Data", "ZZ"]

print("Second stage of processing (Creation of ZX SR contributions for Data and ZZ.\n")

for name, filepath in filename_dct.items():
    inFile =  ROOT.TFile.Open(filepath, "READ")
    tree = inFile.Get("passedEvents")
    n_evts = tree.GetEntries()
    print(f"Successfully opened file:\n  {filepath}")
    print(f"-- Nickname: {name}")
    print(f"-- Found {n_evts} events.")
    estimateZX(file_fakerates_WZremoved, tree, name)
    inFile.Close()