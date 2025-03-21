import pandas as pd
import matplotlib.pyplot as plt
import math
import os
import re
from module import *

kb = 1.987204259 * 10 ** -3
temp = 300

script_directory = os.path.dirname(os.path.abspath(__file__))
cwd = os.getcwd()
print(cwd)

for file in os.listdir():
    if file.endswith('.mae') or file.endswith('.maegz'):
        title = file.split('.')[0]

# convergence analysis
for file in os.listdir():
    if (os.path.isdir(file) and ('bpm_job' in file)):
        os.chdir(file)
        slices = 10
        dir_list = os.listdir()
        file_count = 0
        #check if all convergence analysis output files have been generated. If generated, skip calculations. 
        for file in dir_list:
            if file == 'Expectation_value_vs_Time.png':
                file_count += 1
        
        if file_count == (slices * 3 + 1):
            os.chdir(cwd)
            continue

        #iterate through filenames in current directory.
        for filename in dir_list: 
            # store the kerseq filename:    
            if filename.endswith("kerseq"):
                filename_kerseq = str(filename)
                
            if filename.endswith("out.cfg"):
                filename_cfg = str(filename)
        #open the kerseq file and count the number of filenames.    
        with open(filename_kerseq, 'r') as ker:
            count = 0
            for line in ker:
                # remove empty spaces
                if line != "\n":
                    count += 1
        # remove 5 header lines and remove every other line as bias potential deposited every other line.             
        first = int(((count - 5)/2)/15)
        last = int((count - 5)/2)
        interval = int(first)
        first = str(first)
        last = str(last)
        interval = str(interval)
        # divide by the invertal the expectation value is taken.
        print("$SCHRODINGER/run "+ script_directory + "/metadynamics_convergence_analysis.py -i " + filename_cfg + " -d " + filename_kerseq + " -o  metadynamics_analysis -s "  + first + ":" + last + ":" + interval)
        os.system("$SCHRODINGER/run "+ script_directory + "/metadynamics_convergence_analysis.py -i " + filename_cfg + " -d " + filename_kerseq + " -o  metadynamics_analysis -s "  + first + ":" + last + ":" + interval)
        os.chdir(cwd)

for file in os.listdir():
    if os.path.isdir(file) and ('bpm_job' in file):
        os.chdir(file)
        #check if analysis had alredy been run. If so, go to next directory. 
        finished = False
        for f in os.listdir():
            if 'Expectation_value_vs_Time.png' == f:
                finished = True
        if finished == True:
            os.chdir(cwd)
            continue
        else:
            dir_list = os.listdir()
            sub_strings_filename_1 = '_'
            sub_strings_filename_2 = '.'
            sub_strings_filename_3 = 'is_'

            # Loop through file names containing free energies over indicated intervals. Store intervals in increment variable and store current .fes file being read as a dataframe. Store all data from dataframes into the fes_dataframe.

            all_dataframe=pd.DataFrame()
            fes_dataframe = pd.DataFrame()
            prob_dataframe = pd.DataFrame()
            incr_list = []

            prob_file_in_list = []

            for file in dir_list:    
                if file.endswith('.prob'):
                    prob_file_in_list.append(True)
                else:
                    prob_file_in_list.append(False)

            if any(prob_file_in_list):
                prob_data = True
            else:
                prob_data = None
                    
            for filename in dir_list:
                if filename.endswith(".fes") and filename.startswith("freeenergy"):
                    index1 = filename.index(sub_strings_filename_1)
                    index2 = filename.index(sub_strings_filename_2)
                    increment = filename[index1 + 1: index2]
                    incr_list.append(increment)
                    dataframe = pd.read_csv(filename, delimiter=' ', names=['RMSD', 'Free Energy'], skiprows=5)
                    fes_dataframe['Free Energy ' + increment] = dataframe['Free Energy']
                    
                    
                if filename.endswith(".fes") and filename.startswith("aligned"):
                    index1 = filename.index(sub_strings_filename_1)
                    index2 = filename.index(sub_strings_filename_2)
                    increment = filename[index1 + 1: index2]
                    incr_list.append(increment)
                    dataframe = pd.read_csv(filename, ' ', names=['RMSD', 'Free Energy'], skiprows=5)
                    fes_dataframe['Free Energy ' + increment] = dataframe['Free Energy']
                    
                if filename.endswith(".prob"):
                    index1 = filename.index(sub_strings_filename_3)
                    index2 = filename.index(sub_strings_filename_2)
                    increment = filename[index1 + 3: index2]
                    dataframe = pd.read_csv(filename, ' ', names=['RMSD', 'Probability'], skiprows=5)
                    prob_dataframe['Probability ' + increment] = dataframe['Probability']
                    
                if filename.endswith(".kerseq"):
                    input_file_1 = str(filename)
                    
            fes_dataframe['RMSD'] = dataframe['RMSD']
                    
            if prob_data != None:
                prob_dataframe['RMSD'] = dataframe['RMSD']

            #Plot the free energy vs time.


            fes_dataframe_columns_list = fes_dataframe.columns.values.tolist()
            if prob_data != None:
                prob_dataframe_columns_list = prob_dataframe.columns.values.tolist()

            #Rearrange data in fes_dataframe for ploting

            incr_list_int = list(map(int, incr_list))
            incr_list_int.sort()
            fes_dataframe_sorted = pd.DataFrame()
            prob_dataframe_sorted = pd.DataFrame()
            fes_dataframe_sorted['RMSD'] = fes_dataframe['RMSD']
            if prob_data != None:
                prob_dataframe_sorted['RMSD'] = prob_dataframe['RMSD']
            for incr in incr_list_int:
                fes_dataframe_sorted['Free Energy ' + str(incr)] = fes_dataframe['Free Energy ' + str(incr)]
                if prob_data != None:
                    prob_dataframe_sorted['Probability' + str(incr)] = prob_dataframe['Probability ' + str(incr)]
                
            fes_dataframe_sorted.to_csv()
            prob_dataframe_sorted.to_csv()

            # Create dataframe for .kerseq file and drop rows which do not update the fes. Rest the index of the dataframe. Store time

            kerseq_dataframe = pd.read_csv(input_file_1, skiprows = 5, sep = '    ', engine = 'python', names = ['Time', 'Height', 'Center', 'Width'])
            kerseq_dataframe.drop(kerseq_dataframe[kerseq_dataframe['Height'] == 0].index, inplace=True)
            kerseq_dataframe.reset_index(drop=True, inplace = True)

            time_list = []

            for incr in incr_list_int:
                time_list.append(float(kerseq_dataframe['Time'][incr]))

            num = 1000
            time_list_ns = [round(i/num, 2) for i in time_list]


            # Plot Free energy vs Backbone RMSD vs Time ns

            fes_dataframe_sorted_column_list = fes_dataframe_sorted.columns.values.tolist()

            for column in fes_dataframe_sorted_column_list[1:]:
                plt.plot(fes_dataframe_sorted['RMSD'],fes_dataframe_sorted[column], 'o-')

            plt.title('Free energy vs. Backbone RMSD')
            plt.xlabel('Backbone RMSD (Angstroms')
            plt.ylabel('Free energy (kcal/mol)')
            plt.legend(time_list_ns, bbox_to_anchor=(1.02, 1.1), loc='upper left', title='Time (ns)')
            plt.tight_layout()
            plt.savefig('growing_fes_v2.png')
            plt.clf()


            # Plot Probability vs Backbone RMSD vs Time ns

            prob_dataframe_sorted_column_list = prob_dataframe_sorted.columns.values.tolist()

            for column in prob_dataframe_sorted_column_list[1:]:
                plt.plot(prob_dataframe_sorted['RMSD'],prob_dataframe_sorted[column], 'o-')

            if prob_data != None:
                plt.title('Probability vs. Time')
                plt.xlabel('Backbone RMSD (Angstroms)')
                plt.ylabel('Free energy (kcal/mol)')
                plt.legend(time_list_ns, bbox_to_anchor=(1.02, 1.1), loc='upper left', title='Time (ns)')
                plt.tight_layout()
                plt.savefig('probability_overlay_v2.png')
                plt.clf()


            # Plot the expectation value vs time.

            expectation_value_sum_df = pd.DataFrame()
            expectation_value_df = pd.DataFrame()
            probability_df = pd.DataFrame()
            probability_list = []
            p_list = []
            q_list = []
            expectation_value_list = []
            expectation_value_sum = []

            # Calculate expectation value over time using the boltzmann distribution. For the values (free energy per CV) inside each column of the dataframe, calculate the numerator and denominator of the porbability (p and q) where q is the partition function. After p and q are computed for the column, calculate the probability of each unit of the CV in the column. Then calculate the expecation value per CV unit. Then sum the expectation values and append to the expecation value sum dataframe. 

            for column in fes_dataframe_sorted_column_list[1:]:
                for value in fes_dataframe_sorted[column]:
                    p = math.exp(-1 * (value / (kb * temp)))
                    p_list.append(p)
                q = sum(p_list)
                i = 0
                for value in p_list:
                    probability = value/q
                    probability_list.append(probability)
                    expectation_value_list.append(probability * fes_dataframe_sorted['RMSD'][i])
                    i += 1
                probability_df[column] = probability_list
                expectation_value_df[column] = expectation_value_list
                expectation_value_sum.append(sum(expectation_value_df[column]))
                probability_list.clear()
                expectation_value_list.clear()
                p_list.clear()
                    
            expectation_value_sum_df['expectation_value_sum (Angstroms)'] = expectation_value_sum
            expectation_value_sum_df['time (ns)'] = time_list_ns

            expectation_value_sum_df.to_csv('expect_val_vs_time.csv')

            # Plot the expectation value vs time. 

            plt.plot(expectation_value_sum_df['time (ns)'], expectation_value_sum_df['expectation_value_sum (Angstroms)'], 'o-')

            #for x, y in zip(time_list_ns, expectation_value_sum):
            #    label = "{:.3f}".format(y)
            #    plt.annotate(label, (x,y), textcoords='offset points', xytext=(0, 10), ha='center')

            plt.title('Expectation value vs Time (ns)')
            plt.xlabel('Time (ns)')
            plt.ylabel('Expectation Value (Angstroms)')
            plt.tight_layout()
            plt.savefig('Expectation_value_vs_Time.png')
            plt.clf()
            os.chdir(cwd)
seeds = []
filenames = []
for file in os.listdir():
    if 'bpm_job' in file:
        seeds.append(file.split('_bpm_job_')[-1])
    if ('.mae' in file) or ('maegz' in file):
        filenames.append(file.split('.')[0])

# removed redundant strings from list.
seeds = sorted(list(set(seeds)))

# create dataframe with seeds as index
collected_df = pd.DataFrame(index=seeds)

#create lists to store filenames for naming of dataframes columns
cmp_filenames = []

# iterate through seed directories and append expectation values to dataframe with filenames as column titles. 
i = 0
for file in sorted(os.listdir(), key=natural_keys):
    if (os.path.isdir(file)) and ('bpm_job' in file):
        os.chdir(file)
        cmp_filenames.append(file)
        if 'expect_val_vs_time.csv' in os.listdir():
            exp_df = pd.read_csv('expect_val_vs_time.csv')
            collected_df.loc[cmp_filenames[-1].split('_bpm_job_')[-1], cmp_filenames[-1].split('_bpm_job_')[0] + ' ExpVal RMSD (A)'] = exp_df['expectation_value_sum (Angstroms)'].iloc[-1]
            os.chdir('..')
        else:
            plot_df.at[name,file[-5:]] = np.nan
            os.chdir('..')
            continue
    i += 1
                    
os.chdir(cwd)

# calculate average expectation value and standard deviation of average expectation value calculated. 
collected_df.loc['Average ExpVal RMSD (A)'] = collected_df.mean()
collected_df.loc['Standard Deviation ExpVal RMSD (A)'] = collected_df.loc[seeds].std()
collected_df.to_csv('average_expectation_value_' + title +'.csv')

# grab average expectation values and standard deviations to plot expectation values
row = collected_df.loc[['Average ExpVal RMSD (A)', 'Standard Deviation ExpVal RMSD (A)' ]]
row_list = []
i = 0

# plot the the average expectation value and standard deviation per structure. 
for df in row.values:
    row_list.append(df.tolist())
    i += 1
filenames_list = []
for values in collected_df.columns.values.tolist():
    i = 0
    for a in values.split()[0][::-1]:
        if a.isdigit(): 
            i += 1
        if a.isdigit() == False:
            b = values.split()[0][-i:]
            i = 0
            break

    filenames_list.append(b)
fig_width = (collected_df.shape[1]) * 0.75

if fig_width < 5:
    fig_width = 5

plt.figure(figsize=(fig_width, 5))
plt.errorbar(range(len(row_list[0])), row_list[0],yerr=row_list[1], fmt='o', c='teal', capsize=5)
plt.xticks(range(len(row_list[0])), filenames_list) 
plt.title('Average Expectation Value RMSD (A)')
plt.xlabel('Compound Label')
plt.ylabel('Average Expectation Value RMSD (A)')
plt.savefig('average_expectation_values_' + title +'.svg')