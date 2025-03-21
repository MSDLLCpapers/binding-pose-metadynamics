import shutil
import pandas as pd
import time as tm
import sys
import os
import argparse
import time
import glob
import random

from module import *

from schrodinger import structure

script_directory = os.path.dirname(os.path.abspath(__file__))
print(script_directory)

# get settings for input files
parser = argparse.ArgumentParser(description='Create input files and submit jobs of binding pose metadynamics.') 
parser.add_argument('asl', type=str, help='SMILES selection for CV.') 
parser.add_argument('--work_dir', type=str, default='.', help='Working directory.') 
parser.add_argument('--host', type=str, default='localhost', help='Host to submit job.')
parser.add_argument('--custom_ff', type=str, default=None, help='Use custom OPLS forcefield (Y/N). Usually located $HOME/.schrodinger/opls_dir/') 
# metadynamics settings
parser.add_argument('--kTemp', type=str, default='1.7', help='kTemp value in kcal/mol.') 
parser.add_argument('--g_height', type=str, default='0.3', help='Gaussian height setting.') 
parser.add_argument('--g_width', type=str, default='0.1', help='Gaussian width setting.') 
parser.add_argument('--g_interval', type=str, default='0.09', help='Gaussian deposition interval.')
#simulation settings
parser.add_argument('--time', type=int, default='10', help='Time of simulation in ns.') 
parser.add_argument('--num_simulations', type=int, default=6, help='Number of simulations to run per compound.') 
parser.add_argument('--interval_frames', type=str, default='10', help='Interval for writing frames of trajectory.')
parser.add_argument('--manuscript_seeds', action='store_true', help='Use manuscript seeds.')

args = parser.parse_args()
args.time = str(args.time * 1000)

seeds_file_exists = False
for file in os.listdir():
    if file == 'seeds.csv':
        seeds_file_exists = True
        
if seeds_file_exists:
    seeds = pd.read_csv('seeds.csv')['seeds'].tolist()
    
else:
    if args.manuscript_seeds:
        seeds = [2007, 6950, 5092, 3007, 1950, 7092, 8592, 4207, 9850, 3492]
    else:
        seeds = []
        for i in range(args.num_simulations):
            seeds.append(random.randint(1, 10000))
        seed_df = pd.DataFrame(seeds, columns=['seeds'])
        seed_df.to_csv('seeds.csv')

# change directory to cwd
os.chdir(args.work_dir)
cwd = os.path.abspath(args.work_dir)
print(cwd)

filename = get_filename_mae()

# make directories and extract structures to create .cms files.
mae_files = []
titles = []
jobs_in_dir = []
all_titles = []
all_jobs = []
dirs_in_directory = False

existing_dirs = []

# get list of directories in working directory
for file in os.listdir():
    if os.path.isdir(file):
        dirs_in_directory = True
        filename_file = open('mae_file.txt', 'r')
        filename = filename_file.read()
        break

if dirs_in_directory == False:
    filename = get_filename_mae()
    filename_file = open('mae_file.txt', 'w')
    filename_file.write(filename)
    filename_file.close()

with structure.StructureReader(filename) as reader:
    num_structures = 0
    for st in reader:
        all_titles.append(st.property.get('s_m_title').replace(" ", "_"))
        for file in os.listdir():
            if all_titles[num_structures] in file and os.path.isdir(file):
                all_jobs.append(file)
        num_structures += 1

if dirs_in_directory == False:
    i = 0
    with structure.StructureReader(filename) as reader:
        for st in reader:
            value = 1
            titles.append(st.property.get('s_m_title').replace(" ", "_"))
            with structure.StructureWriter(titles[i]+ '.maegz') as writer:
                writer.append(st)
                mae_files.append(titles[i]+ '.maegz')
            while value <= int(args.num_simulations):
                job_title = titles[i] + '_bpm_job_' + str(value)
                all_jobs.append(job_title)
                if job_title in os.listdir():
                    jobs_in_dir.append(job_title)
                    value += 1
                    continue
                else:
                    os.mkdir(job_title)
                    jobs_in_dir.append(job_title)
                    value += 1
            i += 1
        
    value = value - 1
    # correct for increment at end of loop

    #check if all .cms files have been created. If not, continue to create cms files. Wait for all .cms files to be created. Then copy files to working directories. 
    i = 0
    cms_files = glob.glob('*.cms')
    if (len(cms_files) != len(mae_files)) or (value < args.num_simulations):
        for file in mae_files:
            if args.custom_ff:
                os.system('"${SCHRODINGER}/utilities/multisim" -JOBNAME desmond_setup_' + titles[i] + ' -m ' + script_directory + '/msj_files/desmond_setup.msj ' + file + ' -o ' + titles[i] + '_desmond_setup-out.cms -OPLSDIR ' + args.custom_ff + ' -HOST localhost -TMPLAUNCHDIR')
                print(file, " finished custom")
            else:
                os.system('"${SCHRODINGER}/utilities/multisim" -JOBNAME desmond_setup_' + titles[i] + ' -m ' + script_directory + '/msj_files/desmond_setup.msj ' + file + ' -o ' + titles[i] + '_desmond_setup-out.cms -HOST localhost -TMPLAUNCHDIR')
                print(file, " finished")
            i += 1
        while len(cms_files) < len(mae_files):
            time.sleep(5)
            cms_files = glob.glob('*.cms')
        else:
            print("Copying files to working directories.")
            files = []
            i = 0
            for title in titles:
                files.append([])
                for file in os.listdir():
                    if (title in file) and (not os.path.isdir(file)):
                        files[i].append(file)
                i += 1
            # copy all files to directory with matching title to files
            i = 0
            for title in titles:
                for job in jobs_in_dir:
                    if (title in job):
                        for file in files[i]:
                            shutil.copy(file, job)
                            
                i += 1
            # remove files after they were copied.
            for l in files:
                for file in l:
                    os.remove(file)
            #create .cfg file and msj file
            value = 1
            i = 0
            for job in jobs_in_dir:
                msj = os.path.join(job + '/' + titles[value - 1] + '_desmond_metadynamics.msj')
                cfg = os.path.join(job + '/' + titles[value - 1] + '_desmond_metadynamics.cfg')
                create_msj_file(msj, args.kTemp, args.asl, args.g_height, args.g_width, args.g_interval)
                create_cfg_file(cfg, seeds[i], args.time, args.interval_frames)
                i += 1
                if i == args.num_simulations:
                    value += 1
                    i = 0

value = 1
if dirs_in_directory == True:
    titles = all_titles
    
#submit jobs that were not already submitted. 
for job in all_jobs:
    os.chdir(job)
    out_cms = None
    for file in os.listdir():
        if file.endswith('.msj'):
            msj = file
        if file.endswith('.cfg'):
            cfg = file
        if file.endswith('.cms'):
            cms = file
        #check if job has already been submitted. 
        if file.endswith('metadynamics-out.cms') or file.startswith('.'):
            out_cms = file
            continue
    if out_cms:
        print('skipping job due to presence of ' + out_cms + ' file')
        pass
    else:
        os.system("${SCHRODINGER}/utilities/multisim -JOBNAME " + job  + " -HOST " + args.host + " -maxjob 1 -cpu 1 -m " + msj + " -c " + cfg + " -description Metadynamics " + cms + " -mode umbrella -o " + titles[value - 1] + "_desmond_metadynamics-out.cms")
        print("${SCHRODINGER}/utilities/multisim -JOBNAME " + job  + " -HOST " + args.host + " -maxjob 1 -cpu 1 -m " + msj + " -c " + cfg + " -description Metadynamics " + cms + " -mode umbrella -o " + titles[value - 1] + "_desmond_metadynamics-out.cms")
    if value > args.num_simulations:
        value += 1
    os.chdir(cwd)
        
