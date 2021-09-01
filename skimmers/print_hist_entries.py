"""Does hist.GetEntries() for all hists in the input root file.
Pass in the input root file as first argument:
`python this_script.py <file>`
"""

import ROOT
import sys

infile = sys.argv[1]
f = ROOT.TFile(infile)
key_ls = list(f.GetListOfKeys())
name_ls = [k.GetName() for k in key_ls]
# Find max number of chars among all names.
longest_name = int(max([len(name) for name in name_ls]))
for name in name_ls:
    hist = f.Get(name)
    print(f"{name:<{longest_name}}: {hist.GetEntries()}")