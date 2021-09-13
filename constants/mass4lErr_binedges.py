finalstate_dct = {
    "4mu" : 1,
    "4e" : 2,
    "2e2mu" : 3,
    "2mu2e" : 4
}

class RelMassErrBinEdges:

    def __init__(self):
        self.alphabet_indextup_dct = self.make_alphabet_to_binedge_index_dct()
        self.relmass4lErr_binedge_dct = {
            # 4l final state code : bin edge values
            # WARNING: Filippo is inconsistent about using final state codes!
            # The keys below are 1 less than the typical values.
            # Frequently '1' means '4mu' but now '0' means '4mu'.
            0 : [          # Bin A is the
                0.0000000, # <== 0th and
                0.0056000, # <== 1st bin edges.
                0.0061500,
                0.0067125,
                0.0072500,
                0.0078000,
                0.0084250,
                0.0092375,
                0.0105875,
                0.3000000
                ],
            1 : [
                0.0000000,
                0.0109250,
                0.0125250,
                0.0141625,
                0.0160250,
                0.0181750,
                0.0205750,
                0.0232750,
                0.0269500,
                0.3000000
                ],
            2 : [
                0.0000000,
                0.0086250,
                0.0097250,
                0.0106500,
                0.0116875,
                0.0130500,
                0.0148625,
                0.0180500,
                0.0225125,
                0.3000000
                ],
            3 : [
                0.0000000,
                0.0078750,
                0.0088125,
                0.0097875,
                0.0109250,
                0.0122875,
                0.0138250,
                0.0156375,
                0.0183250,
                0.3000000
                ],
        }

    def make_alphabet_to_binedge_index_dct(self, letters='A B C D E F G H I'):
        """Return a dict like:
            {
                'A' : (0, 1),
                'B' : (1, 2),
                'C' : (2, 3),
                ...
            }
        """
        # Make alphabet keys.
        alphabet_ls = letters.split()
        # alphabet_ls = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()
        indices = list(range( len(alphabet_ls) + 1 ))
        # Make values (2-elem tuple) by threading indices together.
        ls_of_tup_of_indices = zip(indices[:-1], indices[1:])
        return dict(zip(alphabet_ls, ls_of_tup_of_indices))

    def get_edges_mass4lErr_bin(self, finalstate_dct, fs_str=None, fs_int=None, relm4lErr_bin_code=""):
        """
        Return binedges (2-tup) corresponding to final state and relmasserr
        code.
        
        Parameters
        ----------
        fs_str : str
            Final state of 4-leptons: "4mu", "4e", "2e2mu", "2mu2e"
        fs_int : int
            The code corresponding to the final state:
                "4mu"   : 1,
                "4e"    : 2,
                "2e2mu" : 3,
                "2mu2e" : 4
        relm4lErr_bin_code : str
            The code corresponding to the relative mass error bin.
            Accepts: "A", "B", ..., "I"
        """
        using_str_code = fs_str is not None
        using_int_code = fs_int is not None
        assert not (using_str_code and using_int_code)
        assert using_str_code or using_int_code
        if using_str_code:
            fs_int = finalstate_dct[fs_str]
        else:
            assert fs_int in (1, 2, 3, 4)
        fs_int -= 1  # Must subtract 1 to match the weird keys.
        all_binedges_for_fs = self.relmass4lErr_binedge_dct[fs_int]
        ndx1, ndx2 = self.alphabet_indextup_dct[relm4lErr_bin_code]
        binedge_tup = (all_binedges_for_fs[ndx1], all_binedges_for_fs[ndx2])
        return binedge_tup