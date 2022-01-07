#!/bin/bash
#-----------------------------------------------------------------------------
# PURPOSE: Run a python script which uses the HZZ Analyzer on a single event
#          over many events.
# SYNTAX:  ./this_script.sh  >  outfile.txt
# NOTE:
#    - Invokes `make_rootfiles_from_evtid_dct.py`.
#    - Start within the /scripts/ dir.
#    - I find it very difficult to capture the Analyzer output.
#      I think it's due to a specific thread printing to the screen.
#    - When processing X files simultaneously, it takes ~Y seconds per file:
#          -----------
#          | X |  Y  |
#          ----|------
#          | 1 | 180 |
#          | 3 | 220 |
#          | 4 | 220 |
#          | 5 | 350 |
#          -----------
# AUTHOR:  Jake Rosenzweig
# CREATED: 2021-10-20
# UPDATED: 2021-10-27
#-----------------------------------------------------------------------------

# Elisa's 3P1F has 631 unique events.
# Elisa's 2P2F has 2147 unique events.
# Of these, there are 118 events that are found in both her 2P2F and 3P1F CRs.

# for num in {407..630}; do
# for num in {0..2146}; do
# for num in {0..630}; do
basename="elisa_unique_2p2f_3p1f_commontobothCRs"
files_per_batch=4
# Inclusive on both ends!
for num in {40..117}; do
    # echo $num
    if (( $num % $files_per_batch == 0 )) && [ $num -ne 0 ]; then
        echo "...Sleeping for 220 sec..."
        sleep 220
    fi
    echo "Running code using index: ${num}"
    echo $(python3 make_rootfiles_from_evtid_dct.py -i ${num}) > "../output/txt/${basename}_index${num}.txt" &
done