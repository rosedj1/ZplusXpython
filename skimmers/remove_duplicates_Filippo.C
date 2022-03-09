#include <iostream>
#include <set>
#include <TString.h>
#include <TFile.h>
#include <TTree.h>

void remove_duplicates_Filippo() {
    // path / name of root file
    TString prefix = "/cmsuf/data/store/user/t2/users/rosedj1/Samples/skim2L_UL/Data/2017/fullstats/MuonEG-UL2017_MiniAODv2";
    TString filename = prefix+".root";
    TString pathToTree = "Ana/passedEvents";

    std::cout<<filename<<std::endl;

    TFile *oldfile = new TFile(filename);
    TTree *oldtree = (TTree*)oldfile->Get(pathToTree);
//    oldfile->cd("Ana");
    
//TTree *oldtree = (TTree*)gDirectory->Get("passedEvents");
// TTree *oldtree = (TTree*)oldfile->Get("passedEvents");

    Long64_t nentries = oldtree->GetEntries();
    std::cout<<nentries<<" total entries."<<std::endl;
    ULong64_t Run, LumiSect, Event;
    bool passedZ4lSelection;
    oldtree->SetBranchAddress("Run",&Run);
    oldtree->SetBranchAddress("LumiSect",&LumiSect);
    oldtree->SetBranchAddress("Event",&Event);

    //Create a new file + a clone of old tree in new file
    TFile *newfile = new TFile(
            prefix+"_noDuplicates.root"
            ,"recreate");
    TTree *newtree = oldtree->CloneTree(0);

    std::set<TString> runlumieventSet;
    int nremoved = 0;
    for (Long64_t i=0;i<nentries; i++) {
        if (i%250000==0) std::cout<<i<<"/"<<nentries<<std::endl;
        oldtree->GetEntry(i);
if(Run==305821 && Event==455992205 && LumiSect==282)
	std::cout<<"trovato l'event"<<std::endl;
        TString s_Run  = std::to_string(Run);
        TString s_Lumi = std::to_string(LumiSect);
        TString s_Event = std::to_string(Event);
        TString runlumievent = s_Run+":"+s_Lumi+":"+s_Event;
        
        if (runlumieventSet.find(runlumievent)==runlumieventSet.end()) {
            runlumieventSet.insert(runlumievent);
            newtree->Fill();
				//if(Run==305821 && Event==455992205 && LumiSect==282)
				//	std::cout<<"\t\t - lo sto prendendo"<<std::endl;
        } else {
            nremoved++;
				//if(Run==305821 && Event==455992205 && LumiSect==282)
				//        std::cout<<"\t\t - lo sto scartando"<<std::endl;
        }
        //if (passedZ4lSelection) newtree->Fill();
    }

    std::cout<<nremoved<<" duplicates."<<std::endl;
    newtree->Print();
    newtree->AutoSave();
    //delete oldfile;
    delete newfile;
}
