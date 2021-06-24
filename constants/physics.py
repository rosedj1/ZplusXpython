MZ_PDG = 91.1876

LUMI_INT_2016 = -1  # pb^{-1}
LUMI_INT_2017 = -1  # pb^{-1}
LUMI_INT_2018_Jake = 57400  # pb^{-1}
LUMI_INT_2018_Vukasin = 59700  # pb^{-1}
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsZZ4lRunIILegacy#2018
LUMI_INT_2018_TWiki = 59740  # pb^{-1}

xs_dct = {
    # MCM xs vals obtained by going to:
    # https://cms-pdmv.cern.ch/mcm/ > Request > Output Dataset >
    # Search for your data set by providing the data set name.
    # Under 'PrepId' column, copy the name of the file.
    # Under 'Dataset name' column, click on the icon to the right of the name
    # of the data set (it looks like a file explorer).
    # Show all results (bottom-righthand corner).
    # Search (Ctrl-F) for the PrepId.
    # Even if a few options are found, they should all have the same LHEGS
    # file. Click this LHEGS file name.
    # > Select View > Generator parameters.
    # The cross section is in the 'Generator Parameters' column to the right.
    'DY10' : 18610.0,
    'DY50' : 7181, # Vukasin=6225.4,
    'TT'   : 72.1, # Vukasin=87.31,
    'WZ'   : 4.9, # From MCM. # Vukasin=4.67,
    'ZZ'   : 1.325 # From MCM. # Vukasin=1.256
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
