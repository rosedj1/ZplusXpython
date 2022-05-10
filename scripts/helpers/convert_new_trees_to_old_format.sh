#!/bin/bash

names=( )
# names+=( "WZ_preVFP" )
names+=( "DY50_preVFP" )
names+=( "TT_preVFP" )
# names+=( "Data_preVFP" )
names+=( "DY50_postVFP" )
names+=( "Data_postVFP" )
names+=( "WZ_postVFP" )
names+=( "TT_postVFP" )
# names+=( "ZZ_preVFP" )
names+=( "ZZ_postVFP" )

for n in ${names[@]}; do
    echo "Running over ${n}."
    python /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/convert_tree_new2old.py -n ${n} &
done

