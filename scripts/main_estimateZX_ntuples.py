import ROOT

from estimateZX import estimateZX

file_WZremoved = "Hist_Data_ptl3_WZremoved.root"

filename_dct = {
    "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
    "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v2_smallerstats.root"
}

# fileList = [
#     "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
#     "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v2_smallerstats.root"
#     ]

# RootNickNames = ["Data", "ZZ"]

print("Second stage of processing (Creation of ZX SR contributions for Data and ZZ.\n")

for name, filepath in filename_dct.items():
    inFile =  ROOT.TFile.Open(filepath, "READ")
    tree = inFile.Get("Ana/passedEvents")
    n_evts = tree.GetEntries()
    print(f"File: {filepath} has been opened.")
    print(f"-- Nickname: {name}")
    print(f"-- Found {n_evts} events.")
    estimateZX(file_WZremoved, tree, name)
    inFile.Close()