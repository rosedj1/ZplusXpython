#include "TTree.h"
#include "TFile.h"
#include <vector>

using namespace std;

int remove_duplicates() {

    bool dup_found;
    ULong64_t Run;
    ULong64_t LumiSect;
    ULong64_t Event;
    TString key;
    unsigned int n_evts_max;
    unsigned int num_duplicates = 0;

    TString infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/Data2018_Duplicates.root";
    TString outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/Data2018_NoDuplicates_fromcpp.root";

    TFile* tfile = new TFile(infile);
    TTree* tree = (TTree*)tfile->Get("passedEvents");

    TFile* new_tfile = new TFile(outfile, "recreate");
    TTree* new_tree = tree->CloneTree(0);

    // tree->SetBranchStatus("*", 0);
    tree->SetBranchStatus("Run", 1);
    tree->SetBranchStatus("LumiSect", 1);
    tree->SetBranchStatus("Event", 1);

    tree->SetBranchAddress("Run", &Run);
    tree->SetBranchAddress("LumiSect", &LumiSect);
    tree->SetBranchAddress("Event", &Event);

    n_evts_max = tree->GetEntries();
    // Vector to hold keys of unique events: `Run:LumiSect:Event`
    vector<TString> key_vec;
    // TString key_arr[n_evts_max];

    // Event loop.
    for (unsigned int k = 0 ; k < n_evts_max; k++) {
    // for (unsigned int k; k < n_evts_max; k++) {
        if ((k % 1000) == 0) {
            cout << "Event: " << k+1 << "/" << n_evts_max << endl;
        }
        dup_found = false;

        tree->GetEntry(k);

        key = Form("%llu:%llu:%llu", Run, LumiSect, Event);
        // TString* arr_p = std::find(std::begin(key_arr), std::end(key_arr), key);

        // If the key is already in the array, this is a duplicate event; skip it!
        for (const auto &item : key_vec) {
            if (item == key) {
                // Duplicate found.
                num_duplicates += 1;
                printf("Duplicate found in for loop: %d\n", num_duplicates);
                dup_found = true;
                break;
            }
        }
        /*
        //--- Array-based method ---//
        // Also skip if an element of the array is blank
        // (this is part of the array which has not yet been filled).
        for (unsigned int j = 0; j < n_evts_max; j++) {
            if (key_arr[j] == "") {
                // Reached unexplored part of array.
                break;
            }
            */
        // }
        if (dup_found) {
            continue;
        }
        // New event. Load it into the new tree and record it in the array.
        new_tree->Fill();
        key_vec.push_back(key);
    }

    printf("Number of duplicates found: %i\n", num_duplicates);
    new_tree->Write();
    new_tfile->Close();

    cout << "New TTree written to:\n" << outfile << endl;
    return 0;
}