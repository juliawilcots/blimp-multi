# -- VERSION 0.1.0 updated 20211007 by NTA -- 


import os
import blimp_supp as b_s
import pandas as pd
from pathlib import Path
#import make_pdf as mk_pdf

output_sep = '--------------'

print(output_sep)

dir_path = Path.cwd().parents[0]
os.chdir(dir_path)

rd_path = Path.cwd() / 'raw_data'
results_path = Path.cwd() / ('results')
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

df_rmv = pd.read_excel('params.xlsx', 'Remove')
manual_rmv = list(df_rmv.UID)
run_type = 'clumped'

if os.path.isdir(rd_path): # If there is a raw data folder...
	print('Crunching folders: ')
	
	for folder in os.listdir(rd_path):
		if os.path.isdir(rd_path / folder): print(folder) # if the item you find is a directory, continue, else break the loop and go to the next. this helps with '.DS_store' and other random files
		else: break
	
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
					file_n = int(file[5:10])
					samp_name = str(file[10:-4])
					if file_n not in manual_rmv:
						lil_d, batch_data = b_s.read_Nu_data(file_path, file_n, samp_name, folder, run_type)						
						if lil_d != None:		
							d47_crunch_fmt.append(lil_d)
						if batch_data != None:
							batch_data_list.append(batch_data)

			fold_count += 1

df_d47 = pd.DataFrame(d47_crunch_fmt, columns = ['UID', 'Session', 'Sample', 'd45', 'd46', 'd47', 'd48', 'd49'])

b_s.fix_names(df_d47)

print('Run type:', run_type)
rptability = b_s.run_D47crunch(run_type)

if run_type == 'clumped':
	b_s.add_metadata(results_path, rptability, batch_data_list)
	print(output_sep)
	print('Repeatability for all samples is ', round(rptability, 3)*1000, 'ppm' )
	print(output_sep)

	b_s.plot_ETH_D47(rptability)
	b_s.joy_plot()
	b_s.cdv_plots()
	b_s.d47_D47_plot()
	# b_s.d47_D47_plot_bokeh()

elif run_type == 'standard':
	b_s.add_metadata_std()
#mk_pdf.run_mk_pdf()

print(output_sep)
print('SCRIPT COMPLETE.')
