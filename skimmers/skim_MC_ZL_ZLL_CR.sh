#!/bin/bash
##############################################################################
# PURPOSE: Make copies of and apply a skimmer to various MC root files.
# SYNTAX:  ./<this_script>.sh
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-05-21
# UPDATED: 2021-05-26
##############################################################################
samples=( DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root )
samples+=( TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root )
samples+=( WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root )
samples+=( ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root )

skimmer="apply_preselections_minimal.C"
skimmer_copy="${skimmer/.C/_copy.C}"

for filename in "${samples[@]}"; do
    cp ${skimmer} ${skimmer_copy}
    sed -i "s/FILENAME/${filename}/g" ${skimmer_copy}
    # Change name of main function to be the same name as the macro.
    sed -i "s/${skimmer/.C/}/${skimmer_copy/.C/}/g" ${skimmer_copy}
    echo "Skimming: ${filename}"
    root -l -b -q ${skimmer_copy}
    echo "Done."
done

rm ${skimmer_copy}