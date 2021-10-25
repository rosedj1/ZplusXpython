"""Make kinematic distributions of a root file produced from the UF HZZ Ana.
------------------------------------------------------------------------------
SYNTAX:  python3 this_script.py
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-22
UPDATED: 2021-10-25
------------------------------------------------------------------------------
"""
import os
import ROOT as rt
from HiggsMassMeasurement.Utils_ROOT.ROOT_classes import make_TH1F
from HiggsMassMeasurement.Utils_Python.Utils_Files import check_overwrite

overwrite = 1
make_pdf = 0
make_new_rootfile = 0
start_dir = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/"

infile_root = os.path.join(start_dir, "haddedfiles/elisa_unique_353events.root")
new_rootfile = os.path.join(start_dir, "hists/elisa_unique_353events_kinemhists_uselep_Hindex.root")

def make_dct_of_hists_perlep(branches):
    """Return a dict of empty TH1F's.

    key:val format -> {"branch_name_2" : TH1F}

    The '2' indicates that the second lepton from the event fills this hist.
    That's what the 'perlep' part of the function means.

    Example branches:
    - "lep_tightId"
    - "lep_id"
    """
    pass
    # d = {}
    # for br in branches:
    #     for lep_n in range(4):
    #         key = f"{br}_{lep_n}"
    #         d[key] = make_TH1F(f"h_{key}", title=key, n_bins=2,
    #                 xlabel=key, x_min=0, x_max=2,
    #                 ylabel=None, units=None)

    #         key = f"lep_id_{lep_n}"
    #         d[key] = make_TH1F(f"h_{key}", title=key, n_bins=2,
    #                 xlabel=key, x_min=0, x_max=2,
    #                 ylabel=None, units=None)
    # return d

def main():
    check_overwrite(new_rootfile, overwrite=overwrite)
    f = rt.TFile(infile_root)
    t = f.Get("Ana/passedEvents")
    print(f"Opened TTree in file:\n{infile_root}")

    branches = (
        "passedZXCRSelection",
        "nisoleptons",
    )

    branches_per_lep = (
        "lep_tightId",
        "lep_id",
        "lep_RelIsoNoFSR"
    )

    print("Creating hist dict.")
    h_dct = {}
    for lep_n in range(4):
        key = f"lep_tightId_{lep_n}"
        h_dct[key] = make_TH1F(f"h_{key}", title=key, n_bins=2,
                xlabel=key, x_min=0, x_max=2,
                ylabel=None, units=None)

        key = f"lep_id_{lep_n}"
        h_dct[key] = make_TH1F(f"h_{key}", title=key, n_bins=39,
                xlabel=key, x_min=-19.5, x_max=19.5,
                ylabel=None, units=None)

        key = f"lep_RelIsoNoFSR_{lep_n}"
        h_dct[key] = make_TH1F(f"h_{key}", title=key, n_bins=40,
                xlabel=key, x_min=0, x_max=4,
                ylabel=None, units=None)

        key = f"lep_pt_{lep_n}"
        h_dct[key] = make_TH1F(f"h_{key}", title=key, n_bins=100,
                xlabel=key, x_min=0, x_max=200,
                ylabel=None, units="GeV")
        
    key = "n_leps_per_event"
    h_dct[key] = make_TH1F(f"h_{key}", title=key, n_bins=10,
                xlabel=key, x_min=0, x_max=10,
                ylabel=None, units=None)

    for h in h_dct.values():
        h.Sumw2()
        h.StatOverflows(True)

    print("Looping over events.")
    n_4lep_evts = 0
    for ct, evt in enumerate(t):
        if ct == 10: break
        n_leps = len(list(evt.lep_pt))
        h_dct["n_leps_per_event"].Fill(n_leps)

        if n_leps != 4:
            continue
        n_4lep_evts += 1

        for lep_index in range(4):
            index_in_vec = evt.lep_Hindex[lep_index]
            print(f"lep_index: {lep_index}")
            print(f"index_in_vec: {index_in_vec}")

            h_dct[f"lep_tightId_{lep_index}"].Fill(evt.lep_tightId[index_in_vec])
            h_dct[f"lep_id_{lep_index}"].Fill(evt.lep_id[index_in_vec])
            h_dct[f"lep_RelIsoNoFSR_{lep_index}"].Fill(evt.lep_RelIsoNoFSR[index_in_vec])
            h_dct[f"lep_pt_{lep_index}"].Fill(evt.lep_pt[index_in_vec])

    print(f"Number of 4-lep events: {n_4lep_evts}")
    hist_val = h_dct["n_leps_per_event"].GetBinContent(5)  # 5th bin. Remember that 0 is underflow.
    check_4leps = (n_4lep_evts == hist_val)
    print(f"n_4leps counter agrees with the number found in hist: {check_4leps}")
    print(f"check_4leps: {n_4lep_evts}")
    print(f"hist_val:    {hist_val}")

    if make_new_rootfile:
        print(f"Saving hists in new root file:\n{new_rootfile}")
        newfile = rt.TFile.Open(new_rootfile, "recreate")
        for h in h_dct.values():
            h.Write()
        newfile.Close()

    outfile = infile_root.replace(".root", ".pdf")

    if make_pdf:
        c = rt.TCanvas()
        c.Print(f"{outfile}[")
        for h in h_dct.values():
            new_max = h.GetMaximum()
            h.GetYaxis().SetRangeUser(0, new_max * 1.2)
            name = h.GetName()
            if ("pt" in name) or ("RelIso" in name):
                h.Draw("hist")
            else:
                h.Draw("hist text")
            c.Print(outfile)
        c.Print(f"{outfile}]")

if __name__ == '__main__':
    main()