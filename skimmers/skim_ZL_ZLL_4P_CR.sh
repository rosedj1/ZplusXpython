#!/bin/bash
##############################################################################
# PURPOSE: Apply a skimmer to various MC root files.
# SYNTAX:  ./<this_script>.sh
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-05-21
# UPDATED: 2021-08-31
##############################################################################

infile_data="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/noduplicates/Data_2018_NoDuplicates.root"
# outfile_data="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_4P_CR/Data_2018_NoDuplicates.root"
infile_mc_DY="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root"
outfile_mc_DY="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root"
infile_mc_TT="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root"
outfile_mc_TT="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root"
infile_mc_WZ="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root"
outfile_mc_WZ="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root"
infile_mc_ZZ="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root"
# outfile_mc_ZZ="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root"

outfile_data="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZLL_CR/Data_2018_NoDuplicates.root"
outfile_mc_ZZ="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZLL_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root"

# Arguments for C++ code:
#   TString infile,
#   TString outfile,
#   bool isData = true,
#   bool do_Z1LSelection = true,
#   bool do_ZXCRSelection = true,
#   bool do_4PSelection = true
# root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_data}\",\"${outfile_data}\",1\)   > output_data.txt &
# root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_mc_DY}\",\"${outfile_mc_DY}\",0\) > output_DY.txt &
# root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_mc_TT}\",\"${outfile_mc_TT}\",0\) > output_TT.txt &
# root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_mc_WZ}\",\"${outfile_mc_WZ}\",0\) > output_WZ.txt &
# root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_mc_ZZ}\",\"${outfile_mc_ZZ}\",0\) > output_ZZ.txt &

root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_data}\",\"${outfile_data}\",1,0,1,0\) > output_data.txt &
root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile_mc_ZZ}\",\"${outfile_mc_ZZ}\",0,0,1,0\) > output_zz.txt &