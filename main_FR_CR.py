#import stage
import numpy as np
import ROOT
from ROOT import TCanvas, TH1F, TF1, TLegend, gPad, THStack, TColor
#import tdrstyle
import os.path
import os
from array import array
#import yaml
#import sys
import math

from analyzeZX import *

fileList = [
    # "/cmsuf/data/store/user/drosenzw/UFHZZAnalysisRun2/Data/skim2L/SingleMuon/crab_SingleMuon_Run2018A-17Sep2018-v2/210506_233459/0000/SingleMuon_Run2018A-17Sep2018-v2_1.root",
    # "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/Data/skim2L/Data_DoubleMuonRunA_EGammaRunB_MuonEGRunC_SingleMuonRunD.root"
    "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/Data/skim2L/Data_mix_test1.root",
    ]
#fileList = ["../Data_skimmed.root",
#            "../DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_2018filter2l_new_ZX.root",
#            "../TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new_ZX.root",
#            "../WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_2018_filter2l_new_ZX.root",
#            "../ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new_ZX.root"
#            ]

RootNickNames = ["Data"]#,"DY50","TT","WZ","ZZ"]
#RootNickNames = ["Data","DY50","TT","WZ","ZZ"]

# For testing
#fileList = ["../DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_2018filter2l_new_ZX.root",]
#RootNickNames = ["DY50"]

print("First stage of processing (FR computation and CR histogram creation) has been initiated.\n")

for i in range(len(fileList)):
    inFile =  ROOT.TFile.Open(fileList[i], "READ")
    if i == 0:
        tree = inFile.Get("Ana/passedEvents")
        # tree = inFile.Get("passedEvents")
    else:
        tree = inFile.Get("Ana/passedEvents")

    print("File: \"" + fileList[i] + "\" has been opened.\n-- It has "+str(tree.GetEntries())+" events.\n")
    analyzeZX(tree, RootNickNames[i])
    inFile.Close()

    


