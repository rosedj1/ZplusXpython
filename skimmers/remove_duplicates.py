# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
import ROOT as rt
import sys
sys.path.append("/blue/avery/rosedj1/")
from HiggsMassMeasurement.Utils_Python.Utils_Files import check_overwrite

infile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/Data2018_Duplicates.root"
outfile = "/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/Data/2018/fullstats/ZL_ZLL_4P_CR/noduplicates/Data2018_NoDuplicates_doublecheck.root"
overwrite = 0

f = rt.TFile(infile)
t = f.Get("passedEvents")
n_tot = t.GetEntries()
print(f"File opened:\n{infile}")

check_overwrite(outfile, overwrite=overwrite)
newfile = rt.TFile(outfile, "recreate")

newtree = t.CloneTree(0)  # Clone 0 entries.
print("TTree cloned. Filled with 0 entries.")

num_duplicates = 0
event_set = set()
for ct, evt in enumerate(t):
    if (ct % 5000) == 0:
        print(f"Event {ct}/{n_tot}.")

    evt.GetEntry(ct)
    # key = (evt.Run, evt.LumiSect, evt.Event, )
    key = f"{evt.Run}_{evt.LumiSect}_{evt.Event}"

    # num_to_break = 10
    # if ct == num_to_break:
    #     break

    if key in event_set:
        num_duplicates += 1
        continue
    else:
        newtree.Fill()
        event_set.add(key)

newtree.Write()
newfile.Close()

print(f"New TTree written to file:\n{outfile}")
print(f"Number of duplicates found: {num_duplicates}")