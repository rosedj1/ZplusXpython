#!/bin/bash
#-----------------------------------------------------------------------------
# PURPOSE: Find root files to `hadd` using the `find` command.
# SYNTAX:  ./this_script.sh
# NOTE:
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-10-21
# UPDATED: 
#-----------------------------------------------------------------------------
rootfile_dir="/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/"
outdir="/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/haddedfiles"

files_to_hadd=$( find ${rootfile_dir}/elisa*.root -size +50k )

echo "Files to be hadded:"
echo $files_to_hadd

arr=( $files_to_hadd )
len=${#arr[@]}
echo "Number of files: ${len}"

hadd "${outdir}/elisa_unique_${len}events.root" ${files_to_hadd}