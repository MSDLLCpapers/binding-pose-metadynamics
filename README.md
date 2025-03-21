# Binding Pose Metadynamics Conformational Stability Scoring
Python script to run binding pose metadynamics workflow to score conformational stability of macrocyclic peptides using Desmond in Schrodinger.

## Dependencies and Running Scripts
### Dependencies:
  - Schrodinger must be installed on the location in which this script is run. Versions tested 2023-1 and 2024-2.
  - The metadynamics_convergence_analysis.py script must be obtained from Schrodinger via help@schrodinger.com. Place in the src directory before running the scripts. Make sure script is named "metadynamics_convergence_analysis.py"
  - To run all scripts, $SCHRODINGER/run can be used. However, if you do not use $SCHRODINGER/run for the analysis_job.py script, make sure the following depencencies are installed.
 
  |Software|Version|
  |--------|-------|
  |python  | 3.7.12|
  |pandas  | 1.3.5 |
  |matplotlib| 3.5.1|
  |re      | 2.2.1|

### Running Script
- Generate .mae or .maegz file containing compounds to score and save to a working directory.
- In working directory, run:
  - $SCHRODINGER/run submit_jobs.py asl --HOST HOST
  - when jobs finish running, run $SCHRODINGER/run analyze_jobs.py

Gy default, HOST is set to localhost.

For help, run $SCHRODINGER/run submit_jobs.py -h

asl = atom selection language found in Schrodinger. Genearlly best to use SMARTS string.

## Repository Contents
- src: source directory containing all scripts and modules needed to run workflow:
  - submit_jobs.py: creates all desmond input files and submits jobs to hpc.
  - analyze_jobs.py: analyzes results of jobs submitted.
- tutorial: input files and some example output files for tutorial.
  -  mae file of input structures: SFTI-1.mae
  -  csv file of results: average_expectation_value_SFTI-1.csv
  -  svg file of results: average_expectation_value_SFTI-1.svg

## Tutorial SFTI-1 Dataset

Here, the schrodinger module used was Schrodinger/2023-1

Varying crosslinker in SFTI-1 macrocyclic peptide:

![SFTI-1_molecules](https://github.com/user-attachments/assets/094245dc-7cf9-424e-bfd1-b3942968b9e7)

Select all project table entries and export structures to a .mae or maegz file to working directory.

Select region that you would like to enhance the sampling of using binding pose metadynamics. Here, we are selecting the macrocycle ring of the SFTI-1 Peptides ('"SMARTS. N(\[*\])\[CX3\](=\[OX1\])C"').

![SFTI_molecule_highlight](https://github.com/user-attachments/assets/0c8c0a59-c822-4560-8fea-83d4fc7505e6)

Run the following in working directory:
1. $SCHRODINGER/run submit_jobs.py '"SMARTS. N(\[*\])\[CX3\](=\[OX1\])C"' --num_simulations 3 --manuscript_seeds
2. $SCHRODINGER/run analyze_jobs.py

Analysis output results as well as convergence analysis of simulations using Schrodingers Metadynamics Analysis Script (metadynamics_convergence_analysis.py)

Results:
1. average_expectation_values_SFTI-1.svg
2. average_expectation_values_SFTI-1.csv

Convergence analysis per trajectory (found in subdirectories e.g. cmp_1_bpm_job_1):
1.  Report.html

The "average_expectation_values_SFTI-1.svg" is a plot of the average expectation value of the RMSD of the selected region (here the macrocycle ring) from the input conformation per compound.

![average_expectation_values_SFTI-1](https://github.com/user-attachments/assets/1fada4b8-0167-40a8-9401-9d7244272a31)<?xml version="1.0" encoding="utf-8" standalone="no"?>

Compounds with low average expectation values are considered more stable. Compounds 1-3 are considered stable, while compounds 4-6 are considered unstable based on these results.

The data used to create the plot is contained in the "average_expectation_values_SFTI-1.csv" file.

The convergence of each simulation is monitored and generally described in the Report.html. We want to see that free energy surface produced smoothly converges and gaussian heights are small near the end of the simulation. Due to the nature of the CV selected in these calculations and the simulation settings, it is unlikely to see uniformly distributed probability distributions at the end of the simulation, as you will eventaully get stuck in a minima. Therefore, we do not expect to see uniformly distributed block probabilities or low average distances between the block probabilites reported in the "Report.html" file.
