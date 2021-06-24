from ROOT import TFile
from helpers.analyzeZX import analyzeZX
from constants.physics import LUMI_INT_2018_Jake

filename_dct = {
    #--- Nickname : filepath ---#
    # Smaller stats for testing.
    # "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
    # "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext2-v2_smallerstats.root",
    # "WZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_smallerstats.root"

    # Full stats.
    # "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/Data_2018.root",  # n_evts_tot = 170,727,138
    # "DY50" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root",  # n_evts_tot = 187,531,221
    # "TT"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root",  # n_evts_tot = 63,550,000
    # "WZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root",  # n_evts_tot = 17,442,902
    # "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root",  # n_evts_tot = 96,635,000
    # "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_CR/Data_2018.root",  # n_evts_tot = 5,433,670

    # No Duplicates.
    "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_CR/Data_2018_NoDuplicates_vxbs.root",  # n_evts_tot = 3,404,111
    "DY50" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root",  # n_evts_tot = 2,647,699
    "TT"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root",  # n_evts_tot = 1,340,262
    "WZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root",  # n_evts_tot = 819,364
    "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root",  # n_evts_tot = 7,287,720
}

kinem_ls = [
    "mass4l", "mass4lREFIT", "mass4lREFIT_vtx_BS",
    "mass4lErr", "mass4lErrREFIT", "mass4lErrREFIT_vtx_BS",
    "met", "D_bkg_kin", "D_bkg_kin_vtx_BS"
    ]

print("First stage of processing (FR computation and CR histogram creation) has been initiated.\n")

for name, filepath in filename_dct.items():
    inFile =  TFile.Open(filepath, "READ")
    try:
        tree = inFile.Get("Ana/passedEvents")
        n_evts = tree.GetEntries()
    except AttributeError:
        tree = inFile.Get("passedEvents")
        n_evts = tree.GetEntries()
    print(f"File: {filepath} has been opened.")
    print(f"-- Nickname: {name}")
    print(f"-- Found {n_evts} events.")
    analyzeZX(tree, name, lumi=LUMI_INT_2018_Jake)
    inFile.Close()