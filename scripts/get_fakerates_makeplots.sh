#!/bin/bash
# Purpose: Analyze specified samples (Data, DY, TTbar, WZ, ZZ) for Z+L events.
#          Sort events into 2P2F, 3P1F, 4P0F histograms.
#          Also create fake rate hists.
# Syntax: ./<this_script.sh>
# Author: Jake Rosenzweig
# Created: 2021-08-27
# Updated: 
#--- User Switches ---#
process_data=0
process_wz=0
remove_wz=0
draw_fr_plots=1
# WARNING: check `draw_fr_plots` for overwrite flag (`x`).

#--- User Params ---#
infile_rootdata="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_4P_CR/Data_2018_NoDuplicates.root"
infile_rootwz="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root"

outdir_rootfiles="/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/nolepFSR"
outpdf="/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/plots/fakerate_hists/jakesfiles_vukasinsframework_20210827_nolepFSRfor_mZ1.pdf"

outfile_histdata="${outdir_rootfiles}/Hist_Data_ptl3_Data.root"
outfile_histwz="${outdir_rootfiles}/Hist_MC_ptl3_WZ.root"
outfile_histwz_FRremoved="${outdir_rootfiles}/Hist_Data_ptl3_WZremoved.root"


function tell_output {
    if [ $? -eq 0 ]; then
        printf "Files made at: ${1}\n"
    fi
}

if test ${process_data} -eq 1; then
    echo "Estimating fake rates in Data..."
    python /blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/main_FR_CR.py \
        --infile="${outfile_histdata}" \
        --outdir="${outdir_rootfiles}" \
        --nickname="Data" && echo "Done."
    # --fsr \  # Will include FSR in mZ1 calc. By default Vukasin does not.

    # INTERESTING. You can't have a line in bash that ends with '\'
    # and then the next line start with '#'.

    tell_output "${outdir_rootfiles}"
fi

if test ${process_wz} -eq 1; then
    echo "Estimating fake rates in WZ..."
    python /blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/main_FR_CR.py \
        --infile="${outfile_histwz}" \
        --outdir="${outdir_rootfiles}" \
        --nickname="WZ" && echo "Done."
        # --fsr \  # Will include FSR in mZ1 calc. By default Vukasin does not.

    tell_output "${outdir_rootfiles}"
fi

if test ${remove_wz} -eq 1; then
    echo "Removing WZ contribution from Fake Rates..."
    cd /blue/avery/rosedj1/ZplusXpython
    source setup.sh
    python /blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/WZremoval_from_FR_comp.py \
        --infile_data="${outfile_histdata}" \
        --infile_wz="${outfile_histwz}" \
        --outfile="${outfile_histwz_FRremoved}" && echo "Done." || exit 1
fi

if test ${draw_fr_plots} -eq 1; then
    echo "Drawing FR plots..."
    python /blue/avery/rosedj1/ZplusXpython/scripts/plotters/plot_fakerate_hists.py \
        --infile_data="${outfile_histdata}" \
        --infile_fr="${outfile_histwz_FRremoved}" \
        --outfile="${outpdf}" \
        --overwrite && echo "Done." || exit 2
fi