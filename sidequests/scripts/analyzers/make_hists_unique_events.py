import ROOT as rt
from HiggsMassMeasurement.Utils_ROOT.ROOT_classes import make_TH1F

infile_root = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/haddedfiles/elisa_unique_226events.root"
new_rootfile = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/hists/elisa_unique_226events.root"

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
for evt in t:
    n_leps = len(list(evt.lep_pt))
    h_dct["n_leps_per_event"].Fill(n_leps)

    if n_leps != 4:
        continue
    n_4lep_evts += 1

    for ct, (tid, lid, relisoNoFsr, pt) in enumerate(zip(
        evt.lep_tightId, evt.lep_id, evt.lep_RelIsoNoFSR, evt.lep_pt)
    ):
        h_dct[f"lep_tightId_{ct}"].Fill(tid)
        h_dct[f"lep_id_{ct}"].Fill(lid)
        h_dct[f"lep_RelIsoNoFSR_{ct}"].Fill(relisoNoFsr)
        h_dct[f"lep_pt_{ct}"].Fill(pt)

print(f"Number of 4-lep events: {n_4lep_evts}")
hist_val = h_dct["n_leps_per_event"].GetBinContent(5)  # 5th bin. Remember that 0 is underflow.
check_4leps = (n_4lep_evts == hist_val)
print(f"n_4leps counter agrees with the number found in hist: {check_4leps}")
print(f"check_4leps: {n_4lep_evts}")
print(f"hist_val:    {hist_val}")

print(f"Saving hists in new root file:\n{new_rootfile}")
newfile = rt.TFile.Open(new_rootfile, "recreate")
for h in h_dct.values():
    h.Write()
newfile.Close()
# t.Scan("passedZXCRSelection:nisoleptons:lep_tightId:lep_id:lep_RelIsoNoFSR")