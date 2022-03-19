dct_finalstates_str2int = {
    "4mu" : 1,
    "4e" : 2,
    "2e2mu" : 3,
    "2mu2e" : 4,
    "4l" : 5,
}

dct_finalstates_latex = {
    "4mu" : r'4#mu',
    "4e" : r'4e',
    "2e2mu" : r'2e2#mu',
    "2mu2e" : r'2#mu2e',
    "4l" : r'4#ell',
}

dct_finalstates_int2str = {
    val : key for key, val in dct_finalstates_str2int.items()
    }