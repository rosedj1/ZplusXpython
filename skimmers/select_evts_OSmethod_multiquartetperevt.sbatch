#!/bin/bash
#SBATCH --job-name=select_evts_2P2FplusF_3P1plusF_redbkgest_UL_WZxs5p26pb_ge4lepskim_2p2fsync_2016_ZZ
#SBATCH --output=output/select_evts_2P2FplusF_3P1plusF_redbkgest_UL_WZxs5p26pb_ge4lepskim_2p2fsync_2016_ZZ.out
#SBATCH --error=output/select_evts_2P2FplusF_3P1plusF_redbkgest_UL_WZxs5p26pb_ge4lepskim_2p2fsync_2016_ZZ.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rosedj1@ufl.edu
#SBATCH --time=06:00:00
#SBATCH --account=avery
#SBATCH --qos=avery
#SBATCH --mem=4gb
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

echo 'Starting script...'
cd skimmers/
time python select_evts_OSmethod_multiquartetperevt.py -x > output/select_evts_2P2FplusF_3P1plusF_redbkgest_UL_WZxs5p26pb_ge4lepskim_2p2fsync_2016_ZZ.txt

echo 'Script finished!'