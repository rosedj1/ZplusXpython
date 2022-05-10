"""Reformat new RB TTree style into old style.
# Syntax: python <script>.py
# 
# Notes:
#   Style differences:
"""
import ROOT as r
from array import array
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n', dest="name")

args = parser.parse_args()

old_file = f"/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/skim_osmethod_perfectxBFsync_2016_{args.name}.root"
old_tf = r.TFile(old_file, 'read')
tree_name = "passedEvents"
old_tree = old_tf.Get(tree_name)

old_tree.SetBranchStatus("*", 0)
old_br_to_keep = [
    "Run",             
    "Event",           
    "LumiSect",        
    "nVtx",            
    "nInt",            
    "finalState",      
    "passedTrig",      
    "passedFullSelection", 
    "passedZ1LSelection", 
    "passedZXCRSelection", 
    "nZXCRFailedLeptons", 
    "genWeight",       
    "k_ggZZ",          
    "k_qqZZ_qcd_M",    
    "k_qqZZ_ewk",      
    "pileupWeight",    
    "dataMCWeight",    
    "eventWeight",     
    "prefiringWeight", 
    "crossSection",    
    "lep_d0BS",        
    "lep_d0PV",        
    "lep_numberOfValidPixelHits", 
    "lep_trackerLayersWithMeasurement", 
    "vtxLep_BS_pt",    
    "vtxLep_BS_pt_NoRoch", 
    "vtxLep_BS_ptError", 
    "vtxLep_BS_eta",   
    "vtxLep_BS_phi",   
    "vtxLep_BS_mass",  
    "vtxLep_BS_d0",    
    "vtxLep_pt",       
    "vtxLep_ptError",  
    "vtxLep_eta",      
    "vtxLep_phi",      
    "vtxLep_mass",     
    "vtxLepFSR_BS_pt", 
    "vtxLepFSR_BS_eta", 
    "vtxLepFSR_BS_phi", 
    "vtxLepFSR_BS_mass", 
    "vtxLepFSR_pt",    
    "vtxLepFSR_eta",   
    "vtxLepFSR_phi",   
    "vtxLepFSR_mass",  
    "lep_id",          
    "lep_pt",          
    "lep_pterr",       
    "lep_eta",         
    "lep_phi",         
    "lep_mass",        
    "lepFSR_pt",       
    "lepFSR_eta",      
    "lepFSR_phi",      
    "lepFSR_mass",     
    "lep_Hindex",      
    "lep_matchedR03_PdgId", 
    "lep_matchedR03_MomId", 
    "lep_matchedR03_MomMomId", 
    "lep_ecalDriven",  
    "lep_tightId",     
    "lep_Sip",         
    "lep_RelIso",      
    "lep_RelIsoNoFSR", 
    "dataMC_VxBS",     
    "mass4l",          
    "mass4lErr",       
    "mass4lREFIT",     
    "mass4lErrREFIT",  
    "massZ1REFIT",     
    "massZ2REFIT",     
    "mass4l_vtx_BS",   
    "mass4l_vtxFSR_BS", 
    "mass4lErr_vtx_BS", 
    "mass4lREFIT_vtx_BS", 
    "mass4lErrREFIT_vtx_BS", 
    "massZ1REFIT_vtx_BS", 
    "massZ2REFIT_vtx_BS", 
    "mass4l_vtx",      
    "mass4l_vtxFSR",   
    "mass4lErr_vtx",   
    "mass4lREFIT_vtx", 
    "mass4lErrREFIT_vtx", 
    "massZ1",          
    "massZ2",          
    "met",             
    "EventCat",        
    "D_bkg_kin",       
    "D_bkg_kin_vtx_BS", 
    "D_bkg",           
    "D_VBF",           
    "is2P2F",          
    "is3P1F",          
    "isData",          
    "isMCzz",          
    # "fr2_down",        
    # "fr2",             
    # "fr2_up",          
    # "fr3_down",        
    # "fr3",             
    # "fr3_up",          
    "eventWeightFR_down", 
    "eventWeightFR",   
    "eventWeightFR_up", 
    "lep_RedBkgindex",
    ]
br_to_turnbackon = [
    "fakerate_down",
    "fakerate",
    "fakerate_up",
]
for br in old_br_to_keep:
    old_tree.SetBranchStatus(br, 1)

new_file = r.TFile(
    old_file.replace(".root", "_oldformat.root"), "recreate"
    )
new_tree = old_tree.CloneTree(0, "fast")

# New branches.
ptr_fr2_down = array('f', [0.])
ptr_fr2 = array('f', [0.])
ptr_fr2_up = array('f', [0.])
ptr_fr3_down = array('f', [0.])
ptr_fr3 = array('f', [0.])
ptr_fr3_up = array('f', [0.])
new_tree.Branch("fr2_down", ptr_fr2_down, "fr2_down/F")
new_tree.Branch("fr2", ptr_fr2, "fr2/F")
new_tree.Branch("fr2_up", ptr_fr2_up, "fr2_up/F")
new_tree.Branch("fr3_down", ptr_fr3_down, "fr3_down/F")
new_tree.Branch("fr3", ptr_fr3, "fr3/F")
new_tree.Branch("fr3_up", ptr_fr3_up, "fr3_up/F")

# Turn back on the branches to retrieve their data.
for br in br_to_turnbackon:
    old_tree.SetBranchStatus(br, 1)

for evt in old_tree:
    assert evt.fakerate[0] == evt.fakerate[1]
    if evt.is3P1F:
        # Identify whether lep2 or lep3 is the fake.
        if evt.fakerate[2] == 0:
            # Lep3 is fake and so has a fake rate.
            fk_down = evt.fakerate_down[3]
            fk = evt.fakerate[3]
            fk_up = evt.fakerate_up[3]
        elif evt.fakerate[3] == 0:
            # Lep2 is the fake.
            fk_down = evt.fakerate_down[2]
            fk = evt.fakerate[2]
            fk_up = evt.fakerate_up[2]
        else:
            raise ValueError
        
        # Force FR to be in lep3 position---this is consistent with "old way".
        ptr_fr2_down[0] = 0
        ptr_fr2[0] = 0
        ptr_fr2_up[0] = 0
        ptr_fr3_down[0] = fk_down
        ptr_fr3[0] = fk
        ptr_fr3_up[0] = fk_up

    elif evt.is2P2F:
        ptr_fr2_down[0] = evt.fakerate_down[2]
        ptr_fr2[0] = evt.fakerate[2]
        ptr_fr2_up[0] = evt.fakerate_up[2]
        ptr_fr3_down[0] = evt.fakerate_down[3]
        ptr_fr3[0] = evt.fakerate[3]
        ptr_fr3_up[0] = evt.fakerate_up[3]

    new_tree.Fill()

new_tree.Write()
# new_file.Close()
