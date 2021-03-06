import os
from ROOT import TFile
from helpers.analyzeZX import analyzeZX
from constants.analysis_params import (
    LUMI_INT_2018_Jake, n_sumgenweights_dataset_dct_jake
    )
from sidequests.data.filepaths import (
    mc_2017_UL_ZZ, mc_2017_UL_WZ,
    data_2017_UL
    )

# outdir_rootfile = "/blue/avery/rosedj1/ZplusXpython/data/20211017_new2018data"
outdir_rootfile = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/test"
suffix = "test01"  # Underscore gets auto prefixed.
overwrite = 1
n_evts_to_process = 100000

lumi = LUMI_INT_2018_Jake

# dir_data = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/noduplicates/"
# dir_data = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2018/fullstats/TRASH/"
dir_data = os.path.dirname(data_2017_UL)
# dir_mc   = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/MC/2018/fullstats/skimmedbranches/veryfewbranches/"
dir_mc = os.path.dirname(mc_2017_UL_ZZ)

filename_dct = {
    #--- Nickname : filepath ---#
    # "Data"       : os.path.join(dir_data, "Data2018_NoDuplicates.root"),  # n_evts_tot = 3,485,358
    # "DY50"       : os.path.join(dir_mc, "DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root"),
    # "TT"         : os.path.join(dir_mc, "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root"),
    # "WZ-ext1-v2" : os.path.join(dir_mc, "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root"),
    # "ZZ"         : os.path.join(dir_mc, "ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018_veryfewbranches.root"),

    "WZ"         : mc_2017_UL_WZ,

    # "Data" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_CR/Data_2018_NoDuplicates_vxbs.root",  # n_evts_tot = 3,404,111 --- OLD.
    # "DY50" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root",  # n_evts_tot = 2,647,699
    # ### "WZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15-v1_2018.root",  # n_evts_tot = 819,364
    # "WZ-ext1-v2" : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root",
    # ### "WZ_vukasin"   : "/blue/avery/rosedj1/ZplusXpython/data/vukasin/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_2018_filter2l_new_ZX.root",
    # "ZZ"   : "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root",  # n_evts_tot = 7,287,720
}

kinem_ls = [
    "mass4l", "mass4lREFIT", "mass4lREFIT_vtx_BS",
    # "mass4lErr", "mass4lErrREFIT", "mass4lErrREFIT_vtx_BS",
    # "met", "D_bkg_kin", "D_bkg_kin_vtx_BS"
    ]

print("First stage of processing (FR computation and CR histogram creation) has been initiated.\n")

print("!!! USING WRONG LUMI_INT !!!")

for name, filepath in filename_dct.items():
    inFile = TFile.Open(filepath, "READ")
    try:
        tree = inFile.Get("Ana/passedEvents")
        n_evts = tree.GetEntries()
    except (AttributeError, ReferenceError):
        # Probably the wrong path to TTree.
        tree = inFile.Get("passedEvents")
        n_evts = tree.GetEntries()
    print(
        f"File: {filepath} has been opened.\n"
        f"-- Nickname: {name}\n"
        f"-- Found {n_evts} events."
        )
    if "Data" not in name:
        print(
            f"-- MC file has sumGenWeights="
            f"{n_sumgenweights_dataset_dct_jake[name]}."
            )
    analyzeZX(tree=tree, Nickname=name, outfile_dir=outdir_rootfile, suffix=suffix,
               overwrite=overwrite, lumi=lumi, kinem_ls=kinem_ls,
               n_evts_to_process=n_evts_to_process)
    inFile.Close()