#!/bin/bash
#-----------------------------------------------------------------------------
# PURPOSE: Run a python script which uses the HZZ Analyzer on a single event
#          over many events.
# SYNTAX:  ./this_script.sh  >  outfile.txt
# NOTE:
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
# UPDATED: 2021-10-21
#-----------------------------------------------------------------------------

# Elisa's 3P1F has 631 unique events.
# Elisa's 2P2F has 2147 unique events.

# Inclusive on both ends!
for num in {135..630}; do
# for num in {0..2146}; do
# for num in {0..630}; do
    # echo $num
    if (( $num % 4 == 0 )) && [ $num -ne 0 ]; then
        echo "...Sleeping for 180 sec..."
        sleep 180
    fi
    echo "Running code using index: ${num}"
    echo $(python3 make_rootfiles_from_evtid_dct.py -i ${num}) > "../output/txt/index${num}_from_3p1f_dct.txt" &
done