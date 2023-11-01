# --- VERSION 0.2.0 updated 20231026 by JKW ---

import os
import pandas as pd

#import make_pdf as mk_pdf

output_sep = '------------------------'

print(output_sep)

# output folders will be named with this stem
output_name = input("Enter a name for this blimp run: ") # e.g., the date, '2018_runs', etc.
multi_session = input("How many separate analyses would you like to run? (integer number)\n")
n_sessions = int(multi_session)

######### Let user upload multiple sessions and analyze them separately.
# data structure should be something like:

'''
data = {'first_set': dir_with_first_set_of_runs,
		'second_set': dir_with_second_set_of_runs,
		'third_set': dir_with_third_set_of_runs}

and in each dir_with_nth_set_of_runs, you should have your data folders for
all the runs from that set that you want to analyze together.
'''

datasets = {}
i = 0 # at least one session
while i < n_sessions:
	session_name = input("Enter a name for session/analysis %i: " %i)
	session_dir = input("Drag directory containing all data folders for analysis %i into terminal.\n" %i)
	datasets[session_name] = session_dir
	i+=1

# don't use project stuff anymore
# proj = input("Enter name of project:")
# if os.path.isdir(Path.cwd().parents[0] / 'proj' / proj):
# 	dir_path = Path.cwd().parents[0] / 'proj' / proj
# else:
# 	print('Project name does not exist in directory. Try again.')
# 	exit()

####### Julia: need to go to blimp_supp soon.
# My hacky way of telling the blimp_supp module what the name of the project is...
# with open('proj.txt', 'w') as f:
#     f.write(proj)

# os.chdir(dir_path)

# User drags params file into terminal to load it.
# def define_params_location():
# 	'''
# 	user defines where params file is located
# 	'''
# 	params_dir = input("Drag params.xlsx file into terminal, then press enter:\n")
# 	return params_dir

# params = define_params_location()

# why does this import happen so late?
import blimp_supp as b_s



# Create results and plot directories if they do not already exist
######## TO DO: create different folders for each session/analysis
# should be something like:
# for set in datasets:
# 	-> create folders
rd_path = Path.cwd() / 'raw_data'
results_path = Path.cwd() / ('results') # do the parentheses do anything? I don't think so. 
plot_path = Path.cwd() / ('plots')

if os.path.isdir(results_path):
	pass 
else:
	os.mkdir(results_path)

if os.path.isdir(plot_path):
	pass 
else:
	os.mkdir(plot_path)

d47_crunch_fmt = []
batch_data_list = []
fold_count = 0

# Find which analyses to remove analyses (based on params file)
# df_rmv = pd.read_excel('params.xlsx', 'Remove')
# df_rmv = pd.read_excel(params, 'Remove') # new syntax with params file found in separate dir now.
# manual_rmv = list(df_rmv.UID)

# Now do this in blimp_supp
manual_rmv = find_analyses_to_remove()

run_type = 'clumped'
print(output_sep) #------------------------#


################################# ADD FOLDER SYSTEM HERE
# User tells blimp which sessions to run
# Then runs the sessions independently
# Probably move most of the code below into a function and call that function however many times as needed
# Will probably have to adjust the results and plots folders too.
################################# DONE FOR NOW

if os.path.isdir(rd_path): # If there is a raw data folder...
	print('Crunching folders: ')
	
	for folder in os.listdir(rd_path):
		if os.path.isdir(rd_path / folder):
			print(folder) # if the item you find is a directory, continue, else break the loop and go to the next. This helps with '.DS_store' and other random files		
	
			if 'clumped' in folder or 'Clumped' in folder:
				run_type = 'clumped'
			elif 'standard' or 'Standard' in folder:
				run_type = 'standard'
			else:
				print('***Run type (standard or clumped) not defined. Add run type to run folder name.***')
				break

			for file in os.listdir(Path.cwd() / 'raw_data' / folder):
				if 'Data' in file and '.txt' in file and '.fail' not in file:
					file_path = rd_path / folder / file					
					if os.path.getsize(file_path) > 225000 or run_type == 'standard':	# Make sure .txt file is complete					
						file_n = int(file[5:10]) # get UID from file name
						samp_name = str(file[10:-4]) # get sample number from file name
						if file_n not in manual_rmv:
							lil_d, batch_data = b_s.read_Nu_data(file_path, file_n, samp_name, folder, run_type)						
							if lil_d != None:		
								d47_crunch_fmt.append(lil_d)
							if batch_data != None:
								batch_data_list.append(batch_data)

				fold_count += 1
		else: print('   Ignoring ', folder)

df_d47 = pd.DataFrame(d47_crunch_fmt, columns = ['UID', 'Session', 'Sample', 'd45', 'd46', 'd47', 'd48', 'd49'])

b_s.fix_names(df_d47)

print('Run type:', run_type)
raw_deltas_file = Path.cwd() / 'results' / f'raw_deltas_{proj}.csv'

df_sam, df_analy, rptability = b_s.run_D47crunch(run_type, raw_deltas_file)

if run_type == 'clumped':
	print('Adding sample metadata...')
	print(output_sep)
	b_s.add_metadata(results_path, rptability, batch_data_list, df_sam, df_analy)
	print(output_sep)
	print('Repeatability for all samples is ', round(rptability, 3)*1000, 'ppm' )
	print(output_sep)
	print('Data processing complete. Working on plots...')
	print(output_sep)

	df = pd.read_csv(Path.cwd().parents[0]/ 'results' / f'analyses_{proj}.csv')

	b_s.plot_ETH_D47(rptability, df)	
	b_s.cdv_plots(df)
	b_s.d47_D47_plot(df)
	b_s.interactive_plots(df)
	b_s.joy_plot()

elif run_type == 'standard':
	b_s.add_metadata_std()
#mk_pdf.run_mk_pdf()

print(output_sep)
print('SCRIPT COMPLETE.')
