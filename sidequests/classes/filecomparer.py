import os
from collections import Counter
from pprint import pprint
from ROOT import TFile
# Package imports.
from Utils_Python.Utils_Files import check_overwrite, open_json
from Utils_Python.printing import print_periodic_evtnum
from constants.finalstates import dct_finalstates_int2str

def get_list_of_tuples(evt_ls):
    """
    Return a list of 3-tuples from a list of strings `evt_ls`:

    [
        (Run1, LumiSect1, Event1),
        (Run2, LumiSect2, Event2),
        ...
    ]

    NOTE: Elements of tuples are int.
    """
    new_evt_ls = []
    for line in evt_ls:
        # Grab the first three entries: Run, Lumi, Event.
        tup = tuple([int(num) for num in line.split(":")[:3]])
        new_evt_ls.extend([tup])
    return new_evt_ls

def get_runlumievent_ls_tup(txt):
    """Return a list of tuples of (Run, Lumi, Event) from a txt.

    Args:
        txt (str): Path to txt file that contains Run, Lumi Event like:
                   'Run : Lumi : Event'
                   NOTE: Will strip newlines and whitespace from the ends.

    NOTE: Tuple elements are int.
    """
    return get_list_of_tuples(get_list_of_lines(txt))

def write_tree_info_to_txt(
    infile,
    outtxt,
    m4l_lim=(70, 1000),
    keep_2P2F=True,
    keep_3P1F=True,
    fs=5,
    path_to_tree="passedEvents",
    print_every=500000
    ):
    """Write info from TFile `infile` from TTree 'passedEvents' to `outtxt`.

    Info which gets written:
    Run : LumiSect : Event

    Args:
        fs (int): 4-lep final state (branch = finalState).
            1 = 4mu
            2 = 4e
            3 = 2e2mu
            4 = 2mu2e
            5 = all
    """
    m4l_min = m4l_lim[0]
    m4l_max = m4l_lim[1]

    tfile = TFile.Open(infile)
    tree = tfile.Get(path_to_tree)
    n_tot = tree.GetEntries()

    outtxt_dir = os.path.dirname(outtxt)
    outtxt_basename_noext = os.path.basename(outtxt).split(".")[0]

    if keep_2P2F:
        outtxt_basename_noext += "_2P2F"
    if keep_3P1F:
        outtxt_basename_noext += "_3P1F"
    outtxt_basename_noext += f"_{dct_finalstates_int2str[fs]}"
    outtxt_basename_noext += f"_{m4l_min}masswindow{m4l_max}.txt"

    outtxt_fullname = os.path.join(
        outtxt_dir,
        outtxt_basename_noext
    )

    with open(outtxt_fullname, "w") as f:
        f.write("# Run : LumiSect : Event\n")
        for ct, evt in enumerate(tree):
            print_periodic_evtnum(ct, n_tot, print_every=print_every)
            m4l = evt.mass4l
            if (m4l < m4l_min) or (m4l > m4l_max):
                continue
            good_fs = True if fs == evt.finalState or fs == 5 else False
            if not good_fs:
                continue
            keep_evt = False
            if keep_2P2F and evt.is2P2F:
                keep_evt = True
            elif keep_3P1F and evt.is3P1F:
                keep_evt = True
            if keep_evt:
                f.write(f"{evt.Run} : {evt.LumiSect} : {evt.Event}\n")
    print(f"TTree info written to:\n{outtxt_fullname}")

def write_lstup_info_to_txt(ls_tup, outtxt, print_every=500000):
    """Write event ID info from list of tuples `ls_tup` to `outtxt`.

    Example info which gets written:
    # Run : LumiSect : Event
    315690 : 467 : 285311430
    316239 : 157 : 192988698
    ...

    NOTE: Tuple (really a 3-tuple) elements should be ints.
    """
    with open(outtxt, "w") as f:
        f.write("# Run : LumiSect : Event\n")  
        for tup in ls_tup:  
            run, lumi, event = tup 
            f.write(f"{run} : {lumi} : {event}\n") 
        print(f"TTree info written to:\n{outtxt}")

def get_list_of_lines(evt_ls_txt):
    """Return a list of the lines from `evt_ls_txt` with comments removed.
    
    The lines are checked to start with a digit to avoid comments (#).
    Trailing newlines ('\\n') and whitespaces on both ends are stripped.
    """
    ls_lines = []
    with open(evt_ls_txt, "r") as f:
        for line in f.readlines():
            clean_line = line.rstrip('\n').rstrip().lstrip()
            if not clean_line[0].isdigit():
                continue
            ls_lines.extend([clean_line])
    return ls_lines
        # return [line.rstrip('\n').rstrip() for line in f.readlines() if line[0].isdigit()]

def get_list_of_entries(txt):
    """Return a list of entries (int) from a txt file."""
    ls_entries = []
    with open(txt, "r") as f:
        lines = f.readlines()
        for l in lines:
            if "Index" in l:
                str_num = l.split(": ")[1]
                entry = int(str_num.rstrip('\n'))
                ls_entries.extend([entry])
    return ls_entries

def evtID_as_str(evtID):
    """Return `evtID` as a str: 'Run : Lumi : Event'."""
    return f"{evtID[0]} : {evtID[1]} : {evtID[2]}"

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

    def __init__(
        self,
        txt=None,
        ls_str_evtid=None,
        ls_tup_evtid=None,
        set_tup_evtid=None,
        jsonpath_and_cr=('', ''),
        ):
        """Load a list of event IDs from some source of event IDs.
        
        Args:
            txt (str):
                Text file with event IDs as strings.
            ls_str_evtid (list of str):
                List contains event IDs as strings.
            jsonpath_and_cr (tup):
                Element 0 is the path (str) to json file.
                Element 1 is the control region (str) to select. Options:
                    '2p2f' or '3p1f'

                The json file itself is a dict, of course.
                Keys of json are event ID strings, like:
                    '315259 : 139 : 90465649'
                Values are subdicts:
                    {
                        'num_combos_2p2f': 0,
                        'num_combos_3p1f': 1
                        }
        """
        # Make sure only 1 source of events was given.
        assert sum(
                x is not None for x in (
                    txt, ls_str_evtid, ls_tup_evtid, set_tup_evtid,
                    )
                ) == 1
        self.txt = txt

        # First priority: store `self.ls_tup_evtid`.
        if ls_tup_evtid is not None:
            self.ls_tup_evtid = ls_tup_evtid
        # elif len(jsonpath) > 0:
        #     jsonpath = jsonpath_and_cr[0]
        #     cr = jsonpath_and_cr[1].lower()
        #     assert cr in ('2p2f', '3p1f')
        #     self.ls_tup_evtid = self.convert_dict_to_ls_tup(json_path, cr)
        else:
            self.ls_tup_evtid = self.get_ls_tup_evtid(
                txt,
                ls_str_evtid,
                set_tup_evtid
                )
        
    def convert_dict_to_ls_tup(self, json_path, cr):
        """Return a list of 3-tuples representing event IDs.

        FIXME: Needs to be tested.

        Args:
            json_path (str): Path to json file (dict is inside).
            cr (str) : Control region whose event IDs to select. Options:
                '2p2f' or '3p1f'
        """
        dct = open_json(json_path)

        ls_tup_evtid
        for evtid, subdct in dct.items():
            for cr_combo_str, ct in subdct.items():
                if cr in cr_combo_str:
                    # Here's the trick! If there are 2 combos,
                    # we will double the list!
                    ls_strs = [cr_combo_str] * ct
                    ls_tup = get_list_of_tuples(ls_strs)
                    ls_tup_evtid.extend(ls_tup)
        return ls_tup_evtid

    def get_ls_tup_evtid(self, txt, ls_str_evtid, set_tup_evtid):
        """Return a list of tuples of (Run, Lumi, Event).

        Args:
            txt (str):
                Path to txt file that contains Run, Lumi Event like:
                    'Run : Lumi : Event'
                NOTE: Will strip newlines and whitespace from the ends.
            ls_str_evtid (list of str):

        NOTE: Tuple elements are int.
        """
        if isinstance(ls_str_evtid, list):
            # Check to make sure list has expected form.
            assert isinstance(ls_str_evtid[-1], str)
            return get_list_of_tuples(ls_str_evtid)
        if isinstance(set_tup_evtid, set):
            # We were given a set of tuples.
            return list(set_tup_evtid)
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

    def get_duplicate_counter(self):
        """Return a counter of ((evtID_tup): n_times_appeared).
        
        Duplicate events have identical Run : Lumi : Event numbers.
        """
        if self.get_num_duplicates() == 0:
            return Counter()
        else:
            return Counter(self.ls_tup_evtid)
    
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
        counter = self.get_duplicate_counter()
        if len(counter.keys()) == 0:
            print("No duplicates found.")
        else:
            print(f"{'Duplicate Event ID':^26} --- Total Appearances")
            for evtID, n_times in counter.items():
                if n_times > 1:
                    if "str" == as_type.lower():
                        evtID = evtID_as_str(evtID)
                    # Represent the tuple as a string in order to print it.
                    print(f"{evtID.__repr__():<26} --- {n_times:^17}")

        # The below works but it's less sexy.
        # ls_tup_evtid_cp = self.ls_tup_evtid.copy()
        # for unique_evt in self.get_ls_evtids_nodups():
        #     ls_tup_evtid_cp.remove(unique_evt)
        # # Anything left is a duplicate.
        # assert len(ls_tup_evtid_cp) == self.get_num_duplicates()
        # print(f"Number of duplicates found: {len(ls_tup_evtid_cp)}")
        # pprint(ls_tup_evtid_cp)

    def analyze_evtids(self, other, event_type, print_evts=False):
        """Return list of 3-tuple evtIds common to both FileRunLumiEvents.
        
        Args:
            other (FileRunLumiEvent): Dude whose events will be compared.
            event_type (str): Choose between 'common' or 'unique'.
            print_evts (bool, optional): Default is False.

        NOTE:
            Duplicates are removed before evtIds are compared.
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