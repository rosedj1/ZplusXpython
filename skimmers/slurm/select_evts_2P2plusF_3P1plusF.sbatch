#!/bin/bash
#SBATCH --job-name=redbkgest_2018UL_ZZ
#SBATCH --output=redbkgest_2018UL_ZZ.out
#SBATCH --error=redbkgest_2018UL_ZZ.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=04:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
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
cd skimmers/
time python select_evts_2P2plusF_3P1plusF.py > output/redbkgest_2018UL_ZZ.txt

echo 'Script finished!'