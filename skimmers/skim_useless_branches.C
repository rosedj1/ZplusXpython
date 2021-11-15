/**
 * PURPOSE: Copy a TTree to a new root file, but only keep certain branches.
 * AUTHOR: Jake Rosenzweig, jake.rose@cern.ch
 * CREATED: 2021-11-12
 * UPDATED:
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
  TString infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/SingleMuon.root";
  TString outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/SingleMuon_skimmed.root";
  TString intree = "Ana/passedEvents";
  unsigned int n_evts_to_keep = -1;  // Use -1 for "all".
  bool verbose = true;

  TFile *tf = new TFile(infile, "READ");
  TTree *tree = (TTree*)tf->Get(intree);
  cout << "Successfully opened file:\n" << infile << endl;
  cout << "TTree has " << tree->GetEntries() << " entries." << endl;
  // cout << "Saving " << n_evts_to_keep << "(" << n_evts_to_keep/tree->GetEntries() << ")" << " entries." << endl;

  vector<TString> branches{
    "Run",
    "Event",
    "LumiSect",
    "nVtx",
    "nInt",
    "finalState",
    "triggersPassed",
    "passedTrig",
    "passedFullSelection",
    "passedZ4lSelection",
    "passedQCDcut",
    "passedZ1LSelection",
    "passedZ4lZ1LSelection",
    "passedZ4lZXCRSelection",
    "passedZXCRSelection",
    "nZXCRFailedLeptons",
    "k_ggZZ",
    "k_qqZZ_qcd_dPhi",
    "k_qqZZ_qcd_M",
    "k_qqZZ_qcd_Pt",
    "k_qqZZ_ewk",
    "qcdWeights",
    "nnloWeights",
    "pdfWeights",
    "pileupWeight",
    "dataMCWeight",
    "eventWeight",
    "prefiringWeight",
    "lep_d0BS",
    "lep_d0PV",
    "lep_numberOfValidPixelHits",
    "lep_trackerLayersWithMeasurement",
    "lep_p",
    "lep_ecalEnergy",
    "lep_isEB",
    "lep_isEE",
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
    "singleBS_FSR_Lep_pt",
    "singleBS_FSR_Lep_eta",
    "singleBS_FSR_Lep_phi",
    "singleBS_FSR_Lep_mass",
    "vtxLepFSR_BS_pt",
    "vtxLepFSR_BS_eta",
    "vtxLepFSR_BS_phi",
    "vtxLepFSR_BS_mass",
    "vtxLepFSR_pt",
    "vtxLepFSR_eta",
    "vtxLepFSR_phi",
    "vtxLepFSR_mass",
    "singleBS_RecoLep_pt",
    "singleBS_RecoLep_ptError",
    "singleBS_RecoLep_eta",
    "singleBS_RecoLep_phi",
    "singleBS_RecoLep_mass",
    "singleBS_RecoLep_d0",
    "vtxRecoLep_BS_pt",
    "vtxRecoLep_BS_ptError",
    "vtxRecoLep_BS_eta",
    "vtxRecoLep_BS_phi",
    "vtxRecoLep_BS_mass",
    "vtxRecoLep_BS_d0",
    "vtxRecoLep_pt",
    "vtxRecoLep_ptError",
    "vtxRecoLep_eta",
    "vtxRecoLep_phi",
    "vtxRecoLep_mass",
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
    "lep_missingHits",
    "lep_mva",
    "lep_ecalDriven",
    "lep_tightId",
    "lep_tightIdSUS",
    "lep_tightIdHiPt",
    "lep_Sip",
    "lep_IP",
    "lep_isoNH",
    "lep_isoCH",
    "lep_isoPhot",
    "lep_isoPU",
    "lep_isoPUcorr",
    "lep_RelIso",
    "lep_RelIsoNoFSR",
    "lep_MiniIso",
    "lep_ptRatio",
    "lep_ptRel",
    "nisoleptons",
    "H_pt",
    "H_eta",
    "H_phi",
    "H_mass",
    "H_noFSR_pt",
    "H_noFSR_eta",
    "H_noFSR_phi",
    "H_noFSR_mass",
    "mass4l",
    "mass4l_noFSR",
    "mass4lErr",
    "mass4lREFIT",
    "mass4lErrREFIT",
    "massZ1REFIT",
    "massZ2REFIT",
    "mass4l_singleBS",
    "mass4l_singleBS_FSR",
    "mass4lErr_singleBS",
    "mass4lREFIT_singleBS",
    "mass4lErrREFIT_singleBS",
    "massZ1REFIT_singleBS",
    "massZ2REFIT_singleBS",
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
    "mass4mu",
    "mass4e",
    "mass2e2mu",
    "pT4l",
    "eta4l",
    "phi4l",
    "rapidity4l",
    "massZ_vtx_chi2_BS",
    "massZ_vtx_chi2",
    "mass2l_vtx",
    "mass2l_vtx_BS",
    "Z_pt",
    "Z_eta",
    "Z_phi",
    "Z_mass",
    "Z_noFSR_pt",
    "Z_noFSR_eta",
    "Z_noFSR_phi",
    "Z_noFSR_mass",
    "Z_Hindex",
    "massZ1",
    "massErrH_vtx",
    "massH_vtx_chi2_BS",
    "massH_vtx_chi2",
    "massZ1_Z1L",
    "massZ2",
    "pTZ1",
    "pTZ2",
    "met",
    "nFSRPhotons",
    "allfsrPhotons_dR",
    "allfsrPhotons_iso",
    "allfsrPhotons_pt",
    "fsrPhotons_lepindex",
    "fsrPhotons_pt",
    "fsrPhotons_pterr",
    "fsrPhotons_eta",
    "fsrPhotons_phi",
    "fsrPhotons_dR",
    "fsrPhotons_iso",
    "passedFiducialSelection",
    "me_qqZZ_MCFM",
    "bkg_m4l",
    "D_bkg_kin",
    "D_bkg_kin_vtx_BS",
    "D_bkg",
    "D_bkg_VBFdec",
    "D_bkg_VHdec",
  };

  // Turn off all branches, then manually turn on the ones to keep.
  tree->SetBranchStatus("*",0);//1);

  if (verbose) cout << "Saving branches:" << endl;
  for (auto & branch : branches) {
    if (verbose) cout << "  " << branch << endl;
    tree->SetBranchStatus(branch, 1);
  }

  TFile *tf_out = new TFile(outfile, "RECREATE");
  TTree *newtree = tree->CloneTree(n_evts_to_keep);

  newtree->Write();
  cout << "New TTree saved to file:\n" << outfile << endl;
  return;
} // end function
