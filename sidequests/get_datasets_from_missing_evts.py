import subprocess
import os
import sys
import json
from pprint import pprint
from shutil import copy2

sys.path.append("/afs/cern.ch/work/d/drosenzw/HiggsMassMeasurement/")
from Utils_Python.Utils_Files import check_overwrite

infile_txt_elisa_unique_3p1f = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/findmissingevents_comparetoelisa/jakes_new2018data/CRLLos_3P1F_listOfEvents_unique.txt"

input_template = "/afs/cern.ch/work/d/drosenzw/zplusx/CMSSW_10_6_12/src/UFHZZAnalysisRun2/UFHZZ4LAna/python/templateData_102X_Legacy18_2l_cfg.py"
output_template_dir = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/template_copies/"
output_rootfile_dir = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/rootfiles/"
output_txt_dir = "/afs/cern.ch/work/d/drosenzw/zplusx/ZplusXpython/sidequests/txt/"

output_rootfile_basename = "test01"

overwrite = 1

dataset_tup = (
    "/SingleMuon/Run2018A-17Sep2018-v2/MINIAOD",
    "/SingleMuon/Run2018B-17Sep2018-v1/MINIAOD",
    "/SingleMuon/Run2018C-17Sep2018-v1/MINIAOD",
    "/SingleMuon/Run2018D-22Jan2019-v2/MINIAOD",
    "/DoubleMuon/Run2018A-17Sep2018-v2/MINIAOD",
    "/DoubleMuon/Run2018B-17Sep2018-v1/MINIAOD",
    "/DoubleMuon/Run2018C-17Sep2018-v1/MINIAOD",
    "/DoubleMuon/Run2018D-PromptReco-v2/MINIAOD",
    "/MuonEG/Run2018A-17Sep2018-v1/MINIAOD",
    "/MuonEG/Run2018B-17Sep2018-v1/MINIAOD",
    "/MuonEG/Run2018C-17Sep2018-v1/MINIAOD",
    "/MuonEG/Run2018D-PromptReco-v2/MINIAOD",
    "/EGamma/Run2018A-17Sep2018-v2/MINIAOD",
    "/EGamma/Run2018B-17Sep2018-v1/MINIAOD",
    "/EGamma/Run2018C-17Sep2018-v1/MINIAOD",
    "/EGamma/Run2018D-22Jan2019-v2/MINIAOD",
)

evt_id_tup = (
    # "321973:1133:1973286739",
    # "321834:84:126135620",
    # "317182:530:685103194",
    # "321909:318:543241955",
    # "320821:118:130885195",
    # "316766:179:208365005",
    # "316470:447:582167202",
    # "321434:326:542897171",
    # "322252:526:921661039",
)

def shell_cmd(cmd_str, get_stdout=True, outfile=None):
    """Execute `cmd_str` from your shell and return the CompletedProcess.
    
    Say you want to execute: `ls -l some_dir/`
    Then do: shell_cmd("ls -l some_dir/")

    Parameters
    ----------
    cmd_str : str
        String of commands to execute in shell.
    get_stdout : bool
        If True, will store stdout.
        To print stdout as a str:
        `results = subprocess.run(<cmds>)`
        `results.stdout`

        NOTE: If `outfile` is provided, then stdout will not be stored.
        Instead it will be written to `outfile`.
    outfile : str or None
        File path or name of file. Write stdout to this file.
    """
    cmd_parts_ls = cmd_str.split(" ")
    if outfile is not None:
        with open(outfile, "w") as f:
            return subprocess.run(cmd_parts_ls, stdout=f)
    if get_stdout:
        return subprocess.run(cmd_parts_ls, stdout=subprocess.PIPE, universal_newlines=True)
    return subprocess.run(cmd_parts_ls)

def replace_value(old, new, script, verbose=False):
    """Use the `sed` command to replace `old` with `new` in `script`."""
    special_chars = ['/', '.', '\n', ',', '-', ':']
    for sc in special_chars:
        old = old.replace(sc, f"\{sc}")
        new = new.replace(sc, f"\{sc}")
    # old = old.replace("#", "\#")
    # new = new.replace("#", "\#")
    cmd = ["sed", "-i", f"s|{old}|{new}|g", script]
    if verbose:
        print(f"Running this command: {cmd}")
    output = subprocess.run(cmd)

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

class DataSetFinder:

    def __init__(self):
        pass
        # self.run = run
        # self.lumisect = lumisect
        # self.event = event

    def get_stdout_from_pickevent(self, run, lumisect, event, dataset, outfile="pickevents.root"):
        """
        Return the stdout when doing:
            `edmPickEvents.py <dataset> <run:lumisect:event>`

        Parameters
        ----------
        run : int
        lumisect : int
        event : int
        dataset : str
        outfile : str
        """
        print(f"Searching for event {run}:{lumisect}:{event} in {dataset}.")
        results = shell_cmd(
                    f"edmPickEvents.py {dataset} {run}:{lumisect}:{event} --output={outfile}",
                    get_stdout=True
                    )
        return results.stdout
                    
    def parse_stdout(self, stdout):
        """
        Return the str after 'inputFiles=', such as the following:
        
        edmCopyPickMerge outputFile=pickevents.root \\
          eventsToProcess=321834:126135620 \\
          inputFiles=/store/data/Run2018D/MuonEG/MINIAOD/PromptReco-v2/000/321/834/00000/4C96D92F-3AAE-E811-80D4-FA163E9D5E27.root
        """
        return stdout.split("inputFiles=")[1].rstrip("\n")
  
    def find_first_dataset_rootfile(self, run, lumisect, event, dataset_tup, outfile="pickevents.root"):
        """
        Search `dataset_tup` for the first data set containing:
            `run`, `lumisect`, `event`.

        Returns a `RootFile` object, which stores this info:
        
        RootFile.run : int
        RootFile.lumisect : int
        RootFile.event : int
        RootFile.dataset : str
            The data set found which contains `run`, `lumisect`, `event`.
        RootFile.rootfile : str
            The root file found in `dataset` which contains `run`, `lumisect`, `event`.
        """
        rf = RootFile()
        rf.run = run
        rf.lumisect = lumisect
        rf.event = event
        
        print(f"Searching data sets for first instance of: {rf.evt_id()}.")
        for ds in dataset_tup:
            stdout = self.get_stdout_from_pickevent(run, lumisect, event, ds, outfile=outfile)

            possible_rootfile = self.parse_stdout(stdout)
            if len(possible_rootfile) > 0:
                rf.fullpath = possible_rootfile
                rf.dataset = ds
                return rf
        print(f"[WARNING] No rootfile was found corresponding to {rf.evt_id()}.")

class TemplateManager:

    def __init__(self, input_template):
        self.input_template = input_template

    def duplicate_template(self, output_template):
        """Copy `self.input_template` to `output_template`."""
        print(f"Making copy of {self.input_template}:\n{output_template}")
        copy2(self.input_template, output_template)

class RootFile:

    def __init__(self):
        self.run = None
        self.lumisect = None
        self.event = None
        self.dataset = None
        self.fullpath = None

    def evt_id(self):
        return f"{self.run}:{self.lumisect}:{self.event}"

def main():

    os.makedirs(output_template_dir, exist_ok=True)
    os.makedirs(output_rootfile_dir, exist_ok=True)
    os.makedirs(output_txt_dir, exist_ok=True)

    for evt_id in evt_id_tup:
        suffix = evt_id.replace(":", "_")
        output_rootfile_name = f"{output_rootfile_basename.rstrip('.root')}_{suffix}.root"
        output_rootfile = os.path.join(output_rootfile_dir, output_rootfile_name)
        check_overwrite(output_rootfile, overwrite=overwrite)

        input_template_name = os.path.basename(input_template)
        output_template_name = input_template_name.replace(".py", f"_copy_{suffix}.py")
        output_template = os.path.join(output_template_dir, output_template_name)
        check_overwrite(output_template, overwrite=overwrite)

        output_txt_name = f"{output_rootfile_basename}_eventproc_info_{suffix}.out"
        output_txt = os.path.join(output_txt_dir, output_txt_name)

        tm = TemplateManager(input_template)
        tm.duplicate_template(output_template=output_template)

        dsf = DataSetFinder()

        run, lumisect, event = evt_id.split(":")
        rf = dsf.find_first_dataset_rootfile(run=int(run), lumisect=int(lumisect), event=int(event), dataset_tup=dataset_tup, outfile="pickevents.root")

        print(f"rf.run = {rf.run}")
        print(f"rf.lumisect = {rf.lumisect}")
        print(f"rf.event = {rf.event}")
        print(f"rf.evt_id() = {rf.evt_id()}")
        print(f"rf.dataset = {rf.dataset}")
        print(f"rf.fullpath = {rf.fullpath}")

        # Put the output file into the template copy.
        replace_value("DUMMYFILENAME.root", output_rootfile, output_template)

        # Put the input root file into the template copy.
        replace_value("DUMMYFILELIST", rf.fullpath, output_template)
        # replace_value("DUMMYFILELIST", "", output_template)
        
        # Put the event ID into the template copy.
        # all_evt_ids = ','.join(evt_id_tup)
        replace_value("EVENTRANGE", rf.evt_id(), output_template)

        if "Run2018D" not in rf.dataset:
            replace_value('run_for_GT = "D"', 'run_for_GT = "ABC"', output_template)

        # cmd = f"cmsRun {output_template} > {output_txt}"
        cmd = f"cmsRun {output_template}"
        print(f"Executing:\n`{cmd}`")
        shell_cmd(cmd, outfile=output_txt)

if __name__ == "__main__":
    # main()
    dsf = DataSetFinder()
    # with open("delete_evt_id_rootfile.py", "w") as f:
    #     f.write("evt_id_rootfile_dct = {\n")

    #     for evt_id in evt_id_tup:
    #         run, lumisect, event = evt_id.split(":")
    #         rf = dsf.find_first_dataset_rootfile(run=int(run), lumisect=int(lumisect), event=int(event), dataset_tup=dataset_tup, outfile="pickevents.root")
    #         f.write(f"""    "{evt_id}" : "{rf.fullpath}",\n""")
    #     f.write("}\n")

    evt_lsoftup = get_list_of_tuples(get_list_of_lines(infile_txt_elisa_unique_3p1f))
    pprint(evt_lsoftup[:15])

    dct = {}
    for evt_id in evt_lsoftup[5:7]:
        run = evt_id[0]
        lumisect = evt_id[1]
        event = evt_id[2]
        rf = dsf.find_first_dataset_rootfile(run=run, lumisect=lumisect, event=event, dataset_tup=dataset_tup, outfile="pickevents.root")
        dct[rf.evt_id()] = rf.fullpath
    with open("delete_evt_id_rootfile_test01.json", "w") as f:
        # Prettify using indent.
        json.dump(dct, f, indent=4)
