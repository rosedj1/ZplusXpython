MZ_PDG = 91.1876  # GeV

LUMI_INT_2016 = -1  # pb^{-1}
LUMI_INT_2017 = -1  # pb^{-1}
LUMI_INT_2018_Jake = 57750  # pb^{-1}
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
    'WZ'   : 4.9, #v1=4.9 (from MCM).
    'WZ-ext1-v2' : 4.9, #MCM=1.965,  # Elisa used this WZ sample.
    'WZ_vukasin' : 4.67,
    'ZZ'   : 1.325 # From MCM. # Vukasin=1.256
}

n_totevts_dataset_dct = {
    # 'Nickname' : n_evts in MC file. Obtained from `crab report -d <dir>`.
    'DY10'       : -1,  # Not yet analyzed.
    'DY50'       : 187531221,
    'TT'         : 63405000,
    'WZ'         : 10086433,  # v1.
    'WZ-ext1-v2' : 11117763,
    'WZ_vukasin' : 6739437,
    'ZZ'         : 96412000,
    'Data'       : 1,  # Can be anything.
}

n_sumgenweights_dataset_dct = {
    # 'Nickname' : sum of gen weights in MC file, sumWeights.GetBinContent(1).
    'DY10'       : -1,  # Not yet analyzed. Vukasin=37951928.0
    'DY50'       : 127085880.0, # Vukasin=99795992.0
    'TT'         : 62977964.0, # Vukasin=63667448.0
    'WZ'         : 6397150.0,  # v1.
    'WZ-ext1-v2' : 6967813.0,
    'WZ_vukasin' : 6739437,
    'ZZ'         : 95655496.0,  # Vukasin=97457264.0
    'Data'       : 1,  # Can be anything.
}