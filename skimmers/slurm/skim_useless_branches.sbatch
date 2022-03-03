#!/bin/bash
#SBATCH --job-name=skimbranches_Data2016UL_preVFP
#SBATCH --output=/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/skimbranches_Data2016UL_preVFP.out
#SBATCH --error=/cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/output/skimbranches_Data2016UL_preVFP.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=08:00:00
#SBATCH --account=avery
#SBATCH --qos=avery-b
#SBATCH --mem=8gb
#SBATCH --partition=bigmem
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

echo 'Starting script...'
time root -l /cmsuf/data/store/user/t2/users/rosedj1/ZplusXpython/skimmers/skim_useless_branches.C

echo 'Script finished!'