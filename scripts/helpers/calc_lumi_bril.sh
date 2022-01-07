# FIXME: This script is complete, but has not been tested.
#!/bin/bash
##############################################################################
# PURPOSE: Print the total integrated luminosity from a series of lumi files.
# NOTES:
# - You should be one dir above your crab dir.
#   E.g. <you_are_here>/crab_DoubleMuon_Run2018A-17Sep2018-v2
# - Modify `glob_file_list` to grab the crab dirs you need.
# SYNTAX:  ./<this_script>.sh
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-05-26
# UPDATED: 2021-10-17
##############################################################################
# The name of the file to store all L_int vals.
outfile="lumi_2018_test02.txt"
lumifile="processedLumis.json"
overwrite=true

glob_file_list=( crab*Run2018* )

function get_lumi {
    # Print out the recorded lumi from the file ($1).
    tail -n 5 $1 | head -n 1 | cut -d\| -f7 | sed 's/ //'
}

# If `outfile` does not exist or we wish to overwrite it, create it.
if [ ! -e "${outfile}" ] || test overwrite; then
    echo -n > "${outfile}"
fi

for d in "${glob_file_list[@]}"; do

    echo "${d}:"
    echo "Doing \`crab report\` to get 'processedLumis.json'"
    crab report -d "${d}"

    echo "Entering ${d}/results/"
    cd ${d}/results/

    echo "Storing luminosity from lumi sections in file:"
    echo "${d}/results/output_brilcalc.txt"
    # brilcalc lumi -c web -i "${lumifile}" > output_brilcalc.txt
    brilcalc lumi -i "${lumifile}" -c web > output_brilcalc.txt
    
    printf "Storing total luminosity in file:\n${outfile}\n" 
    lumi_inv_ub=$( get_lumi output_brilcalc.txt )
    # Convert to fb^{-1}.
    lumi_inv_fb=$( bc -l <<< "scale=6; $lumi_inv_ub/1000000000" )
    
    echo "${d}, ${lumi_inv_fb}" >> ../../"${outfile}"
    # get_lumi output_brilcalc.txt >> ../../"${outfile}"
    cd ../..
    printf "Done.\n\n"
done