MZ_PDG = 91.1876

LUMI_INT_2016 = -1  # pb^{-1}
LUMI_INT_2017 = -1  # pb^{-1}
LUMI_INT_2018_Jake = 57400  # pb^{-1}
LUMI_INT_2018_Vukasin = 59700  # pb^{-1}
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsZZ4lRunIILegacy#2018
LUMI_INT_2018_TWiki = 59740  # pb^{-1}

xs_dct = {
    'DY10' : 18610.0,
    'DY50' : 6225.4,
    'TT'   : 87.31,
    'WZ'   : 4.67,
    'ZZ'   : 1.256
}

n_totevts_dataset_dct = {
    # 'Nickname' : n_evts in MC file. Obtained from `crab report -d <dir>`.
    'DY10' : -1,
    'DY50' : 187531221,
    'TT'   : 63405000,
    'WZ'   : 10086433,
    'ZZ'   : 96412000,
    'Data' : 1,  # Can be anything.
}
