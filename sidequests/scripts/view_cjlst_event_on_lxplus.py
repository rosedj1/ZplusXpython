from ROOT import TFile
from enum import IntEnum
from numpy import array

from sidequests.funcs.evt_comparison import print_evt_info_bbf, analyze_single_evt

infile_matteo_data2018 = "/eos/cms/store/group/phys_higgs/cmshzz4l/cjlst/RunIILegacy/200430_LegacyRun2/Data_2018/AllData/ZZ4lAnalysis.root"
f = TFile.Open(infile_matteo_data2018)
t = f.Get("CRZLLTree/candTree")

class CjlstFlag(IntEnum):
    CR3P1F = 8388608
    CR2P2F = 4194304
    CRLLss = 2097152
    
if __name__ == '__main__':
    analyze_single_evt(t, 321305, 1003, 1613586694, fw="cjlst")
    print_evt_info_cjlst(t, 32366)