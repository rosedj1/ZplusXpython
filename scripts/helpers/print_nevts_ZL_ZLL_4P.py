
"""
Print the number of events which:
- passedZ1LSelection
- passedZXCRSelection
- pass 4 tight, isolated leptons.

Finally check that the sum of events is equal to the total num of events.
"""
import ROOT
import sys

infile = sys.argv[1]
f = ROOT.TFile(infile)
t = f.Get("passedEvents")

def check_4P_event(event):
    """Return True if `event` has 4 tight, isolated leptons."""
    if event.passedZ1LSelection:
        return False
    if event.passedZXCRSelection:
        return False
    if len(event.lep_pt) != 4:
        return False
    if sum(list(event.lep_tightId)) != 4:
        return False
    # Make sure all muons pass isolation cut.
    for lid, liso in zip(event.lep_id, event.lep_RelIsoNoFSR):
        if (abs(lid) == 13):
            if (liso >= 0.35):
                return False
    return True

n_tot = t.GetEntries()
n_Z1L = 0
n_ZXCR = 0 
n_4P = 0 
n_bad_lepHindex = 0 
n_good_lepHindex = 0 

for ct, evt in enumerate(t, 1):
    if (ct % int(1E5)) == 0:
        print(f"Event {ct}/{n_tot}")
    if evt.passedZ1LSelection: 
        n_Z1L += 1 
    if evt.passedZXCRSelection: 
        n_ZXCR += 1 
    if check_4P_event(evt): 
        n_4P += 1 
        if -1 in list(evt.lep_Hindex): 
            n_bad_lepHindex += 1 
        else: 
            n_good_lepHindex += 1 

print(f"n_good_lepHindex = {n_good_lepHindex}") 
print(f"n_bad_lepHindex = {n_bad_lepHindex}") 
print(f"n_Z1L = {n_Z1L}, n_ZXCR = {n_ZXCR}, n_4P = {n_4P}") 
print((n_Z1L + n_ZXCR + n_4P) == t.GetEntries())