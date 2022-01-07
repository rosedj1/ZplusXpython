import ROOT as rt
import sys
import os
from glob import glob

# file_ls = sys.argv[1:]
file_ls = glob("/cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/Samples/skim2L/MC/fullstats/*.root")

for infile in file_ls:
    f = rt.TFile(infile)
    h = f.Get('Ana/sumWeights')
    print(f'{os.path.basename(infile)}: {h.GetBinContent(1)}')
