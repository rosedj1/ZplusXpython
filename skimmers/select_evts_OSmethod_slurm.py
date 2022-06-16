import os
from sidequests.data.filepaths import (
    # data_2016_UL_ge4lepskim, data_2017_UL_ge4lepskim, data_2018_UL_ge4lepskim,
    # mc_2016_UL_DY_ge4lepskim, mc_2017_UL_DY_ge4lepskim, mc_2018_UL_DY_ge4lepskim,
    # mc_2016_UL_TT_ge4lepskim, mc_2017_UL_TT_ge4lepskim, mc_2018_UL_TT_ge4lepskim,
    # mc_2016_UL_WZ_ge4lepskim, mc_2017_UL_WZ_ge4lepskim, mc_2018_UL_WZ_ge4lepskim,
    # mc_2016_UL_ZZ_ge4lepskim, mc_2017_UL_ZZ_ge4lepskim, mc_2018_UL_ZZ_ge4lepskim,
    # fakerates_WZremoved_2016_UL_woFSR,
    # fakerates_WZremoved_2017_UL_woFSR,
    # fakerates_WZremoved_2018_UL_woFSR
    fakerates_WZremoved_2016_UL_woFSR_preVFP,
    fakerates_WZremoved_2016_UL_woFSR_postVFP,
    #=== 2016 ===#
    data_2016_UL_preVFP_ge4lepskim,  data_2016_UL_postVFP_ge4lepskim,
    mc_2016_UL_preVFP_DY_ge4lepskim, mc_2016_UL_postVFP_DY_ge4lepskim,
    mc_2016_UL_preVFP_TT_ge4lepskim, mc_2016_UL_postVFP_TT_ge4lepskim,
    mc_2016_UL_preVFP_WZ_ge4lepskim, mc_2016_UL_postVFP_WZ_ge4lepskim,
    mc_2016_UL_preVFP_ZZ_ge4lepskim, mc_2016_UL_postVFP_ZZ_ge4lepskim
    )
from constants.analysis_params import (
    dct_xs_jake,
    LUMI_INT_2016_UL_preVFP, LUMI_INT_2016_UL_postVFP,
    LUMI_INT_2016_UL, LUMI_INT_2017_UL, LUMI_INT_2018_UL,
    # dct_sumgenweights_2016_UL,
    dct_sumgenweights_2016_UL_preVFP, dct_sumgenweights_2016_UL_postVFP,
    dct_sumgenweights_2017_UL,
    dct_sumgenweights_2018_UL
    )
from Utils_Python.SlurmManager import SLURMSubmitter
from Utils_Python.Utils_Files import make_dirs
from sidequests.classes.templatemanager import TemplateManager

# This script runs only over 1 year each time.
year = 2016
LUMI = LUMI_INT_2016_UL_postVFP
dct_sumgenwgts = dct_sumgenweights_2016_UL_postVFP
infile_fakerates = fakerates_WZremoved_2016_UL_woFSR_postVFP
dct_xs = dct_xs_jake
dct_infile_name = {
    'Data' : data_2016_UL_postVFP_ge4lepskim,
    'DY50' : mc_2016_UL_postVFP_DY_ge4lepskim,
    'TT'   : mc_2016_UL_postVFP_TT_ge4lepskim,
    'WZ'   : mc_2016_UL_postVFP_WZ_ge4lepskim,
    'ZZ'   : mc_2016_UL_postVFP_ZZ_ge4lepskim,
}

break_at = -1
print_every = 100_000
overwrite = 0
verbose = 1

py_template = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpythonDELETE/ZplusXpython/skimmers/select_evts_OSmethod_multiquartetperevt_template.py"
outdir_logfiles  = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/"
outdir_rootfiles = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/rootfiles/redbkgskim/"
outdir_json = "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/json/"

# Don't include nickname or year.
prefix = "skim_osmethod_perfectxBFsync"
suffix = "postVFP"  # Don't add a leading underscore.

for d in (outdir_rootfiles, outdir_logfiles, outdir_json):
    make_dirs(d)

slurm = SLURMSubmitter(
    prescript_text='pwd; hostname; date',
    verbose=True
    )

# Create and submit a SLURM script for each infile.
for name, infile in dct_infile_name.items():

    job_name = f"{prefix}_{name}_{year}_{suffix}".rstrip("_")
    filepath_slurm_script = os.path.join(
        outdir_logfiles, f"{job_name}.sbatch"
        )

    print("Duplicating and updating python template.")
    tm = TemplateManager(input_template=py_template)
    # Place new template in log dir.
    # "/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/"

    basename = os.path.basename(py_template)
    new_template_path = os.path.join(
        outdir_logfiles, basename.replace(".py", f"_{job_name}.py")
        )
    tm.duplicate_template(
        output_template=new_template_path,
        overwrite=overwrite
        )
    tm.replace_vals(
        new_template_path,
        REPLACE_NAME=name,
        REPLACE_FILE=infile,
        REPLACE_YEAR=year,
        REPLACE_LUMI=LUMI,
        REPLACE_DCT_SUMGENWGTS=dct_sumgenwgts,
        REPLACE_DCT_XS=dct_xs,
        REPLACE_FAKERATE_INFILE=infile_fakerates,
        REPLACE_PREFIX=prefix,
        REPLACE_SUFFIX=suffix,
        REPLACE_OUTDIR_ROOTFILES=outdir_rootfiles,
        REPLACE_OUTDIR_JSON=outdir_json,
        REPLACE_BREAK_AT=break_at,
        REPLACE_PRINT_EVERY=print_every,
        )

    cmds_in_slurm_script = f"""
        source ~/.bash_profile
        conda activate my_root_env

        cd /cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/
        source setup.sh
        cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpythonDELETE/ZplusXpython/
        source setup_hpg.sh
        echo 'Packages loaded.'

        echo 'Checking for valid GRID cert...'
        export X509_USER_PROXY=/cmsuf/data/store/user/t2/users/rosedj1/myproxy
        export X509_CERT_DIR=/cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/certificates

        echo 'Starting script...'
        python {new_template_path} {'-x' if overwrite else ''} {'-v' if verbose else ''}
        """

    slurm.prep_directives(
        job_name=job_name,
        output_txt=os.path.join(outdir_logfiles, f"{job_name}.out"),
        email="rosedj1@ufl.edu",
        time="04:00:00",
        acct="avery",
        burst=False,
        mem=(4, "gb"),
        partition="hpg2-compute", #"bigmem",
        nodes=1
        )
    slurm.make_slurm_script(
        slurm_outpath=filepath_slurm_script, cmdstr=cmds_in_slurm_script,
        overwrite=overwrite
        )
    slurm.submit_script(filepath_slurm_script)
