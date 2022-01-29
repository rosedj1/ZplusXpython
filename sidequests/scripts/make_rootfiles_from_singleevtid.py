"""
------------------------------------------------------------------------------
PURPOSE: Prepares a template and uses the HZZ Analyzer on a single root file
Make a single root file from specific data events, using Run:LumiSect:Event.
SYNTAX:  python3 <this_script>.py
NOTE:    Before running script, do:
            ```
            voms-proxy-init
            cmsenv
            ```
    - If you want to use this file on multiple root files at once, use:
      sidequests/scripts/run_HZZAna_singleevent_in_bkg.sh
AUTHOR:  Jake Rosenzweig
CREATED: 2021-10-20
UPDATED: 2021-10-27
------------------------------------------------------------------------------
"""
import os
import sys
import argparse
# import ROOT
from Utils_Python.Utils_Files import open_json, check_overwrite, replace_value
from Utils_Python.Commands import shell_cmd
from sidequests.classes.filemanager import TemplateManager

overwrite = 0
infile_json = "../data/json/elisa_unique_2p2f_3p1f_commontobothCRs_evts_id_rootfile.json"
output_rootfile_basename = "elisa_unique_2p2f_3p1f_commontobothCRs"

input_template      = "/afs/cern.ch/work/d/drosenzw/zplusx/CMSSW_10_6_12/src/UFHZZAnalysisRun2/UFHZZ4LAna/python/templateData_102X_Legacy18_2l_cfg_template.py"
output_template_dir = "/afs/cern.ch/work/d/drosenzw/zplusx/CMSSW_10_6_12/src/UFHZZAnalysisRun2/UFHZZ4LAna/python/template_copies/"
output_rootfile_dir = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/"
output_txt_dir      = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/output/txt/"

def get_dir_to_run_ana(output_template_dir):
    """
    Return the starting dir where you should do:
        `cmsRun <template>.py`.
    """
    assert "UFHZZAnalysisRun2" in output_template_dir
    return output_template_dir.split("UFHZZAnalysisRun2")[0]

if __name__ == "__main__":
    os.makedirs(output_template_dir, exist_ok=True)
    os.makedirs(output_rootfile_dir, exist_ok=True)
    os.makedirs(output_txt_dir, exist_ok=True)
         
    dir_start = os.getcwd()
    dir_to_run_ana = get_dir_to_run_ana(output_template_dir)
    
    evt_id_rootfile_dct = open_json(infile_json)

    # evtana = EventAnalyzer()
    # evtana.run_analyzer_single_evt()

    # class EventAnalyzer:

    #     def __init__(self):
    #         pass

    #     def run_analyzer_single_evt(self, evt_id_str, output_template): #input_root, input_dataset, output_rootfile):
    #         """
    #         Run HZZ Analyzer on single event and output a root file.
    #         Single event is specified by `evt_id_str`:
    #             "Run:LumiSect:Event"
    #         Executes:
    #             `cmsRun template_<blahblah>_cfg_copy.py`
    #         """
    #         cmd = f"cmsRun {output_template}"
    #         print(f"Executing:\n`{cmd}`")
    #         shell_cmd(cmd, outfile=output_txt)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='index', type=int, help='Index of list(JSON dict.keys())')
    args = parser.parse_args()
    index = int(args.index)
    
    # Grab a single event.
    evt_id = list(evt_id_rootfile_dct.keys())[index]
    
    suffix = evt_id.replace(":", "_")
    output_rootfile_name = output_rootfile_basename.replace('.root', '')
    output_rootfile_name += f'_{suffix}.root'
    output_rootfile = os.path.join(output_rootfile_dir, output_rootfile_name)
    check_overwrite(output_rootfile, overwrite=overwrite)

    input_template_name = os.path.basename(input_template)
    output_template_name = input_template_name.replace(".py", f"_copy_{suffix}.py")
    output_template = os.path.join(output_template_dir, output_template_name)
    check_overwrite(output_template, overwrite=overwrite)

    # This txt file contains `cout` info from the HZZ Analyzer!
    output_txt_name = output_rootfile_name.replace('.root', '.out')
    output_txt = os.path.join(output_txt_dir, output_txt_name)


    input_rootfile = evt_id_rootfile_dct[evt_id][0]
    input_dataset  = evt_id_rootfile_dct[evt_id][1]
    print(f"input_dataset:  {input_dataset}")
    print(f"input_rootfile: {input_rootfile}")

    # Prep the template copy.
    tm = TemplateManager(input_template)
    tm.duplicate_template(output_template=output_template)
    # Output file.
    replace_value("DUMMYFILENAME.root", output_rootfile, output_template)
    # Input root file
    replace_value("DUMMYFILELIST", input_rootfile, output_template)
    # Event ID.
    replace_value("EVENTRANGE", evt_id, output_template)

    if "Run2018D" not in input_dataset:
        replace_value('run_for_GT = "D"', 'run_for_GT = "ABC"', output_template)

    shell_cmd(f"cd {dir_to_run_ana}", verbose=True)
    shell_cmd(f"cmsRun {output_template}", outfile=output_txt, verbose=True)
    print(f"Created root file:\n{output_rootfile}")
    print(f"Created output txt:\n{output_txt}")
    shell_cmd(f"cd {dir_start}", verbose=True)