from ROOT import TFile
from analyzeZX import analyzeZX

var_bin_dct = {
    "ptl3" : [],
    "m4l" : [],
}

filename_dct = {
    # Nickname : filepath
    "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
    "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v2_smallerstats.root",
    "WZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_smallerstats.root"
}

#fileList = ["../Data_skimmed.root",
#            "../DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_2018filter2l_new_ZX.root",
#            "../TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new_ZX.root",
#            "../WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_2018_filter2l_new_ZX.root",
#            "../ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new_ZX.root"
#            ]

print("First stage of processing (FR computation and CR histogram creation) has been initiated.\n")

for name, filepath in filename_dct.items():
    inFile =  ROOT.TFile.Open(filepath, "READ")
    tree = inFile.Get("Ana/passedEvents")
    n_evts = tree.GetEntries()
    print(f"File: {filepath} has been opened.")
    print(f"-- Nickname: {name}")
    print(f"-- Found {n_evts} events.")
    analyzeZX(tree, name)
    inFile.Close()