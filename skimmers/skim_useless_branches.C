/**
 * PURPOSE: Copy a TTree to a new root file, but only keep certain branches.
 * NOTES: User should add/remove branches in vector branches in script.
 * This code doesn't seem to work with files that are too large.
 * Probably a problem with memory when opening a very large TTree.
 * It couldn't skim a 773 GB Drell-Yan MC file.
 * FIXED! Simply do: t->CloneTree(-1, "fast")
 * AUTHOR: Jake Rosenzweig, jake.rose@cern.ch
 * CREATED: 2021-11-12
 * UPDATED: 2022-02-10
 */

#include <iostream>
#include <vector>
#include "TFile.h"
#include "TTree.h"
#include "TString.h"

using namespace std;

void skim_useless_branches() {
  /**
   * 
   */
  // TString infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/SingleMuon.root";
  // TString outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/SingleMuon_skimmed.root";
  // TString infile = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/MC/2018/fullstats/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root";
  // TString outfile = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/MC/2018/fullstats/skimmedbranches/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root";
  TString infile = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2017/fullstats/SingleElectron_2017.root";
  TString outfile = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L/Data/2017/fullstats/skimmedbranches/fewbranches/SingleElectron_2017.root";
  TString intree = "Ana/passedEvents";
  unsigned int n_evts_to_keep = -1;  // Use -1 for "all".
  bool verbose = true;

  // Branches to keep.
  /*
  vector<TString> branches{
    "Run",
    "LumiSect",
    "Event",
    "passedFullSelection",
    "passedZ1LSelection",
    "passedZXCRSelection",
    "passedTrig",
    "nZXCRFailedLeptons",
    "finalState",
    "eventWeight",
    "k_qqZZ_qcd_M",
    "k_qqZZ_ewk",
    "lep_Hindex",
    "lep_id",
    "lep_pt",
    "lep_eta",
    "lep_phi",
    "lep_mass",
    "lepFSR_pt",
    "lepFSR_eta",
    "lepFSR_phi",
    "lepFSR_mass",
    "lep_RelIsoNoFSR",
    "lep_tightId",
    "met",
    "massZ1",
    "massZ2",
    "mass4l",
  };
  */
  vector<TString> branches{
    "Run",
    "Event",
    "LumiSect",
    "nVtx",
    "nInt",
    "finalState",
    "passedFullSelection",
    "passedZ1LSelection",
    "passedZXCRSelection",
    "passedTrig",
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
    "D_bkg_kin",
    "D_bkg_kin_vtx_BS",
    "D_bkg",
    "D_VBF",
    "EventCat",
    "lep_matchedR03_PdgId",
    "lep_matchedR03_MomId",
    "lep_matchedR03_MomMomId",
    
    // New branches that will be added for RedBkg studies.
    // "is2P2F",
    // "is3P1F",
    // "isData",
    // "isMCzz",
    // "fr2_down",
    // "fr2",
    // "fr2_up",
    // "fr3_down",
    // "fr3",
    // "fr3_up",
    // "eventWeightFR_down",
    // "eventWeightFR",
    // "eventWeightFR_up",
    // "lep_RedBkgindex",

  TFile *tf = new TFile(infile, "READ");
  TTree *tree = (TTree*)tf->Get(intree);
  cout << "Successfully opened file:\n" << infile << endl;
  cout << "TTree has " << tree->GetEntries() << " entries." << endl;
  // cout << "Saving " << n_evts_to_keep << "(" << n_evts_to_keep/tree->GetEntries() << ")" << " entries." << endl;

  // Turn off all branches, then manually turn on the ones to keep.
  tree->SetBranchStatus("*", 0);
  if (verbose) cout << "Saving branches:" << endl;
  for (auto & branch : branches) {
    if (verbose) cout << "  " << branch << endl;
    tree->SetBranchStatus(branch, 1);
  }

  TFile *tf_out = new TFile(outfile, "RECREATE");
  // TTree *newtree = tree->CloneTree(n_evts_to_keep);
  TTree *newtree = tree->CloneTree(n_evts_to_keep, "fast");

  newtree->Write();
  cout << "New TTree saved to file:\n" << outfile << endl;
  return;
} // end function
