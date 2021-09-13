import json
from collections import OrderedDict

class YieldCollector:
    def __init__(self):
        self.d = OrderedDict()
        self.yield_str = ""

    def add_yield_info(self, fs_code, relmass4lErr_bin_str, yield_val):
        """Add yield info to `self.d`."""
        key = f'redbkg_{fs_code}_{relmass4lErr_bin_str}'
        self.d[key] = float(f"{yield_val:.6f}")

    def make_yield_str(self):
        """Make and store `self.yield_str` info.
        
        Format: 
        redbkg_1_A : 6.616000,
        """
        self.yield_str = f"red_bkg_norm = {json.dumps(self.d, indent=4)}\n"

    def write_txt(self, outpath):
        """Write a txt file of yields to `outpath`."""
        with open(outpath, "w") as outf:
            outf.write(self.yield_str)
        print(f"Yields written to:\n  {outpath}")