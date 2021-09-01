/**
 * PURPOSE: Skim a root file produced from the UFHZZ4L Analyzer.
 * NOTES:
 * - Useful for reducible background studies.
 * - VX+BS info is saved.
 * - Select events in the Z+L, Z+LL, and/or 4P control regions.
 * - Specify either Data or MC using `isData` and check file paths!
 * AUTHOR: Jake Rosenzweig, jake.rose@cern.ch
 * CREATED: 2021-05-20, happy birthday, Sheldoni!
 * UPDATED: 2021-08-31
 */

#include <iostream>
#include <cstdlib>
#include <vector>
#include "TFile.h"
#include "TH1F.h"
#include "TDirectory.h"
#include "TTree.h"
#include "TChain.h"
#include "TString.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include <numeric>

using namespace std;

void apply_redbkg_evt_selection_vxbs(
  TString infile,
  TString outfile,
  bool isData = true,
  bool do_Z1LSelection = true,
  bool do_ZXCRSelection = true,
  bool do_4PSelection = true
  ){
  /**
   * do_Z1LSelection  : Use for fake rate studies.
   * do_ZXCRSelection : Use for RedBkg estimation (apply fake rates).
   * do_4PSelection   : 4 prompt leptons.
   */
  TString intree;
  if (isData) {
    // infilename = "Data_2018_NoDuplicates.root";
    // indir = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/noduplicates/"
    // outfilename = "Data_2018_4P_CR.root";
  // TString infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/DoubleMuon_2018.root";
  // TString infile2 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/EGamma_2018.root";
  // TString infile3 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/MuonEG_2018.root";
  // TString infile4 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/SingleMuon_2018.root";
    // outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/ZL_ZLL_CR/" + outfilename;
    // outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/" + outfilename;
    intree = "passedEvents";
  } else {
    // MC.
    // infilename = "FILENAME"; // Will be replaced by bash script.
    // infilename = "WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_realistic_v15_ext1-v2_2018.root"; //"FILENAME"; // Will be replaced by bash script.
    // infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/" + infilename;
    // outfilename = infilename;
    // outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/4P_CR/" + outfilename;
    intree = "Ana/passedEvents";
  }

  // TString outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/Data_2018_ZL_ZLL_CRs.root";
  TFile *tf_out = new TFile(outfile, "RECREATE");
  TTree *newtree = new TTree("passedEvents","passedEvents");

  TChain *cc = new TChain(intree);

  cc->Add(infile);
  cout << "Successfully opened file:\n" << infile << endl;
  // cc->Add(infile2);
  // cc->Add(infile3);
  // cc->Add(infile4);

  TTreeReader reader(cc);
  unsigned int n_tot_tree = reader.GetEntries(true);
  // Assign TTreeReader to a branch on old tree.
  // TTreeReaderValue<ULong64_t> Event_reader(reader, "Event"); Doesn't store useful info.
  TTreeReaderValue<int>            finalState_reader(reader, "finalState");
  TTreeReaderValue<bool>           passedZ1LSelection_reader(reader, "passedZ1LSelection");
  TTreeReaderValue<bool>           passedZXCRSelection_reader(reader, "passedZXCRSelection");
  TTreeReaderValue<float>          eventWeight_reader(reader, "eventWeight");
  TTreeReaderValue<float>          k_qqZZ_qcd_M_reader(reader, "k_qqZZ_qcd_M");
  TTreeReaderValue<float>          k_qqZZ_ewk_reader(reader, "k_qqZZ_ewk");
  TTreeReaderValue<float>          met_reader(reader, "met");
  TTreeReaderArray<int>            lep_Hindex_reader(reader, "lep_Hindex");
  TTreeReaderValue<vector<float>>  lep_pt_reader(reader, "lep_pt");
  TTreeReaderValue<vector<float>>  lep_eta_reader(reader, "lep_eta");
  TTreeReaderValue<vector<float>>  lep_phi_reader(reader, "lep_phi");
  TTreeReaderValue<vector<float>>  lep_mass_reader(reader, "lep_mass");
  TTreeReaderValue<vector<float>>  lep_RelIsoNoFSR_reader(reader, "lep_RelIsoNoFSR");
  TTreeReaderValue<vector<int>>    lep_id_reader(reader, "lep_id");
  TTreeReaderValue<vector<int>>    lep_tightId_reader(reader, "lep_tightId");
  TTreeReaderValue<vector<int>>    lep_matchedR03_PdgId_reader(reader, "lep_matchedR03_PdgId");
  TTreeReaderValue<vector<int>>    lep_matchedR03_MomId_reader(reader, "lep_matchedR03_MomId");
  TTreeReaderValue<vector<int>>    lep_matchedR03_MomMomId_reader(reader, "lep_matchedR03_MomMomId");
  TTreeReaderValue<vector<double>> vtxLepFSR_BS_pt_reader(reader, "vtxLepFSR_BS_pt");
  TTreeReaderValue<vector<double>> vtxLepFSR_BS_eta_reader(reader, "vtxLepFSR_BS_eta");
  TTreeReaderValue<vector<double>> vtxLepFSR_BS_phi_reader(reader, "vtxLepFSR_BS_phi");
  TTreeReaderValue<vector<double>> vtxLepFSR_BS_mass_reader(reader, "vtxLepFSR_BS_mass");
  TTreeReaderValue<vector<float>>  lepFSR_pt_reader(reader, "lepFSR_pt");
  TTreeReaderValue<vector<float>>  lepFSR_eta_reader(reader, "lepFSR_eta");
  TTreeReaderValue<vector<float>>  lepFSR_phi_reader(reader, "lepFSR_phi");
  TTreeReaderValue<vector<float>>  lepFSR_mass_reader(reader, "lepFSR_mass");
  TTreeReaderValue<vector<int>>    lep_genindex_reader(reader, "lep_genindex");
  // Various mass4l values and associated errors.
  TTreeReaderValue<float>  mass4l_reader(reader, "mass4l");
  TTreeReaderValue<float>  mass4lErr_reader(reader, "mass4lErr");
  //
  TTreeReaderValue<float>  mass4l_vtx_reader(reader, "mass4l_vtx");
  TTreeReaderValue<float>  mass4lErr_vtx_reader(reader, "mass4lErr_vtx");
  //
  TTreeReaderValue<float>  mass4l_vtx_BS_reader(reader, "mass4l_vtx_BS");
  TTreeReaderValue<float>  mass4lErr_vtx_BS_reader(reader, "mass4lErr_vtx_BS");
  //
  TTreeReaderValue<float>  mass4lREFIT_reader(reader, "mass4lREFIT");
  TTreeReaderValue<float>  mass4lErrREFIT_reader(reader, "mass4lErrREFIT");
  //
  TTreeReaderValue<float>  mass4lREFIT_vtx_reader(reader, "mass4lREFIT_vtx");
  TTreeReaderValue<float>  mass4lErrREFIT_vtx_reader(reader, "mass4lErrREFIT_vtx");
  //
  TTreeReaderValue<float>  mass4lREFIT_vtx_BS_reader(reader, "mass4lREFIT_vtx_BS");
  TTreeReaderValue<float>  mass4lErrREFIT_vtx_BS_reader(reader, "mass4lErrREFIT_vtx_BS");
  // These have no associated error in Analyzer.
  TTreeReaderValue<float>  mass4l_vtxFSR_reader(reader, "mass4l_vtxFSR");
  TTreeReaderValue<float>  mass4l_vtxFSR_BS_reader(reader, "mass4l_vtxFSR_BS");
  TTreeReaderValue<float>  mass4l_noFSR_reader(reader, "mass4l_noFSR");
  //
  TTreeReaderValue<float>  D_bkg_kin_reader(reader, "D_bkg_kin");
  TTreeReaderValue<float>  D_bkg_kin_vtx_BS_reader(reader, "D_bkg_kin_vtx_BS");
  // Make variables which will attach to new branch.
  // ULong64_t Event;
  int finalState;
  bool passedZ1LSelection;
  bool passedZXCRSelection;
  float eventWeight;
  float k_qqZZ_qcd_M;
  float k_qqZZ_ewk;
  float met;
  float mass4l;
  vector<float> lep_pt;
  vector<float> lep_eta;
  vector<float> lep_phi;
  vector<float> lep_mass;
  vector<float> lep_RelIsoNoFSR;
  vector<int> lep_Hindex;
  // int lep_Hindex[4];
  vector<int> lep_id;
  vector<int> lep_tightId;
  vector<int> lep_matchedR03_PdgId;
  vector<int> lep_matchedR03_MomId;
  vector<int> lep_matchedR03_MomMomId;
  vector<double> vtxLepFSR_BS_pt;
  vector<double> vtxLepFSR_BS_eta;
  vector<double> vtxLepFSR_BS_phi;
  vector<double> vtxLepFSR_BS_mass;
  vector<float>  lepFSR_pt;
  vector<float>  lepFSR_eta;
  vector<float>  lepFSR_phi;
  vector<float>  lepFSR_mass;
  vector<int>    lep_genindex;
  float mass4l_noFSR;
  float mass4lErr;
  float mass4lREFIT;
  float mass4lREFIT_vtx;
  float mass4lErrREFIT;
  float mass4lErrREFIT_vtx;
  float mass4l_vtx;
  float mass4lErr_vtx;
  float mass4l_vtxFSR;
  float mass4l_vtx_BS;
  float mass4l_vtxFSR_BS;
  float mass4lErr_vtx_BS;
  float mass4lREFIT_vtx_BS;
  float mass4lErrREFIT_vtx_BS;
  float D_bkg_kin;
  float D_bkg_kin_vtx_BS;

  // Set vars to new branch.
  // newtree->Branch("Event", &Event);
  newtree->Branch("finalState", &finalState);
  newtree->Branch("passedZ1LSelection", &passedZ1LSelection);
  newtree->Branch("passedZXCRSelection", &passedZXCRSelection);
  newtree->Branch("eventWeight", &eventWeight);
  newtree->Branch("k_qqZZ_qcd_M", &k_qqZZ_qcd_M);
  newtree->Branch("k_qqZZ_ewk", &k_qqZZ_ewk);
  newtree->Branch("met", &met);
  newtree->Branch("mass4l", &mass4l);
  // Lepton kinematics.
  newtree->Branch("lep_Hindex", &lep_Hindex);
  newtree->Branch("lep_pt", &lep_pt);
  newtree->Branch("lep_eta", &lep_eta);
  newtree->Branch("lep_phi", &lep_phi);
  newtree->Branch("lep_mass", &lep_mass);
  newtree->Branch("lep_RelIsoNoFSR", &lep_RelIsoNoFSR);
  newtree->Branch("lep_id", &lep_id);
  newtree->Branch("lep_tightId", &lep_tightId);
  newtree->Branch("lep_matchedR03_PdgId", &lep_matchedR03_PdgId);
  newtree->Branch("lep_matchedR03_MomId", &lep_matchedR03_MomId);
  newtree->Branch("lep_matchedR03_MomMomId", &lep_matchedR03_MomMomId);
  newtree->Branch("vtxLepFSR_BS_pt", &vtxLepFSR_BS_pt);
  newtree->Branch("vtxLepFSR_BS_eta", &vtxLepFSR_BS_eta);
  newtree->Branch("vtxLepFSR_BS_phi", &vtxLepFSR_BS_phi);
  newtree->Branch("vtxLepFSR_BS_mass", &vtxLepFSR_BS_mass);
  newtree->Branch("lepFSR_pt", &lepFSR_pt);
  newtree->Branch("lepFSR_eta", &lepFSR_eta);
  newtree->Branch("lepFSR_phi", &lepFSR_phi);
  newtree->Branch("lepFSR_mass", &lepFSR_mass);
  newtree->Branch("lep_genindex", &lep_genindex);
  // m4l.
  newtree->Branch("mass4l_noFSR", &mass4l_noFSR);
  newtree->Branch("mass4lErr", &mass4lErr);
  newtree->Branch("mass4lREFIT", &mass4lREFIT);
  newtree->Branch("mass4lErrREFIT", &mass4lErrREFIT);
  newtree->Branch("mass4lErrREFIT_vtx", &mass4lErrREFIT_vtx);
  newtree->Branch("mass4lREFIT_vtx", &mass4lREFIT_vtx);
  newtree->Branch("mass4l_vtx",    &mass4l_vtx);
  newtree->Branch("mass4lErr_vtx", &mass4lErr_vtx);
  newtree->Branch("mass4l_vtxFSR", &mass4l_vtxFSR);
  newtree->Branch("mass4l_vtx_BS", &mass4l_vtx_BS);
  newtree->Branch("mass4l_vtxFSR_BS", &mass4l_vtxFSR_BS);
  newtree->Branch("mass4lErr_vtx_BS", &mass4lErr_vtx_BS);
  newtree->Branch("mass4lREFIT_vtx_BS", &mass4lREFIT_vtx_BS);
  newtree->Branch("mass4lErrREFIT_vtx_BS", &mass4lErrREFIT_vtx_BS);
  newtree->Branch("D_bkg_kin", &D_bkg_kin);
  newtree->Branch("D_bkg_kin_vtx_BS", &D_bkg_kin_vtx_BS);

  unsigned int eventCount = 0;
  unsigned int n_tot_Z1L = 0;
  unsigned int n_tot_ZXCR = 0;
  unsigned int n_tot_4P = 0;
  unsigned int n_leps;
  unsigned int n_muons;
  unsigned int n_tight;
  unsigned int n_iso;
  bool keep_event;
  // Begin iterating over the TTree.
  while (reader.Next()) {
    eventCount++;
    n_leps = 0;
    n_muons = 0;
    n_tight = 0;
    n_iso = 0;
    keep_event = false;

    if (eventCount % 1000000 == 0) {
    // if (eventCount % 100000 == 0) {
      std::cout << eventCount << "/" << n_tot_tree << " events read." << std::endl;
      // if (eventCount % 1000000 == 0) {break;}
    }

    //--- Event selection ---//
    // Only interested in events which go into Z+L, Z+LL, or 4P CRs.
    // 4P: Have exactly 4 tight and isolated leps (they look like 4 prompt).
    passedZ1LSelection = *passedZ1LSelection_reader;
    passedZXCRSelection = *passedZXCRSelection_reader;
    lep_id = (*lep_id_reader);
    lep_tightId = (*lep_tightId_reader);
    lep_RelIsoNoFSR = (*lep_RelIsoNoFSR_reader);

    if (do_Z1LSelection && passedZ1LSelection) {
      n_tot_Z1L += 1;
      keep_event = true;
      }
    if (do_ZXCRSelection && passedZXCRSelection) {
      n_tot_ZXCR += 1;
      keep_event = true;
      }
    if (do_4PSelection) {
      // Need exactly 4 leps.
      n_leps = lepFSR_pt_reader->size();
      if (n_leps == 4) {
        // All leps must be tight (pass BDT threshold).
        n_tight = std::accumulate(lep_tightId.begin(), lep_tightId.end(), 0);
        if (n_tight == 4) {
          // If there are any muons, make sure they pass isolation cut.
          for (unsigned int k=0; k < 4; k++) {
            if (abs(lep_id[k]) == 13) {
              n_muons += 1;
              // We have a muon. Now check its iso val.
              if (lep_RelIsoNoFSR[k] < 0.35) {
                n_iso += 1;
              }
            }
          }
          if (n_muons == n_iso) {
            n_tot_4P += 1;
            keep_event = true;
            }
        }
      }
    }
    if (!keep_event) continue;
    // Found an event worth keeping.

    // Store the values in the new branches: branch = reader_val    
    finalState = *finalState_reader;
    eventWeight = *eventWeight_reader;
    k_qqZZ_qcd_M = *k_qqZZ_qcd_M_reader;
    k_qqZZ_ewk = *k_qqZZ_ewk_reader;
    met = *met_reader;
    mass4l = *mass4l_reader;
    // Arrays must be dealt with differently.
    for (int k : lep_Hindex_reader) {
      lep_Hindex.push_back(k);
    }
    lep_pt = *lep_pt_reader;
    lep_eta = *lep_eta_reader;
    lep_phi = *lep_phi_reader;
    lep_mass = *lep_mass_reader;
    lep_matchedR03_PdgId = *lep_matchedR03_PdgId_reader;
    lep_matchedR03_MomId = *lep_matchedR03_MomId_reader;
    lep_matchedR03_MomMomId = *lep_matchedR03_MomMomId_reader;
    vtxLepFSR_BS_pt = *vtxLepFSR_BS_pt_reader;
    vtxLepFSR_BS_eta = *vtxLepFSR_BS_eta_reader;
    vtxLepFSR_BS_phi = *vtxLepFSR_BS_phi_reader;
    vtxLepFSR_BS_mass = *vtxLepFSR_BS_mass_reader;
    lepFSR_pt = *lepFSR_pt_reader;
    lepFSR_eta = *lepFSR_eta_reader;
    lepFSR_phi = *lepFSR_phi_reader;
    lepFSR_mass = *lepFSR_mass_reader;
    lep_genindex = *lep_genindex_reader;
    //
    mass4l_noFSR = *mass4l_noFSR_reader;
    mass4lErr = *mass4lErr_reader;
    mass4lREFIT = *mass4lREFIT_reader;
    mass4lREFIT_vtx = *mass4lREFIT_vtx_reader;
    mass4lErrREFIT = *mass4lErrREFIT_reader;
    mass4lErrREFIT_vtx = *mass4lErrREFIT_vtx_reader;
    mass4l_vtx = *mass4l_vtx_reader;
    mass4lErr_vtx = *mass4lErr_vtx_reader;
    mass4l_vtx_BS = *mass4l_vtx_BS_reader;
    mass4l_vtxFSR_BS = *mass4l_vtxFSR_BS_reader;
    mass4lErr_vtx_BS = *mass4lErr_vtx_BS_reader;
    mass4lREFIT_vtx_BS = *mass4lREFIT_vtx_BS_reader;
    mass4lErrREFIT_vtx_BS = *mass4lErrREFIT_vtx_BS_reader;
    //
    D_bkg_kin = *D_bkg_kin_reader;
    D_bkg_kin_vtx_BS = *D_bkg_kin_vtx_BS_reader;

    // Save all values of this event in TTree.
    newtree->Fill();

    lep_Hindex.clear();
  } // end event loop

  newtree->Write();
  cout << "New TTree saved to file:\n" << outfile << endl;
  cout << "Found " << n_tot_Z1L << " Z+L events (for fake rate studies)." << endl;
  cout << "Found " << n_tot_ZXCR << " Z+LL events (2P2F or 3P1F)." << endl;
  cout << "Found " << n_tot_4P << " tight, iso, 4-lep events (for signal region comparison)." << endl;
  cout << "Total events: " << n_tot_Z1L + n_tot_ZXCR + n_tot_4P << endl;
  return;
} // end function
