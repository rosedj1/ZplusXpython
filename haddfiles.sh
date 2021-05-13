#!/bin/bash

# samples=( DoubleMuon )
# samples=( EGamma )
# samples+=( MuonEG )
# samples+=( SingleMuon )

# samples=( DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8 )
# samples=( TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8 )
# samples+=( WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8 )
samples=( ZZTo4L_TuneCP5_13TeV_powheg_pythia8 )

for samp in "${samples[@]}"; do
    hadd -f "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/${samp}_2018.root" /cmsuf/data/store/user/drosenzw/UFHZZAnalysisRun2/Data/skim2L/${samp}/crab_${samp}*/*/*/*.root
    #--- Skim subset of Data ---#
    # hadd -f "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/${samp}_2018_smallerstats.root" /cmsuf/data/store/user/drosenzw/UFHZZAnalysisRun2/Data/skim2L/${samp}/crab_${samp}*A*/*/*/*_1[0-9].root
done