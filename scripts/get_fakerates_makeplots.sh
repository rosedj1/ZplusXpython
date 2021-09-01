#!/bin/bash
# Purpose: Analyze specified samples (Data, DY, TTbar, WZ, ZZ) for Z+L events.
#          Sort events into 2P2F, 3P1F, 4P0F histograms.
#          Also create fake rate hists.
# Syntax: ./<this_script.sh>
# Author: Jake Rosenzweig
# Created: 2021-08-27
# Updated: 2021-08-30
#--- User Switches ---#
process_data=0
process_dy50=0
process_tt=0
process_wz=0
process_zz=0

remove_wz=1
draw_fr_plots=1

overwrite=0
# WARNING: check `draw_fr_plots` for overwrite flag (`x`).

#--- User Params ---#
infile_root_data="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_4P_CR/Data_2018_NoDuplicates.root"
infile_root_dy50="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root"
infile_root_tt="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_2018.root"
infile_root_wz="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root"
infile_root_zz="/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_4P_CR/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_2018.root"

outdir_rootfiles="/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/data/best_asof_20210827/uselepFSRtocalc_mZ1"
outpdf="/blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/plots/fakerate_hists/jakesfiles_vukasinsframework_20210830_uselepFSRtocalc_mZ1_butnoFSRonprobelep.pdf"

outfile_hist_data="${outdir_rootfiles}/Hist_Data_ptl3_Data.root"
# outfile_hist_dy50="${outdir_rootfiles}/Hist_MC_ptl3_DY50.root"
# outfile_hist_tt="${outdir_rootfiles}/Hist_MC_ptl3_TT.root"
outfile_hist_wz="${outdir_rootfiles}/Hist_MC_ptl3_WZ.root"
# outfile_hist_zz="${outdir_rootfiles}/Hist_MC_ptl3_ZZ.root"
outfile_hist_wz_FRremoved="${outdir_rootfiles}/Hist_Data_ptl3_WZremoved.root"

function process_sample {
    # Use `main_FR_CR.py` to process a sample, plugging in filepaths.
    #
    # Parameters
    # ----------
    # $1 : int
    #     1 to process samples (0 to skip) .
    # $2 : str
    #     Sample rootfile inpath.
    # $3 : str
    #     Hist rootfile outdir.
    # $4 : str
    #     Nickname of sample.
    # $5 : int
    #     1 to overwrite output file (0 otherwise).
    if test ${1} -eq 1; then
        echo "Estimating fake rates in ${4}..."
        python /blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/main_FR_CR.py \
            --infile="${2}" \
            --outdir="${3}" \
            --nickname="${4}" \
            --fsr \
            --overwrite="${5}" && echo "Done."
        if [ $? -eq 0 ]; then
            printf "Files made at: ${3}\n"
        fi
    fi
}

process_sample ${process_data} ${infile_root_data} ${outdir_rootfiles} "Data" ${overwrite}
process_sample ${process_dy50} ${infile_root_dy50} ${outdir_rootfiles} "DY50" ${overwrite}
process_sample ${process_tt}   ${infile_root_tt}   ${outdir_rootfiles} "TT"   ${overwrite}
process_sample ${process_wz}   ${infile_root_wz}   ${outdir_rootfiles} "WZ"   ${overwrite}
process_sample ${process_zz}   ${infile_root_zz}   ${outdir_rootfiles} "ZZ"   ${overwrite}

#--- Remove WZ contribution from FRs. ---#
if test ${remove_wz} -eq 1; then
    echo "Removing WZ contribution from Fake Rates..."
    cd /blue/avery/rosedj1/ZplusXpython
    source setup.sh
    python /blue/avery/rosedj1/zplusx_vukasin/ZplusXpython/WZremoval_from_FR_comp.py \
        --infile_data="${outfile_hist_data}" \
        --infile_wz="${outfile_hist_wz}" \
        --outfile="${outdir_rootfiles}/Hist_Data_ptl3_WZremoved.root"

        test $? -eq 0 && echo "Created WZ-removed FR file: ${outdir_rootfiles}\n" || exit 1
fi

if test ${draw_fr_plots} -eq 1; then
    echo "Drawing FR plots..."
    python /blue/avery/rosedj1/ZplusXpython/scripts/plotters/plot_fakerate_hists.py \
        --infile_data="${outfile_hist_data}" \
        --infile_fr="${outfile_hist_wz_FRremoved}" \
        --outfile="${outpdf}" \
        --overwrite="${overwrite}"
        
        test $? -eq 0 && printf "FR plot made:\n${outpdf}\n" || exit 2
fi