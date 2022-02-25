#!/bin/bash

indirs=( )
# indirs+=( "freshinstall_20220217/hists_WZxs4p43_withFSR_autoscript/" )
# indirs+=( "freshinstall_20220217/hists_WZxs4p43_woFSR_autoscript" )
# indirs+=( "freshinstall_20220217/hists_WZxs5p26_withFSR_autoscript" )
# indirs+=( "freshinstall_20220224/hists_WZxs4p43_withFSR_autoscript" )
indirs+=( "freshinstall_20220224/hists_WZxs4p43_woFSR_autoscript" )
indirs+=( "freshinstall_20220224/hists_WZxs5p26_woFSR_autoscript" )
# indirs+=( "freshinstall_20220224/hists_WZxs5p26_withFSR_autoscript" )

for year in 2017 2018; do
    for d in ${indirs[@]}; do
        python /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/scripts/plotters/plot_fakerate_hists.py \
            -d "${d}/Hist_Data_ptl3_Data_${year}.root" \
            -f "${d}/Hist_Data_ptl3_WZremoved_${year}.root" \
            -o "${d}/fakerates_${year}UL_yaxissyncwithAN.pdf" \
            -y "${year}"
        # echo "it is the year ${year} and dir ${d}"
    done
done