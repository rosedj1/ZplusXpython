from ROOT import *

def removeDuplicatesH4l(dirData):

    era = "Run2017-17Nov2017_hzz4l"

    f_DoubleEG = TFile(dirData+"DoubleEG_"+era+".root","READ")
    t_DoubleEG = f_DoubleEG.Get("Ana/passedEvents")
    
    f_DoubleMu = TFile(dirData+"DoubleMuon_"+era+".root","READ")
    t_DoubleMu = f_DoubleMu.Get("Ana/passedEvents")

    f_MuonEG = TFile(dirData+"MuonEG_"+era+".root","READ")
    t_MuonEG = f_MuonEG.Get("Ana/passedEvents")

    f_SingleElectron = TFile(dirData+"SingleElectron_"+era+".root","READ")
    t_SingleElectron = f_SingleElectron.Get("Ana/passedEvents")

    f_SingleMuon = TFile(dirData+"SingleMuon_"+era+".root","READ")
    t_SingleMuon = f_SingleMuon.Get("Ana/passedEvents")


    DoubleEGPaths = [ "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v","HLT_DoubleEle33_CaloIdL_MW_v","HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL_v"]
    DoubleMuPaths = [ "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v","HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8_v","HLT_TripleMu_10_5_5_DZ_v","HLT_TripleMu_12_10_5_v"]
    MuonEGPaths = [ "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v","HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v","HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v","HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v","HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ_v","HLT_Mu8_DiEle12_CaloIdL_TrackIdL_v","HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ_v"]
    SingleElePaths = [ "HLT_Ele35_WPTight_Gsf_v","HLT_Ele38_WPTight_Gsf_v","HLT_Ele40_WPTight_Gsf_v"]
    SingleMuPaths = [ "HLT_IsoMu27_v"] 

    ### DoubleEG ###
    f_new_DoubleEG = TFile("DoubleEG_"+era+"_NoDuplicates.root","recreate")
    t_new_DoubleEG = t_DoubleEG.CloneTree(0)
    n=0
    nentries = t_DoubleEG.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print i,"/",nentries,'DoubleEG'        
        t_DoubleEG.GetEntry(i)        

        passed = False
        for path in DoubleEGPaths:
            if (path in str(t_DoubleEG.triggersPassed)): passed=True

        if passed:
            t_new_DoubleEG.Fill()                
            n+=1

    t_new_DoubleEG.Print()
    t_new_DoubleEG.AutoSave()
    del f_new_DoubleEG
    print n,'DoubleEG'

    ### DoubleMu ###
    f_new_DoubleMu = TFile("DoubleMu_"+era+"_NoDuplicates.root","recreate")
    t_new_DoubleMu = t_DoubleMu.CloneTree(0)

    nentries = t_DoubleMu.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print i,"/",nentries,'DoubleMu'        
        t_DoubleMu.GetEntry(i)        

        passed = False
        for path in DoubleMuPaths:
            if (path in str(t_DoubleMu.triggersPassed)): passed=True

        for path in DoubleEGPaths:
            if (path in str(t_DoubleMu.triggersPassed)): passed=False

        if passed:
            t_new_DoubleMu.Fill()                
            n+=1

    t_new_DoubleMu.Print()
    t_new_DoubleMu.AutoSave()
    del f_new_DoubleMu
    print n,'DoubleEG+DoubleMu'
      

    ### MuonEG ###
    f_new_MuonEG = TFile("MuonEG_"+era+"_NoDuplicates.root","recreate")
    t_new_MuonEG = t_MuonEG.CloneTree(0)

    nentries = t_MuonEG.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print i,"/",nentries,'MuonEG'        
        t_MuonEG.GetEntry(i)        

        passed = False
        for path in MuonEGPaths:
            if (path in str(t_MuonEG.triggersPassed)): passed=True

        for path in DoubleEGPaths:
            if (path in str(t_MuonEG.triggersPassed)): passed=False

        for path in DoubleMuPaths:
            if (path in str(t_MuonEG.triggersPassed)): passed=False

        if passed:
            t_new_MuonEG.Fill()                
            n+=1

    t_new_MuonEG.Print()
    t_new_MuonEG.AutoSave()
    del f_new_MuonEG
    print n,'DoubleMu+DoubleEG+MuonEG'

    ### SingleElectron ###
    f_new_SingleElectron = TFile("SingleElectron_"+era+"_NoDuplicates.root","recreate")
    t_new_SingleElectron = t_SingleElectron.CloneTree(0)
    nentries = t_SingleElectron.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print i,"/",nentries,'SingleElectron'        
        t_SingleElectron.GetEntry(i)        

        passed = False
        for path in SingleElePaths:
            if (path in str(t_SingleElectron.triggersPassed)): passed=True

        for path in MuonEGPaths:
            if (path in str(t_SingleElectron.triggersPassed)): passed=False

        for path in DoubleEGPaths:
            if (path in str(t_SingleElectron.triggersPassed)): passed=False

        for path in DoubleMuPaths:
            if (path in str(t_SingleElectron.triggersPassed)): passed=False

        if passed:
            t_new_SingleElectron.Fill()                
            n+=1
    
    t_new_SingleElectron.Print()
    t_new_SingleElectron.AutoSave()
    del f_new_SingleElectron
    print n,'DoubleEG+DoubleMu+MuonEG+SingleElectron'


    ### SingleMuon ###
    f_new_SingleMuon = TFile("SingleMuon_"+era+"_NoDuplicates.root","recreate")
    t_new_SingleMuon = t_SingleMuon.CloneTree(0)

    nentries = t_SingleMuon.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print i,"/",nentries,'SingleMuon'        
        t_SingleMuon.GetEntry(i)        

        passed = False
        for path in SingleMuPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=True

        for path in SingleElePaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        for path in MuonEGPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        for path in DoubleEGPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        for path in DoubleMuPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        if passed:
            t_new_SingleMuon.Fill()                
            n+=1

    t_new_SingleMuon.Print()
    t_new_SingleMuon.AutoSave()
    del f_new_SingleMuon
    print n,'DoubleEG+DoubleMu+MuonEG+SingleElectron+SingleMuon'

removeDuplicatesH4l("/raid/raid7/dsperka/Run2/HZZ4l/SubmitArea_13TeV/")

#  LocalWords:  SingleElePaths
