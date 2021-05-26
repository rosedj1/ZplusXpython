#!/bin/bash
##############################################################################
# PURPOSE: Do entire non-ZZ background analysis.
# NOTES:   Calculates fake rates, applies them 
# SYNTAX:  ./<this_script>.sh
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-05-26
# UPDATED: 
##############################################################################
conda activate my_root_env

echo "--- Evaluating Fake Rates ---"
python main_FR_CR.py
echo "--- Removing WZ from FR ---"
python WZremoval_from_FR_comp.py
echo "--- Estimating reducible background contribution (including FRs) ---"
python main_estimateZX_ntuples.py
python estimate_final_numbers_macro.py
echo "--- Plotting histograms ---"
python plotting_macros.py
echo "Done."