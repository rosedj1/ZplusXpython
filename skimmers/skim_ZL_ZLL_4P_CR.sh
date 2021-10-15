#!/bin/bash
##############################################################################
# PURPOSE: Apply the RedBkg skimmer to multiple root files.
#          Send jobs to background.
# SYNTAX:  ./<this_script>.sh
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-05-21
# UPDATED: 2021-10-14
##############################################################################
infile_dir="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats"
outfile_dir="${infile_dir}/ZL_ZLL_4P_CR"

input_rootfiles=( )
# input_rootfiles+=( "MuonEG.root" )
input_rootfiles+=( "SingleMuon.root" )
input_rootfiles+=( "DoubleMuon.root" )
input_rootfiles+=( "EGamma.root" )
# Arguments for C++ code:
#   TString infile,
#   TString outfile,
#   bool isData = true,
#   bool do_Z1LSelection = true,
#   bool do_ZXCRSelection = true,
#   bool do_4PSelection = true
cd /blue/avery/rosedj1/ZplusXpython/skimmers/
for f in "${input_rootfiles[@]}"; do
    infile="${infile_dir}/${f}"
    outfile_name=${f/.root/_Duplicates.root}
    outfile="${outfile_dir}/${outfile_name}"
    root -l -b -q apply_redbkg_evt_selection_vxbs.C\(\"${infile}\",\"${outfile}\",1,1,1,1\) > "${outfile/root/out}" &
done