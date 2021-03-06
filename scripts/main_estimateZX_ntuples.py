import ROOT
from scripts.helpers.estimateZX import estimateZX
from constants.analysis_params import LUMI_INT_2018_Jake
from sidequests.data.filepaths import fakerates_WZremoved

# outfile_dir = "/blue/avery/rosedj1/ZplusXpython/data/controlreg_OS/20210802"
outfile_dir = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/test"
suffix = ""
overwrite = 0

# file_WZremoved = "Hist_Data_ptl3_WZremoved.root"
file_fakerates_WZremoved = fakerates_WZremoved

filename_dct = {
    # "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_CR/Data_2018_NoDuplicates_vxbs.root",  # n_evts_tot = 3,404,111
    # "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root",
    "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2018/fullstats/TRASH/MuonEG_skimmed_test.root",
    "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/MC/2018/fullstats/skimmedbranches/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018_veryfewbranches.root",
}

print("\nSecond stage of processing (Creation of ZX SR contributions for Data and ZZ.\n")

for name, filepath in filename_dct.items():
    inFile =  ROOT.TFile.Open(filepath, "READ")
    tree = inFile.Get("passedEvents")
    n_evts = tree.GetEntries()
    print(
        f"Successfully opened file:\n"
        f"-- {filepath}\n"
        f"-- Nickname: {name}"
        f"-- Found {n_evts} events in TTree."
    )
    estimateZX(FakeRateFile=file_fakerates_WZremoved, tree=tree,
               Nickname=name, outfile_dir=outfile_dir, suffix=suffix,
               overwrite=overwrite, lumi=LUMI_INT_2018_Jake)
    inFile.Close()