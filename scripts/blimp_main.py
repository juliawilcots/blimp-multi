# --- VERSION 0.2.0 updated 20231026 by JKW ---

import os
import pandas as pd
import json ## add to environment yaml!!!

#import make_pdf as mk_pdf

output_sep = '------------------------'

print(output_sep)

# Read information from json file
json_file = input("Drag your .json file here, then press enter:\n")

# json file should have fields: "blimp_run_name", "sessions", "params"
with open(json_file.strip(' ')) as f:
    blimp_data = json.load(f)
    # f.close()

# Skip params here. Do that in blimp_supp
output_name = blimp_data["blimp_run_name"]
datasets = blimp_data["sessions"] # a dictionary of collections of runs you want to process separately
output_path = blimp_data["output_path"]
params = blimp_data["params"] # will be the path to a params.xlsx file

output_folder = output_path + '/' + output_name

# Create folders for each dataset
if os.path.isdir(output_folder): # first, make a directory named '[output_name]'
	pass 
else:
	os.mkdir(output_folder)
# In for loop below, make/check for folders for each dataset in datasets

####### Julia: time to get rid of 'proj'


# COMMENTED OUT FOR NOW FOR DEBUGGING PURPOSES
import blimp_supp as b_s

######### Manual input option ########
# Manual input option:
# output_name = input("Enter a name for this blimp run: ") # e.g., the date, '2018_runs', etc.
# multi_session = input("How many separate analyses would you like to run? (integer number)\n")
# n_sessions = int(multi_session)
# datasets = {}
# i = 0 # at least one session
# while i < n_sessions:
# 	session_name = input("Enter a name for session/analysis %i: " %i)
# 	session_dir = input("Drag directory containing raw_data folder for analysis %i into terminal.\n" %i)
# 	datasets[session_name] = session_dir.strip(' ') #sometimes an extra space at the end of the filepath
# 	i+=1
# 
# User drags params file into terminal to load it. MANUAL MODE ONLY
# def define_params_location():
# 	'''
# 	user defines where params file is located
# 	'''
# 	params_dir = input("Drag params.xlsx file into terminal, then press enter.\n")
# 	return params_dir.strip(' ') # there is sometimes an extra space at the end of the filepath
# 
# params = define_params_location()

####### IF NOT RUNNING blimp_supp.py, UNCOMMENT THIS CODE AND IMPORT PARAMS HERE (for testing) ########
def import_params():
	'''
	Get data from each sheet of the params excel file
	'''
	df_rmv = pd.read_excel(params, 'Remove')
	df_anc = pd.read_excel(params, 'Anchors', index_col = 'Anchor')
	df_const = pd.read_excel(params, 'Constants', index_col = 'Name')
	df_threshold = pd.read_excel(params, 'Thresholds', index_col = 'Type')
	df_rnm = pd.read_excel(params, 'Rename_by_UID')
	df_meta = pd.read_excel(params, 'Metadata')
	df_names = pd.read_excel(params, 'Names_to_change')

	return df_rmv, df_anc, df_const, df_threshold, df_rnm, df_meta, df_names

df_rmv, df_anc, df_const, df_threshold, df_rnm, df_meta, df_names = import_params()

manual_rmv = list(df_rmv.UID)

run_type = 'clumped'
print(output_sep) #------------------------#

# Create results and plot directories if they do not already exist
######## TO DO: create different folders for each session/analysis
# should be something like:
# for set in datasets:
# 	-> create folders

########## Everything below here happens separately for each set of analyses
for set_name,data_path in datasets.items():

	rd_path = data_path + '/raw_data' # path to raw data

	# check for/create folder for this dataset
	dataset_path = output_folder + '/' + set_name
	if os.path.isdir(dataset_path):
		pass 
	else:
		os.mkdir(dataset_path)	

	# Check for / create results and plots folders:
	results_path = output_path + '/%s/%s/results' %(output_name,set_name)
	plot_path = output_path + '/%s/%s/plots' %(output_name,set_name)

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


	if os.path.isdir(rd_path): # If there is a raw data folder...
		print('Crunching folders: ')
		
		for folder in os.listdir(rd_path):
			folder_path = rd_path + '/%s' %folder
			# print('folder_path: ',folder_path)
			if os.path.isdir(folder_path):
				# print('folder: ',folder) # if the item you find is a directory, continue, else break the loop and go to the next. This helps with '.DS_store' and other random files		
				if 'clumped' in folder or 'Clumped' in folder:
					run_type = 'clumped'
				elif 'standard' or 'Standard' in folder:
					run_type = 'standard'
				else:
					print('***Run type (standard or clumped) not defined. Add run type to run folder name.***')
					break

				for file in os.listdir(folder_path):
					if 'Data' in file and '.txt' in file and '.fail' not in file:
						file_path = folder_path + '/' + file
						# print('file_path: ', file_path)					
						if os.path.getsize(file_path) > 225000 or run_type == 'standard':	# Make sure .txt file is complete					
							file_n = int(file[5:10]) # get UID from file name
							samp_name = str(file[10:-4]) # get sample number from file name
							# GOT HERE!!
							if file_n not in manual_rmv:
								lil_d, batch_data = b_s.read_Nu_data(folder_path, file_path, file_n, samp_name, folder, run_type)						
								if lil_d != None:		
									d47_crunch_fmt.append(lil_d)
								if batch_data != None:
									batch_data_list.append(batch_data)

					fold_count += 1
			else: print('   Ignoring ', folder)

	df_d47 = pd.DataFrame(d47_crunch_fmt, columns = ['UID', 'Session', 'Sample', 'd45', 'd46', 'd47', 'd48', 'd49'])

	b_s.fix_names(df_d47, results_path)

	print('Run type:', run_type)
	##### FIX THIS NEXT #####
	# raw_deltas_file = Path.cwd() / 'results' / f'raw_deltas_{proj}.csv' # just have fix_names return the raw deltas file (actually probably some D47Crunch reason why this isn't happening)
	# df_sam, df_analy, rptability = b_s.run_D47crunch(run_type, raw_deltas_file)
	raw_deltas_file = results_path + '/raw_deltas.csv'
	df_sam, df_analy, rptability = b_s.run_D47crunch(run_type, raw_deltas_file, results_path)


	if run_type == 'clumped':
		print('Adding sample metadata...')
		print(output_sep)
		b_s.add_metadata(results_path, rptability, batch_data_list, df_sam, df_analy)
		print(output_sep)
		print('Repeatability for all samples is ', round(rptability, 3)*1000, 'ppm' )
		print(output_sep)
		print('Data processing complete. Working on plots...')
		print(output_sep)

		# df = pd.read_csv(Path.cwd().parents[0]/ 'results' / f'analyses_{proj}.csv')
		df = pd.read_csv(results_path + '/analyses.csv')

		b_s.plot_ETH_D47(rptability, df, plot_path)	
		b_s.cdv_plots(df, results_path, plot_path)
		b_s.d47_D47_plot(df, plot_path)
		b_s.interactive_plots(df, plot_path)
		b_s.joy_plot(plot_path)

	elif run_type == 'standard':
		b_s.add_metadata_std()
	#mk_pdf.run_mk_pdf()

	print(output_sep)
	print('SCRIPT COMPLETE.')
