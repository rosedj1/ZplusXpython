#import stage
# import numpy as np
import ROOT
# from ROOT import TCanvas, TH1F, TF1, TLegend, gPad, THStack, TColor
#import tdrstyle
# import os
# from array import array
#import yaml
#import sys
# import math

from analyzeZX import *

var_bin_dct = {
    "ptl3" : [],
    "m4l" : [],
}

fileList = [
    # "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/Data_2018_smallerstats.root",
    "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/smallerstats/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1_smallerstats.root"
    ]
#fileList = ["../Data_skimmed.root",
#            "../DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_2018filter2l_new_ZX.root",
#            "../TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new_ZX.root",
#            "../WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_2018_filter2l_new_ZX.root",
#            "../ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new_ZX.root"
#            ]

# RootNickNames = ["Data"]#,"DY50","TT","WZ","ZZ"]
RootNickNames = ["WZ"]

# For testing
#fileList = ["../DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_2018filter2l_new_ZX.root",]
#fRootNickNames = ["DY50"]

print("First stage of processing (FR computation and CR histogram creation) has been initiated.\n")

for i in range(len(fileList)):
# for i in range(1,2):
    inFile =  ROOT.TFile.Open(fileList[i], "READ")
    # if i == 0:
    #     tree = inFile.Get("Ana/passedEvents")
        # tree = inFile.Get("passedEvents")
    # else:
    tree = inFile.Get("Ana/passedEvents")
    n_evts = tree.GetEntries()

    print("File: {} has been opened.".format(fileList[i]))
    print("-- Found {} events.".format(n_evts))
    analyzeZX(tree, RootNickNames[i])
    inFile.Close()

    


