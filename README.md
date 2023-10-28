
Hello and welcome! 

This is a code repository for the paper:
# Gamma-ray burst detection using Poisson-FOCuS and other trigger algorithms
_Authors: 
Giuseppe Dilillo, 
Kes Ward, 
Idris Eckley, 
Paul Fearnhead, 
Riccardo Crupi,
Yuri Evangelista,
Andrea Vacchi,
Fabrizio Fiore_

The paper deals with algorithms for detecting gamma-ray bursts. 


## Data

You can download the data used in this research from [Zenodo](https://doi.org/10.5281/zenodo.8334676).

## Setup

### Requirements
1. Python and few external packages, see section section "Environment creation".
2. To run the C code of this repository you will need cmake and a compiler (such as GCC).
3. A UNIX-like system or the patience to rewrite a few shell scripts. 

### 1. Download
First you must download the data and the present repository.
For downloading the data go to Zenodo link above and download all the files there,
from the page's bottom panel.
To clone the repository, you can use git. 
Run from your terminal at appropriate location:

`git clone https://github.com/peppedilillo/grb-trigger-algorithms.git`

If you have no git, you can download the repository clicking on the green
button on the top right of this page and then clicking on `Download zip`.

### 2. Environment creation
We provide an environment file to easily setup a python anaconda environment.
To install this environment, move to the repository's local folder and run:

`conda env create -f environment.yml`

If everything went fine you should now be able to see an environment called
`grb-trigger-algorithms` in your environment list, which you can get using
`conda env list`.

If you are not using anaconda you can still use  `environment.yml` to find all 
the packages needed to run the python code of this repo.

### 3. Everything in its right place 

Now we do put the data in their default location.
This will make it easier to run the scripts.
Move all the datasets you downloaded from Zenodo in the `grb-trigger-algorithm\data\`
data folder, then unzip the file `simulated_dataset_compeff.zip`.
The folder structure should look something like this:

```
grb-trigger-algorithm
|- .gitignore
|- environment.yml
|- README.md
|- grb-trigger-algorithm
| |- data
| | |- \README.md
| | |- simulated_dataset_grb180703949.fits
| | |- simulated_dataset_grb120707800.fits
| | |- gbm_dataset_20140101_20140108.zip
| | |- gbm_dataset_20171002_20171009.zip
| | |- gbm_dataset_20190601_20190608.zip
| | |- simulated_dataset_compeff
| | | |- pois_l4_n2048_0000.txt
| | | |- ..
```

### 4. Compiling the C implementations

We provide C implementations for Poisson-FOCuS and a benchmark algorithm emulating
the one from Fermi-GBM. To use this programs you need to compile them.
We provide CMake files for this purpose.

For compiling the C implementation of Poisson-FOCuS:
1. Move to `grb-trigger-algorithm/grb-trigger-algorithm/algorithms_c/pfocus_c/`
2. In there, create a directory called `cmake-build-debug` and another called `cmake-build-release`.
3. Move to the `cmake-build-debug` folder and (assuming cmake is in your PATH) run `cmake ..  -D CMAKE_BUILD_TYPE=Debug`.
4. Now run `cmake --build . --config Debug`.
3. Move to `../cmake-build-release` folder and run `cmake ..  -D CMAKE_BUILD_TYPE=Release`.
4. Now run `cmake --build . --config Release`.

This will create executables in you debug and release folders called `pfocus` and `pfocus_compeff`.
The debug versions will print a status string at each iteration.
Repeat the same for the benchmark, which is located in the folder `grb-trigger-algorithm/grb-trigger-algorithm/algorithms_c/benchmark/`.


You are set! 

## Running the experiments

### 1. Computational efficiency

We provide a shells script `compeff.sh` to automatically run the computational efficiency tests.
To run this script on mac move to the `grb-trigger-algorithms/grb-trigger-algorithms` folder and run:

`zsh compeff.sh`

This requires you to have set up the data (see section 1. and 3. of "Setup") and compiled the C implementations of Poisson-FOCuS and the GBM-like benchmark.
The results of these tests are stored in the folder `grb-trigger-algorithms/computational_efficiency/outputs`.
In the folder `grb-trigger-algorithms/computational_efficiency` you will also find a script `table.py` to parse these results into a latex table.

### 2. Tests on real data

This will run Poisson-FOCuS with exponential smoothing background assessment on one week of data from Fermi-GBM. The test analyzes data from all Fermi-GBM detectors, binned at 16 ms using a python implementation of Poisson-FOCuS, see `grb-trigger-algorithms/algorithms/pfocus_des.py`.
It will take some time. 
To run the test move to `grb-trigger-algorithms` with your terminal and run:

`python realdata.py`

The results from the experiment are saved in `grb-trigger-algorithms/real_data/logs`.

### 3. Detection performances

This experiment tests the computational performances of different python algorithms (see `grb-trigger-algorithms/algorithms`). 
To run the test move to the `grb-trigger-algorithms` folder with your terminal and run:

`python detperf.py`.

Results will be stored in `grb-trigger-algorithms/detection_performances/outputs`.
We also provide scripts to plot and table the results, see `plot.py` and `table.py` in `grb-trigger-algorithms/detection_performances/`.

## Other material
The folder `/grb-trigger-algorithms/visualization` contains the code used for creating the "checker plots" representing the operations of different algorithms (Figure 1 and Figure 2 of the paper).

We provide some non-code, non-data material with this repository.
These include:
* Annotated logs for our runs over Fermi data, for all periods considered in the paper.
  These files are located in the folder `/grb-trigger-algorithms/real_data/logs`.
* Plots for all the transients observed with Fermi-GBM which trigger Poisson-FOCuS and have no counterpart in official catalogs.
  These files are in the folder `/grb-trigger-algorithms/real_data/plots`.
* Results from our computational efficiency tests (in `/grb-trigger-algorithms/computationa_efficiency/outputs`)
  and latex tables (`/grb-trigger-algorithms/computationa_efficiency/tables`)
* Result tables for our statistical power tests (in `/grb-trigger-algorithms/detection_performances/tables`)

## Uninstalling

To uninstall delete the repository local folder.
If you installed our conda environment you can uninstall it with:

`conda remove -n grb-trigger-algorithms --all`

## Bibliography

The paper this repo buils on has yet to be published. 
I will update with a link as soon as we have it or a preprint out.

* Dilillo, G., et al. "Gamma-ray burst detection using Poisson-FOCuS and other trigger algorithms." _manuscript submitted for publication_ (2023).

* Ward, Kes, et al. "Poisson-FOCuS: An efficient online method for detecting count bursts with application to gamma ray burst detection." _Journal of the American Statistical Association_ (2023): 1-13.
