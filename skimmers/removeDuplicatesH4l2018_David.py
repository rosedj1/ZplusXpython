from ROOT import TFile

def removeDuplicatesH4l(dirData):

    era = "2018_smallerstats"
    # era = "Run2018-17Sep2018_hzz4l"
    
    f_DoubleMu = TFile(dirData+"DoubleMuon_"+era+".root","READ")
    t_DoubleMu = f_DoubleMu.Get("Ana/passedEvents")

    f_MuonEG = TFile(dirData+"MuonEG_"+era+".root","READ")
    t_MuonEG = f_MuonEG.Get("Ana/passedEvents")

    f_EG = TFile(dirData+"EGamma_"+era+".root","READ")
    t_EG = f_EG.Get("Ana/passedEvents")

    f_SingleMuon = TFile(dirData+"SingleMuon_"+era+".root","READ")
    t_SingleMuon = f_SingleMuon.Get("Ana/passedEvents")

    DoubleMuPaths = ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v","HLT_TripleMu_10_5_5_DZ_v","HLT_TripleMu_12_10_5_v"]
    EGPaths = ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v","HLT_DoubleEle25_CaloIdL_MW_v","HLT_Ele32_WPTight_Gsf_v"]
    MuonEGPaths = ["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v","HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v","HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v","HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v","HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ_v","HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ_v"]
    SingleMuonPaths = ["HLT_IsoMu24_v"] 

    ### DoubleMu ###
    n=0
    f_new_DoubleMu = TFile("DoubleMu_"+era+"_NoDuplicates.root","recreate")
    t_new_DoubleMu = t_DoubleMu.CloneTree(0)

    nentries = t_DoubleMu.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print(i,"/",nentries,'DoubleMu'        )
        t_DoubleMu.GetEntry(i)        

        passed = False
        for path in DoubleMuPaths:
            if (path in str(t_DoubleMu.triggersPassed)): passed=True

        if passed:
            t_new_DoubleMu.Fill()                
            n+=1

    t_new_DoubleMu.Print()
    t_new_DoubleMu.AutoSave()
    del f_new_DoubleMu
    print(n,'DoubleMU')
      
    ### EG ###
    f_new_EG = TFile("EG_"+era+"_NoDuplicates.root","recreate")
    t_new_EG = t_EG.CloneTree(0)
    nentries = t_EG.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print(i,"/",nentries,'EG'        )
        t_EG.GetEntry(i)        

        passed = False
        for path in EGPaths:
            if (path in str(t_EG.triggersPassed)): passed=True

        for path in DoubleMuPaths:
            if (path in str(t_EG.triggersPassed)): passed=False

        if passed:
            t_new_EG.Fill()                
            n+=1
    
    t_new_EG.Print()
    t_new_EG.AutoSave()
    del f_new_EG
    print(n,'DoubleMu+EG')


    ### MuonEG ###
    f_new_MuonEG = TFile("MuonEG_"+era+"_NoDuplicates.root","recreate")
    t_new_MuonEG = t_MuonEG.CloneTree(0)

    nentries = t_MuonEG.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print(i,"/",nentries,'MuonEG'        )
        t_MuonEG.GetEntry(i)        

        passed = False
        for path in MuonEGPaths:
            if (path in str(t_MuonEG.triggersPassed)): passed=True

        for path in EGPaths:
            if (path in str(t_MuonEG.triggersPassed)): passed=False

        for path in DoubleMuPaths:
            if (path in str(t_MuonEG.triggersPassed)): passed=False

        if passed:
            t_new_MuonEG.Fill()                
            n+=1

    t_new_MuonEG.Print()
    t_new_MuonEG.AutoSave()
    del f_new_MuonEG
    print(n,'DoubleMu+EG+MuonEG')

    ### SingleMuon ###
    f_new_SingleMuon = TFile("SingleMuon_"+era+"_NoDuplicates.root","recreate")
    t_new_SingleMuon = t_SingleMuon.CloneTree(0)

    nentries = t_SingleMuon.GetEntries()
    for i in range(nentries):        
        if (i%10000==0): print(i,"/",nentries,'SingleMuon'        )
        t_SingleMuon.GetEntry(i)        

        passed = False
        for path in SingleMuonPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=True

        for path in MuonEGPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        for path in EGPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        for path in DoubleMuPaths:
            if (path in str(t_SingleMuon.triggersPassed)): passed=False

        if passed:
            t_new_SingleMuon.Fill()                
            n+=1

    t_new_SingleMuon.Print()
    t_new_SingleMuon.AutoSave()
    del f_new_SingleMuon
    print(n,'DoubleMu+MuonEG+EG+SingleMuon')

# removeDuplicatesH4l("/cms/data/store/user/t2/users/dsperka/Run2/HZZ4l/SubmitArea_13TeV/rootfiles_Data80X_hzz4lskim_M17_Feb21/")
removeDuplicatesH4l("/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/smallerstats/")
