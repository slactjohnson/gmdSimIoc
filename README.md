# gmdSimIoc
## Summary
Repository for a simulated X(GMD) device.

This repository contains a simple simulation IOC for the LCLS (X)GMD devices using [Caproto](https://github.com/caproto/caproto). 

The IOC takes an input .csv file of array data and will continuously loop through the supplied data. Additional controls are discussed below.

## Usage
### Starting the IOC
The python environment requires that you have [Caproto](https://github.com/caproto/caproto) available, as well as numpy. In the LCLS ECS environment you can get a conda environment with these requirements and more by running:
```bash
source /cds/group/pcds/pyps/conda/py36env.sh
```
Once you have the proper environment you can run the IOC and supply a data file. For example:
```bash
./gmdSimIoc.py --datafile good_xgmd_electron.csv
```

### Using the IOC
You can see all of the available PVs by adding --list-pvs to the above start command:
```bash
./gmdSimIoc.py --datafile good_xgmd_electron.csv --list-pvs 
```
A simple EDM screen is provided in the repository. This screen can be launched (assuming you have access to EDM in your environment) using the included shell script:
```bash
./gmdSimScreen.sh
```

### Using your own data
There are a few datafiles relevant to the (X)GMD that are provided in the repository, but you could use other data from (X)GMD experiments. There is a helper script included for creating files that can be read by the IOC using the LCLS psana system. To use this script you will need to be logged into an LCLS psana machine and have the LCLS-II psana environment. Example below:
```bash
ssh psana
source /cds/sw/ds/ana/conda2/manage/bin/psconda.sh
```
The script takes four arguments: experiment, run number, detector name, and the output .csv file name. Example:
```bash
./make_test_data.py tmo43218 28 xgmdstr0 my_output_file.csv
```
