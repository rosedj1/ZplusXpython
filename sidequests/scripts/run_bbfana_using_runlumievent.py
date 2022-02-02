"""
------------------------------------------------------------------------------
PURPOSE: Prepares a template and uses the HZZ Analyzer on a single root file
Make a single root file from specific data events, using Run:LumiSect:Event.
SYNTAX:  python3 <this_script>.py
NOTE:    Before running script, do:
            ```
            voms-proxy-init -voms cms
            cmsenv
            # In the ZplusXpython dir, do:
            source setup_lxplus.sh  # Or setup_hpg.sh.
            ```
    - If you want to use this file on multiple root files at once, look into:
      sidequests/scripts/run_HZZAna_singleevent_in_bkg.sh
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-20
UPDATED: 2022-02-02
------------------------------------------------------------------------------
"""
import os
import sys
import argparse
# import ROOT
from Utils_Python.Utils_Files import open_json, check_overwrite, replace_value
from Utils_Python.Commands import shell_cmd
from sidequests.classes.templatemanager import TemplateManager
from sidequests.scripts.get_datasets_from_missing_evts import make_evtid2rootfile_dct
from sidequests.data.datasets import dataset_tup_2018

overwrite = 0
verbose = 1  # BBF Analyzer will print verbosely into an '.out' file.

ls_str_evt_ids = [
    #=== Below are 8/9 of Jake's unique 3P1F 4mu events which the BBF Ana with
    #=== the RedBkg fix now selects.
    "315689:342:398232246",
    # "322599:224:359072495",
    # "316766:179:208365005",
    "319524:885:1310553109",
    # "317291:636:878537435",
    # "322348:827:1498597313",
    # "321434:39:65055154",
    # "319991:777:1213672625"
]

# Will be appended with evtID info.
outfile_rootname = "jakehas_butnotfilippo_3p1f"

input_template = "/afs/cern.ch/work/d/drosenzw/zplusx/CMSSW_10_6_12/src/UFHZZAnalysisRun2/UFHZZ4LAna/python/templateData_102X_Legacy18_2l_cfg_template.py"
outdir_template = "/afs/cern.ch/work/d/drosenzw/zplusx/CMSSW_10_6_12/src/UFHZZAnalysisRun2/UFHZZ4LAna/python/template_copies/"
outdir_root = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/"
outdir_txt = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/output/txt/"

def get_dir_to_run_ana(outdir_template):
    """
    Return the starting dir where you should do:
        `cmsRun <template>.py`.
    """
    assert "UFHZZAnalysisRun2" in outdir_template
    return outdir_template.split("UFHZZAnalysisRun2")[0]

def prepare_bbf_template_copy(
    ana_template,
    evtID,
    input_dataset,
    input_rootfile,
    output_template,
    output_rootfile,
    verbose=False,
    ):
    """Creates a copy of a template for the BBF Analyzer."""
    tm = TemplateManager(ana_template)
    tm.duplicate_template(output_template=output_template)
    # Event ID.
    replace_value("EVENTRANGE", evtID, output_template)
    # Input root file
    replace_value("DUMMYFILELIST", input_rootfile, output_template)
    # Output file.
    replace_value("DUMMYFILENAME.root", output_rootfile, output_template)
    if "Run2018D" not in input_dataset:
        replace_value('run_for_GT = "D"', 'run_for_GT = "ABC"', output_template)
    replace_value('VERBOSE', "True" if verbose else "False", output_template)

def run_bbfana_single_evt(
    evtID,
    dataset_tup,
    ana_template,
    outdir_root,
    outfile_rootname,
    overwrite=False,
    verbose=False,
    ):
    """
    Run BBF Analyzer on single event and output a root file.

    Single event is specified by `evtID`:
        "Run:LumiSect:Event"
    Executes:
        `cmsRun template_<blahblah>_cfg_copy.py`

    Args:
        evtID (str):
            "Run:Lumi:Event" of the event you want to process.
        dataset_tup (tup):
            Tuple of strings of the Data Set names to search for `evtID`.
        ana_template (str):
            File path to the BBF Analyzer template.
        outfile_rootname= (str):
            File path to output root file with analyzed event info.
    """
    os.makedirs(outdir_template, exist_ok=True)
    os.makedirs(outdir_root, exist_ok=True)
    os.makedirs(outdir_txt, exist_ok=True)
        
    dir_start = os.getcwd()
    dir_to_run_ana = get_dir_to_run_ana(outdir_template)

    # Grab a single event.
    run, lumi, event = evtID.split(":")

    suffix = evtID.replace(":", "_")
    output_rootfile_name = outfile_rootname.replace('.root', '')
    output_rootfile_name += f'_{suffix}.root'
    output_rootfile = os.path.join(outdir_root, output_rootfile_name)
    check_overwrite(output_rootfile, overwrite=overwrite)

    ana_template_name = os.path.basename(ana_template)
    output_template_name = ana_template_name.replace(".py", f"_copy_{suffix}.py")
    output_template = os.path.join(outdir_template, output_template_name)
    check_overwrite(output_template, overwrite=overwrite)

    # This txt file contains `cout` info from the HZZ Analyzer!
    output_txt_name = output_rootfile_name.replace('.root', '.out')
    output_txt = os.path.join(outdir_txt, output_txt_name)

    evt_lsoftup = [(run, lumi, event,)]
    d_evt_info = make_evtid2rootfile_dct(
        evt_lsoftup,
        dataset_tup=dataset_tup_2018,
        evt_start=1,
        evt_stop=-1
        )

    input_rootfile = d_evt_info[evtID][0]
    input_dataset  = d_evt_info[evtID][1]
    print(f"input_dataset:  {input_dataset}")
    print(f"input_rootfile: {input_rootfile}")

    prepare_bbf_template_copy(
        evtID=evtID,
        ana_template=ana_template,
        input_dataset=input_dataset,
        input_rootfile=input_rootfile,
        output_template=output_template,
        output_rootfile=output_rootfile,
        verbose=verbose,
        )

    shell_cmd(f"cd {dir_to_run_ana}", verbose=True)
    shell_cmd(f"cmsRun {output_template}", outfile=output_txt, verbose=True)
    print(f"Created root file:\n{output_rootfile}")
    print(f"Created output txt:\n{output_txt}")
    shell_cmd(f"cd {dir_start}", verbose=True)

if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     '-e', 
    #     '--eventID', 
    #     dest='eventID', 
    #     type=str, 
    #     help='Run:Lumi:Event (e.g. 319991:777:1213672625)'
    #     )

    for evt_str in ls_str_evt_ids:

        run_bbfana_single_evt(
            evtID=evt_str,
            dataset_tup=dataset_tup_2018,
            ana_template=input_template,
            outdir_root=outdir_root,
            outfile_rootname=outfile_rootname,
            overwrite=overwrite,
            verbose=verbose,
        )
