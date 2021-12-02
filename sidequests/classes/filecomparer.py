import os
from collections import Counter
from pprint import pprint

from sidequests.funcs.evt_comparison import (
    get_runlumievent_ls_tup, get_list_of_tuples)

from Utils_Python.Utils_Files import check_overwrite

class FileComparer:

    def __init__(self, txt_file1, txt_file2, control_reg="", verbose=False):
        """
        Feed in two txt files to be compared.

        NOTE:
        - Each txt file is converted to a list of 3-tuples and stored.
        - Only lines which begin with a digit are read and stored.

        Parameters
        ----------
        control_reg : str
            Used for printing and writing files.
            If you don't want a specific control region, use "".
        """
        self.file1 = txt_file1
        self.file2 = txt_file2
        self.cr = control_reg
        self.verbose = verbose
        self.set_common_to_both  = None  # Replaced once files are compared.
        self.set_unique_to_file1 = None  # Replaced once files are compared.
        self.set_unique_to_file2 = None  # Replaced once files are compared.

        self.check_cr(txt_file1, txt_file2)
        if control_reg in "":
            self.cr = "all"
        self.ls_of_tup_file1_nodup = None
        self.ls_of_tup_file2_nodup = None

        # Check for duplicates.
        self.ls_of_tup_file1 = get_runlumievent_ls_tup(txt_file1)
        if self.check_for_dups(txt_file1, self.ls_of_tup_file1):
            # Remove duplicates by turning to a set and then back to list.
            self.ls_of_tup_file1_nodup = list(set(self.ls_of_tup_file1))
        else:
            self.ls_of_tup_file1_nodup = self.ls_of_tup_file1

        self.ls_of_tup_file2 = get_runlumievent_ls_tup(txt_file2)
        if self.check_for_dups(txt_file2, self.ls_of_tup_file2):
            self.ls_of_tup_file2_nodup = list(set(self.ls_of_tup_file2))
        else:
            self.ls_of_tup_file2_nodup = self.ls_of_tup_file2

        self.compare_files()

    def check_for_dups(self, txt_file, ls_of_tup):
        """Return True and print info if duplicates within a file are found."""
        len_ls = len(ls_of_tup)
        len_set = len(set(ls_of_tup))
        if len_ls != len_set:
            n_dups = len_ls - len_set
            print(f"[WARNING] Duplicates ({n_dups}) found in file: {txt_file}")
            print(f"[WARNING] len(ls)={len_ls} != len(set)={len_set}")
            if self.verbose:
                # There's some counting error here...
                # I know there are 120 duplicates, but counter only finds 118.
                counter = Counter(ls_of_tup)
                print(f"Showing duplicates found in file:\n{txt_file}")
                dup_key_ls = [k for k,v in counter.items() if v > 1]
                # pprint(dup_key_ls)
                # assert n_dups == len(dup_key_ls)
                pprint(dup_key_ls)
            return True
        return False

    def check_cr(self, path1, path2):
        """Make sure that the control region is the one requested."""
        cr_low = self.cr.lower()
        assert cr_low in ("2p2f", "3p1f", "")
        # Make sure that the two files have the requested CR.
        msg = f"The `control_reg` ({self.cr}) not found in names of txt files."
        assert all(cr_low in f.lower() for f in (path1, path2)), msg

    def compare_files(self):
        """Store unique and common info about files. Called when instantiated."""
        self.set_common_to_both = set(self.ls_of_tup_file1_nodup) & set(self.ls_of_tup_file2_nodup)
        self.set_unique_to_file1 = set(self.ls_of_tup_file1_nodup) - set(self.ls_of_tup_file2_nodup)
        self.set_unique_to_file2 = set(self.ls_of_tup_file2_nodup) - set(self.ls_of_tup_file1_nodup)

    def print_results(self, whose="all", show_n_evts=25, save_to_file=None):
        """Print info describing differences between two files.
        
        Parameters
        ----------
        whose : str
            "file1", "file2", "all"
        """
        print(f"Comparing {self.cr.upper()}:")
        print(f"file1: {self.file1}")
        print(f"file2: {self.file2}")

        print(f"{'n_evts total file1 (no dup): ':<25}{len(self.ls_of_tup_file1_nodup)}")
        print(f"{'n_evts total file2 (no dup): ':<25}{len(self.ls_of_tup_file2_nodup)}")
        print(f"{'n_evts in common: ':<25}{len(self.set_common_to_both)}")
        print(f"{'n_evts unique to file1: ':<25}{len(self.set_unique_to_file1)}")
        print(f"{'n_evts unique to file2: ':<25}{len(self.set_unique_to_file2)}")

        header = "#-- Run -- LumiSect -- Event --#"
        if show_n_evts == -1:
            show_n_evts = None
        if whose in ("file1", "all"):
            print(f"  file1's unique events:")
            print(header)
            pprint(list(self.set_unique_to_file1)[:show_n_evts])
            print()
        if whose in ("file2", "all"):
            print(f"  file2's unique events:")
            print(header)
            pprint(list(self.set_unique_to_file2)[:show_n_evts])
            print()

    def save_events_to_txt(self, kind, outtxt, no_dup=True, overwrite=False):
        """
        Write the events to `outtxt` in the format:

        Run : LumiSect : Event

        Parameters
        ----------
        kind : str
            Choose which events to write to `outtxt`.
            "file1", "file2", "common", "file1_unique", "file2_unique"
        """
        check_overwrite(outtxt, overwrite=overwrite)
        assert kind in ("file1", "file2", "common", "file1_unique", "file2_unique")

        if kind in "file1":
            iter_ls_of_tup = self.ls_of_tup_file1_nodup if no_dup else self.ls_of_tup_file1
        elif kind in "file2":
            iter_ls_of_tup = self.ls_of_tup_file2_nodup if no_dup else self.ls_of_tup_file2
        elif kind in "common":
            iter_ls_of_tup = self.set_common_to_both
        elif kind in "file1_unique":
            iter_ls_of_tup = self.set_unique_to_file1
        elif kind in "file2_unique":
            iter_ls_of_tup = self.set_unique_to_file2

        with open(outtxt, "w") as f:
            f.write("# Run : LumiSect : Event\n")
            for tup in iter_ls_of_tup:
                f.write(f"{tup[0]} : {tup[1]} : {tup[2]}\n")
            print(f"Wrote '{self.cr} {kind}' events to file:\n{outtxt}")

class FileRunLumiEvent:
    """TODO: Initialize instances of this class inside of FileComparer."""

    def __init__(self, txt=None, ls_str_evtid=None):
        """Load evtIDs from a txt file or a list of strings.
        
        Args:
            txt (str): Text file with event IDs as strings.
            ls_str_evtid (list of str)
        """
        self.txt = txt
        self.ls_tup_evtid = self.get_ls_tup_evtid(txt, ls_str_evtid)
        
    def get_ls_tup_evtid(self, txt, ls_str_evtid):
        """Return a list of tuples of (Run, Lumi, Event).

        Args:
            txt (str):
                Path to txt file that contains Run, Lumi Event like:
                    'Run : Lumi : Event'
                NOTE: Will strip newlines and whitespace from the ends.
            ls_str_evtid (list of str):
                

        NOTE: Tuple elements are int.
        """
        # Use exclusive or (xor) to make sure only one source of evtIDs.
        txt_is_good = txt is not None
        ls_is_good = ls_str_evtid is not None
        assert (txt_is_good ^ ls_is_good)
        if ls_is_good:
            assert isinstance(ls_str_evtid, list)
            assert isinstance(ls_str_evtid[-1], str)
            return get_list_of_tuples(ls_str_evtid)
        # Otherwise we are dealing with a txt file with evtID info.
        return get_runlumievent_ls_tup(txt)
    
    def get_ls_evtids_nodups(self, as_type="int"):
        """Return a list of evtIDs with no duplicates..
        
        Args:
            as_type (str): Can choose: 'int' or 'str'.
                'int' -> 3-tuple of ints: (Run, Lumi, Event,)
                'str' -> A single string: 'Run : Lumi : Event'
                Either way, 1 evtID still counts as 1 entry.
        """
        set_tup = set(self.ls_tup_evtid)
        if "str" in as_type.lower():
            return [self.as_str(tup) for tup in set_tup]
        return list(set_tup)
    
    def get_num_duplicates(self, verbose=False):
        """Return the number of duplicate events found in this file.
        
        Duplicate events have identical Run : Lumi : Event numbers.
        """
        n_dups = self.get_tot_num_entries() - len(self.get_ls_evtids_nodups())
        if verbose:
            if n_dups > 0:
                print(f"[WARNING] Found {n_dups} duplicates in:\n{self.txt}")
            else:
                print("No duplicates found.")
        return n_dups
    
    def get_tot_num_entries(self):
        """Return the number of 3-tuples within `self.ls_tup_evtid`."""
        return len(self.ls_tup_evtid)

    def get_num_entries_nodup(self):
        """Return the number of 3-tuples after removing duplicates."""
        return self.get_tot_num_entries() - self.get_num_duplicates()
    
    def show_duplicates(self, as_type="int"):
        """Print the Run : Lumi : Event of any duplicates found in file.
        
        Args:
            as_type (str): Way to display the printed info.
                Can choose: 'int' or 'str'.
        """
        if self.get_num_duplicates() == 0:
            print("No duplicates found.")
        else:
            # FIXME: There may be a counting error here...
            counter = Counter(self.ls_tup_evtid)
            if "str" in as_type.lower():
                dup_ls = [self.as_str(k) for k,v in counter.items() if v > 1]
            else:
                dup_ls = [k for k,v in counter.items() if v > 1]
            print("Duplicate events:")
            pprint(dup_ls)

    def as_str(self, key_tup):
        """Return `key_tup` as a str: 'Run : Lumi : Event'."""
        return f"{key_tup[0]} : {key_tup[1]} : {key_tup[2]}"
    
    def analyze_evtids(self, other, event_type, print_evts=False):
        """Return list of 3-tuple evtIds common to both FileRunLumiEvents.
        
        Args:
            other (FileRunLumiEvent): Dude whose events will be compared.
            event_type (str): Choose between 'common' or 'unique'.
            print_evts (bool, optional): Default is False.
        """
        this_set = set(self.get_ls_evtids_nodups())
        other_set = set(other.get_ls_evtids_nodups())
        choice = event_type.lower()
        if "common" in choice:
            set_evt_combine = this_set & other_set
        elif "unique" in choice:
            set_evt_combine = this_set - other_set
        else:
            raise ValueError(f"event_type={event_type} not understood")
        n_evts = len(set_evt_combine)
        if self.txt is None:
            basename = "...the original list you used."
        else:
            basename = os.path.basename(self.txt)
        print(f"Found {n_evts} {event_type} events in:\n{basename}")
        if print_evts:
            print(set_evt_combine)
        return list(set_evt_combine)