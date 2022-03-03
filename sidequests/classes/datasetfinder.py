import warnings
from sidequests.classes.rootfileevent import RootFileEvent
from Utils_Python.Commands import shell_cmd

class DataSetFinder:

    def __init__(self):
        pass

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
        try:
            results = shell_cmd(
                        f"edmPickEvents.py {dataset} {run}:{lumisect}:{event} --output={outfile}",
                        get_stdout=True
                        )
        except IndexError:
            print("Did you do `voms-proxy-init`?")
            raise IndexError("list index out of range")
        return results.stdout
                    
    def parse_stdout(self, stdout):
        """
        Return the str after 'inputFiles=', such as the following:
        
        edmCopyPickMerge outputFile=pickevents.root \\
          eventsToProcess=321834:126135620 \\
          inputFiles=/store/data/Run2018D/MuonEG/MINIAOD/PromptReco-v2/000/321/834/00000/4C96D92F-3AAE-E811-80D4-FA163E9D5E27.root
        """
        if "inputFiles=" not in stdout:
            warnings.warn('"inputFiles=" not found in stdout.')
            return ""
        return stdout.split("inputFiles=")[1].rstrip("\n")
  
    def find_first_dataset_rootfile(self, run, lumisect, event, dataset_tup, outfile="pickevents.root"):
        """
        Search `dataset_tup` for the first data set containing:
            `run`, `lumisect`, `event`.

        Returns a `RootFileEvent` object, which stores this info:
        
        RootFileEvent.run : int
        RootFileEvent.lumisect : int
        RootFileEvent.event : int
        RootFileEvent.dataset : str
            The data set found which contains `run`, `lumisect`, `event`.
        RootFileEvent.rootfile : str
            The root file found in `dataset` which contains `run`, `lumisect`, `event`.
        """
        rf = RootFileEvent()
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