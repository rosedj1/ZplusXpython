"""
PURPOSE: Take a txt file of "event ID" (Run:LumiSect:Event) values and search
         a list of data sets in which to find the corresponding event. Save
         the LFN of the root file and the data set name to a json file.
SYNTAX:  python3 <this_script>.py
NOTE:
    - Before running script, do: `voms-proxy-init`
    - Sometimes when running this code, the edmDumpEvent.py command will throw an
      an error and cause the entire code to crash.
      Workaround: work in batches of <=300 events.
      TODO: Add a try/except block to catch the error.
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-18
UPDATED: 2021-10-27
"""
import sys
from pprint import pprint
from Utils_Python.Utils_Files import save_to_json, check_overwrite
from Utils_Python.printing import print_header_message
from sidequests.data.datasets import dataset_tup_2018
from sidequests.classes.filemanager import DataSetFinder

infile_txt_elisa_unique_3p1f       = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/data/jakes_new2018data/CRLLos_3P1F_listOfEvents_unique.txt"
infile_txt_elisa_unique_2p2f       = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/data/jakes_new2018data/CRLLos_2P2F_listOfEvents_unique.txt"
infile_txt_elisa_commonwithherself = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/data/jakes_new2018data/CRLLos_2P2F_3P1F_listOfEvents_unique_commontobothCRs.txt"

outfile_json_3p1f = "../data/json/elisa_unique_evts_id_rootfile_3p1f.json"
outfile_json_2p2f = "../data/json/elisa_unique_evts_id_rootfile_2p2f.json"
outfile_json_elisa_commonwithherself = "../data/json/elisa_unique_2p2f_3p1f_commontobothCRs_evts_id_rootfile.json"

overwrite = 0

evt_start = 1  # Event 1 is the first event.
evt_stop = -1  # Includes this last event. Use `-1` for all.

def get_list_of_lines(evt_ls_txt):
    """
    Return a list of the lines from `evt_ls_txt`.
    The lines must start with a digit.
    Trailing newlines ('\\n') are stripped.
    """
    with open(evt_ls_txt, "r") as f:
        return [line.rstrip('\n') for line in f.readlines() if line[0].isdigit()]

def get_list_of_tuples(evt_ls):
    """
    Return a list of 3-tuples from a list of strings `evt_ls`:

    [
        (Run1, LumiSect1, Event1),
        (Run2, LumiSect2, Event2),
        ...
    ]
    """
    new_evt_ls = []
    for line in evt_ls:
        tup = tuple([int(num) for num in line.split(":")])
        new_evt_ls.append(tup)
    return new_evt_ls

def make_evtid2rootfile_dct(evt_lsoftup, dataset_tup, evt_start=1, evt_stop=-1):
    """
    Return a dict with the following key:val pairs:
        
        (Run:LumiSect:Event) : [
            "rootfile_path_LogicalFileName",
            "dataset"
        ]

    Run : int
    LumiSect : int
    Event : int
    rootfile_path_LogicalFileName : str
    dataset : str
        The data set containing the rootfile.
    
    Parameters
    ----------
    evt_lsoftup : list of 3-tuples
        Each 3-tuple is `(Run:LumiSect:Event)`.
        This corresponds to a particular event found in some root file in
        some data set.
    dataset_tup : tuple of str
        The possible data sets to search for the root file containing the
        event.
    evt_start : int
        The first event to start processing.
        Starts at `1`.
    evt_stop : int
        The last event to process.
        If `-1` then process all events.
    """
    if evt_stop == -1:
        evt_stop = len(evt_lsoftup)
    n_evts_to_proc = evt_stop - evt_start + 1
    print(f"Processing event range: {evt_start}->{evt_stop}")
    print(f"Number of unique events to process: {n_evts_to_proc}")
    dct = {}
    dsf = DataSetFinder()
    
    for ct, evt_id in enumerate(evt_lsoftup[(evt_start-1):evt_stop], 1):
        if (ct % 10) == 0:
            print_header_message(
                f"Processing event {ct}/{n_evts_to_proc}",
                pad_char="#",
                n_center_pad_chars=5
                )

        run      = evt_id[0]
        lumisect = evt_id[1]
        event    = evt_id[2]

        rf = dsf.find_first_dataset_rootfile(run=run, lumisect=lumisect, event=event, dataset_tup=dataset_tup, outfile="pickevents.root")
        dct[rf.evt_id(as_type="str")] = (rf.fullpath, rf.dataset)
    return dct

def write2json_evtid2rootfile_dct(infile_txt, outfile_json, dataset_tup, evt_start=0, evt_stop=-1, overwrite=False):
    """
    Write a dict to a json file, where the dict relates evt ID to root
    file and data set info.

    Parameters
    ----------
    dataset_tup : tuple of str
        The data sets to search for `Run:LumiSect:Event`.
    evt_start : int
        The first event to start processing.
    evt_stop : int
        The last event to process.
        If `-1` then process all events.
    """
    check_overwrite(outfile_json, overwrite=overwrite)
    print(
        f"Extracting event list from:\n{infile_txt}\n"
        f"Will write JSON file:\n{outfile_json}\n"
        f"Using data sets:"
        )
    pprint(dataset_tup)
    evt_lsoftup = get_list_of_tuples(get_list_of_lines(infile_txt))
    dct = make_evtid2rootfile_dct(evt_lsoftup, dataset_tup, evt_start=evt_start, evt_stop=evt_stop)
    save_to_json(dct, outfile_json, sort_keys=False, overwrite=True)

if __name__ == "__main__":
    # write2json_evtid2rootfile_dct(infile_txt=infile_txt_elisa_unique_3p1f, outfile_json=outfile_json_3p1f, dataset_tup=dataset_tup_2018, evt_start=evt_start, evt_stop=evt_stop, overwrite=overwrite)
    # write2json_evtid2rootfile_dct(infile_txt=infile_txt_elisa_unique_2p2f, outfile_json=outfile_json_2p2f, dataset_tup=dataset_tup_2018, evt_start=evt_start, evt_stop=evt_stop, overwrite=overwrite)
    
    write2json_evtid2rootfile_dct(infile_txt=infile_txt_elisa_commonwithherself, outfile_json=outfile_json_elisa_commonwithherself, dataset_tup=dataset_tup_2018, evt_start=evt_start, evt_stop=evt_stop, overwrite=overwrite)
