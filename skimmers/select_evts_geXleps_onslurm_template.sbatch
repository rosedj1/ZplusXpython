#!/bin/bash
#SBATCH --job-name=NAME
#SBATCH --output=LOGDIR/NAME.out
#SBATCH --error=LOGDIR/NAME.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=06:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
#SBATCH --mem=6gb
#SBATCH --partition=hpg2-compute
#SBATCH --nodes=1

pwd; hostname; date
source ~/.bash_profile
conda activate my_root_env

cd /cmsuf/data/store/user/t2/users/rosedj1/HiggsMassMeasurement/
source setup.sh
cd /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/
source setup_hpg.sh
echo 'Packages loaded.'

echo 'Checking for valid GRID cert...'
export X509_USER_PROXY=/cmsuf/data/store/user/t2/users/rosedj1/myproxy
export X509_CERT_DIR=/cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/certificates

# Code here.
python NEW_PYSCRIPT > LOGDIR/NAME.txt

echo 'Script finished!'
