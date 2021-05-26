#!/bin/bash
##############################################################################
# PURPOSE: Print the total integrated luminosity from a series of lumi files.
# NOTES:   You should be one dir above your crab dir.
#          E.g. <you_are_here>/crab_DoubleMuon_Run2018A-17Sep2018-v2
#          You first need to do `crab report -d <crab_dir>`
#          TODO: [] Implement crab report.
# SYNTAX:  ./<this_script>.sh
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-05-26
# UPDATED: 
##############################################################################
# The name of the file to store each L_int.
outfile="lumi_2018_test.txt"
lumifile="processedLumis.json"
wildcard_file_list=crab_[DEMS][oGui]*

function get_lumi {
    # Print out the recorded lumi from the file ($1).
    tail -n 5 $1 | head -n 1 | cut -d\|  -f7
}

touch "${outfile}"
for d in "${wildcard_file_list}"; do
    echo "Entering ${d}"
    cd "${d}/results/"
    brilcalc lumi -c web -i "${lumifile}" > output_brilcalc.txt
    get_lumi $d >> ../../"${outfile}"
    cd ../..
done

# Print the sum of L_int. Convert to fb^{-1}.
awk '{sum+=$1} END{print sum/1E9}' "${outfile}"