import os
from pathlib import Path

def define_params_location():
	'''
	user defines where params file is located
	'''
	params_loc = input("Enter path to params file from %s (omit first /):\n" %Path.cwd())
	params_dir = Path.cwd() / params_loc
	params_dir = params_loc
	print(params_dir)
	return params_dir

def check_params_location():
	'''
	check that params file exists
	'''
	params_dir = define_params_location() # user inputs directory containing params file
	params_yn = input('Is the params file in %s? (Y/N):\n' %params_dir)
	return params_yn, params_dir

params_yn = 'N'

# Keep trying (failsafe if you type your directory wrong)
while params_yn == 'N':
	params_yn, params_dir = check_params_location()

if Path.is_file(params_dir / 'params.xlsx'):
	params = params_dir / 'params.xlsx'
else:
	print('params.xlsx not found in %s' %params_dir)
	print('add your params file and try again. goodbye for now.')
	exit()

# Only get here if we have found a params file. Otherwise the program will exit.

