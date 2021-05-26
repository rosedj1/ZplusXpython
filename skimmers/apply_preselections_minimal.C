/**
 * PURPOSE: Skim a root file produced from the UFHZZ4L Analyzer.
 * NOTES:
 * - Useful for reducible background studies.
 * - Minimal branches are kept. No VX+BS info.
 * - Very little selection is implemented (just looking for events in the Z+L
 *   and Z+LL control regions).
 * AUTHOR: Jake Rosenzweig, jake.rose@cern.ch
 * CREATED: 2021-05-20, happy birthday, Sheldoni!
 * UPDATED: 2021-05-26
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

using namespace std;

void apply_preselections_minimal(){

  TString filename = "FILENAME"; //"WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018.root";

  TString infile1 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/" + filename;
  // TString infile1 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/DoubleMuon_2018.root";
  // TString infile2 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/EGamma_2018.root";
  // TString infile3 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/MuonEG_2018.root";
  // TString infile4 = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/SingleMuon_2018.root";

  // TString outfile_path = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/fullstats/Data_2018_ZL_ZLL_CRs.root";
  TString outfile_path = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/ZL_ZLL_CR/" + filename;

  TFile *outfile = new TFile(outfile_path, "RECREATE");
  TTree *newtree = new TTree("passedEvents","passedEvents");

  TString intree = "Ana/passedEvents";
  TChain *cc = new TChain(intree);

  cc->Add(infile1);
  // cc->Add(infile2);
  // cc->Add(infile3);
  // cc->Add(infile4);

  TTreeReader reader(cc);
  // Assign TTreeReader to a branch on old tree.
  TTreeReaderValue<bool> passedZ1LSelection_reader(reader, "passedZ1LSelection");
  TTreeReaderValue<bool> passedZXCRSelection_reader(reader, "passedZXCRSelection");
  TTreeReaderValue<float> eventWeight_reader(reader, "eventWeight");
  TTreeReaderValue<float> k_qqZZ_qcd_M_reader(reader, "k_qqZZ_qcd_M");
  TTreeReaderValue<float> k_qqZZ_ewk_reader(reader, "k_qqZZ_ewk");
  TTreeReaderValue<float> met_reader(reader, "met");
  TTreeReaderValue<float> mass4l_reader(reader, "mass4l");
  TTreeReaderArray<int> lep_Hindex_reader(reader, "lep_Hindex");
  TTreeReaderValue<vector<float>> lep_pt_reader(reader, "lep_pt");
  TTreeReaderValue<vector<float>> lep_eta_reader(reader, "lep_eta");
  TTreeReaderValue<vector<float>> lep_phi_reader(reader, "lep_phi");
  TTreeReaderValue<vector<float>> lep_mass_reader(reader, "lep_mass");
  TTreeReaderValue<vector<float>> lep_RelIsoNoFSR_reader(reader, "lep_RelIsoNoFSR");
  TTreeReaderValue<vector<int>> lep_id_reader(reader, "lep_id");
  TTreeReaderValue<vector<int>> lep_tightId_reader(reader, "lep_tightId");
  TTreeReaderValue<vector<int>> lep_matchedR03_PdgId_reader(reader, "lep_matchedR03_PdgId");
  TTreeReaderValue<vector<int>> lep_matchedR03_MomId_reader(reader, "lep_matchedR03_MomId");
  TTreeReaderValue<vector<int>> lep_matchedR03_MomMomId_reader(reader, "lep_matchedR03_MomMomId");

  // Make variables which will attach to new branch.
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

  // Set vars to new branch.
  newtree->Branch("passedZ1LSelection", &passedZ1LSelection);
  newtree->Branch("passedZXCRSelection", &passedZXCRSelection);
  newtree->Branch("eventWeight", &eventWeight);
  newtree->Branch("k_qqZZ_qcd_M", &k_qqZZ_qcd_M);
  newtree->Branch("k_qqZZ_ewk", &k_qqZZ_ewk);
  newtree->Branch("met", &met);
  newtree->Branch("mass4l", &mass4l);
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

  unsigned int eventCount = 0;
  // Begin iterating over the TTree.
  while (reader.Next()) {
    eventCount++;
    if (eventCount % 1000000 == 0) {
      std::cout << eventCount << " events read." << std::endl;
    }

    //--- Event selection ---//
    // if (*gen_HX_b1_recojet_pt < pt_threshold) continue;
    // if (abs(*gen_HX_b1_recojet_eta) > eta_threshold) continue;

    // Store the values in the new branches: branch = reader_val
    passedZ1LSelection = *passedZ1LSelection_reader;
    passedZXCRSelection = *passedZXCRSelection_reader;

    // Must pass either passedZ1LSelection or passedZXCRSelection.
    if (!passedZ1LSelection && !passedZXCRSelection) continue;

    eventWeight = *eventWeight_reader;
    k_qqZZ_qcd_M = *k_qqZZ_qcd_M_reader;
    k_qqZZ_ewk = *k_qqZZ_ewk_reader;
    met = *met_reader;
    mass4l = *mass4l_reader;
    // Arrays must be dealt with separately.
    for (int k : lep_Hindex_reader) {
      lep_Hindex.push_back(k);
    }
    // lep_Hindex = *lep_Hindex_reader;
  // lep_Hindex[0] = lep_Hindex_reader[0];  // Changing this from int[4] to vector<int>.
  // lep_Hindex[1] = lep_Hindex_reader[1];  // Changing this from int[4] to vector<int>.
  // lep_Hindex[2] = lep_Hindex_reader[2];  // Changing this from int[4] to vector<int>.
  // lep_Hindex[3] = lep_Hindex_reader[3];  // Changing this from int[4] to vector<int>.
    lep_pt = *lep_pt_reader;
    lep_eta = *lep_eta_reader;
    lep_phi = *lep_phi_reader;
    lep_mass = *lep_mass_reader;
    lep_RelIsoNoFSR = *lep_RelIsoNoFSR_reader;
    lep_id = *lep_id_reader;
    lep_tightId = *lep_tightId_reader;
    lep_matchedR03_PdgId = *lep_matchedR03_PdgId_reader;
    lep_matchedR03_MomId = *lep_matchedR03_MomId_reader;
    lep_matchedR03_MomMomId = *lep_matchedR03_MomMomId_reader;

    // Save all values of this event in TTree.
    newtree->Fill();

    lep_Hindex.clear();
  } // end event loop
  
  newtree->Write();
  cout << "New TTree saved to file:\n" << outfile_path << endl;

  return;
} // end function
