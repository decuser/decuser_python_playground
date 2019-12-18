#!/usr/bin/env python

# Changelog
#
# 20191216 0.6.0 refactored
# 20191216 0.5.1 added fast digest support, cleaned up a little
# 20191212 0.5.0 added recursion and hidden file support, changed version scheme
#				 to support more minor update versions
# 20191210 0.4 refactored, added comments, added same name diff digest
# 20191210 0.3 Added argparse functionality and brief mode support
# 20191210 0.2 Added duplicate checking in src and dst individually
# 20191210 0.1 Initial working SW_VERSION

# Wishlist
# done 20191216 shallow digest ('random' 100 megs for large files)
# done 20191216 progress indication during sha1 calcs (simple version)
# done 20191212 wds recursion and hidden file support
# done 20191210 wds brief mode (suppress detailed lists)

# TODO - count dirs and files separately

import hashlib
import sys
import re
import time
import argparse
import random
from os import listdir, walk
from os.path import isfile, join, isdir, relpath, getsize
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Constants
DEBUG = False
BLOCKSIZE = 65536
SAMPLESIZE = (1 * 1024 * 1024)
BUFFERING = -1			# 0 for no bufferning, -1 for default
SEED = (10 * 1024 * 1024)
SW_VERSION = "0.6.0"
CREATED = "20191210"
UPDATED = "20191216"

# Data Structures
src_only = {}
dst_only = {}
exact_match = {}
src_digest_diff = {}
dst_digest_diff = {}
diff_name_match_digest = []
match_name_diff_digest = []
src_only_duplicates = {}
dst_only_duplicates = {}

# Methods

# Calculate sha1 digests for the src_files and create src_files_dict
# return a dictionary and reverse index
def calculate_sha1s(dir, display, files, args):
	if not args['brief']: print(f"Calculating sha1 digests in {display} ", end="")
	files_dict = {}
	current_progress = 0
	for f in files:
		if isfile(dir + f):
			if args['fast']:
				files_dict[f] = shallow_digest(dir + f)
			else:
				files_dict[f] = full_digest(dir + f)
			current_progress = current_progress + getsize(dir + f)
			display_progress(current_progress, src_files_bytes, 50)
	
	# Create revidx_src_files, a reverse index for searching src_files_dict by value
	revidx = defaultdict(set)
	for key, value in files_dict.items():
		revidx[value].add(key)
	
	return [files_dict, revidx]

# Compare the files in src to those in dst
# clunky, need to fix, too many arguments, too many 'globals', crying for class
def compare_directories(ldict, rrevidx, rdict, exmatch, mname_ddigest, srctxt, dsttxt, args):

	only = {}
	digest_diff = {}
	if not args['brief']: print(f"Comparing {srctxt} to {dsttxt} ...", end="")
	# look for src files in dst
	for key in ldict.keys():
		ahash = ldict[key]
		dst_match_digest = rrevidx.get(ahash)
		if dst_match_digest is not None:
			for fil in dst_match_digest:
				if(key == fil):
					exmatch[key] = ahash
				else:
					if fil in ldict.keys():
						if(ahash != ldict[fil]):
							digest_diff[ahash] = key
					else:
						digest_diff[ahash] = key
		else:
			# check if filename is in dst (digest mismatch)
			skey = re.sub(r'^' + re.escape(args['srcdir']), args['dstdir'], key)
			if(skey in rdict.keys()):
				mname_ddigest.append([key, ahash, rdict[skey]])
			else:
				only[key] = ahash
			
	return [only, digest_diff]

# Display a dictionary in specified order, default is key, value
def display_dictionary(dict, sortorder = "kv"):
    if sortorder == "kv":
            for k, v in sorted(dict.items(), key=lambda x: (x[0], x[1])):
                print(f"{k} {v}")
            print()
    elif sortorder == "vk":
            for k, v in sorted(dict.items(), key=lambda x: (x[1], x[0])):
                print(f"{v} {k}")
            print()

# Display dots when doing long running tasks (needs improvements)
def display_progress(curr, total, inc):
	if DEBUG:
		print(f"curr: {curr}")
		print(f"total: {total}")
		print(f"inc: {inc}")
	if total - curr > 0:
		per_progress = int((total / curr) * 100)
		if curr % (100 / inc):
			print(".", end="")
			sys.stdout.flush()

# Display welcome banner
def display_welcome(version, created, updated, args):
	print("\n+------------------------------------+")
	print(f"|  Welcome to dircmp version {SW_VERSION}   |")
	print(f"|  Created by Will Senn on {CREATED}  |")
	print(f"|       Last updated {UPDATED}        |")
	print("+------------------------------------+")
	if not args['brief']: 
		print("Digest: sha1")
		print(f"Source (src): {args['srcdir']}\nDestination (dst): {args['dstdir']}")
		print(f"Show all files: {args['all']}")
		print(f"Recurse subdirectories: {args['recurse']}")
		print(f"Calculate shallow digests: {args['fast']}\n")

# Caculate a sha1 digest from file entire contents of file
# this is the default method
# returns the calculated hex encoded digest
def full_digest(file_to_digest):
	hasher = hashlib.sha1()
	with open(file_to_digest, 'rb') as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
	digest = hasher.hexdigest()
	afile.close()
	return digest

# Get arguments from the command line
# returns arguments in a dictionary
def get_arguments():
	# positional arguments: 
	#  srcdir			a source directory
	#  dstdir			a destination directory
	#
	# regular arguments:
	#   -b, --brief		Brief mode - suppress file lists
	#   -a, --all		Include hidden files in comparisons
	#   -r, --recurse	Recurse subdirectories
	#   -f, --fast		Perform shallow digests (super fast, but less accurate)
	parser = argparse.ArgumentParser(
		description='Compare 2 directories using sha1 checksums.')
	parser.add_argument('srcdir', metavar='srcdir', type=str, 
		help='a source directory')
	parser.add_argument('dstdir', metavar='dstdir', type=str,
		help='a destination directory')
	parser.add_argument('-b', '--brief', action='store_true',
		help='Brief mode - suppress file lists')
	parser.add_argument('-a', '--all', action='store_true',
		help='Include hidden files in comparisons')
	parser.add_argument('-r', '--recurse', action='store_true',
		help='Recurse subdirectories')
	parser.add_argument('-f', '--fast', action='store_true',
		help='Perform shallow digests (super fast, but less accurate)')
	args = vars(parser.parse_args())
	args['srcdir'] = join(args['srcdir'], '')
	args['dstdir'] = join(args['dstdir'], '')

	# check if src and dst exist and are directories
	# bail otherwise
	if(not isdir(args['srcdir'])):
		print(f"{args['srcdir']} is not a directory")
		sys.exit()

	if(not isdir(args['dstdir'])):
		print(f"{args['dstdir']} is not a directory")
		sys.exit()
	return args

# Analyze src directory for files having duplicate contents
# return dictionary of duplicates
def get_duplicates(dict, revidx, display, args):
	if not args['brief']: print(f"Analyzing {display} directory ...", end="")
	
	duplicates = {}
	# look for duplicate content in src
	for key in dict.keys():
		ahash = dict[key]
		match_digest = revidx.get(ahash)
		if match_digest is not None:
			for fil in match_digest:
				if(key != fil):
					duplicates[key] = ahash
	return duplicates

# Read the source files into src_files list and count them
def get_files(dir, displayname, args):
	if not args['brief']: print(f"Scanning {displayname} ...", end="")
	files = recurse_subdir(dir, args['recurse'], args['all'])
	files_bytes = total_files(dir, files)
	num_files = len(files)
	return [files, files_bytes, num_files]

# Create a list of dirs and files from a root
def recurse_subdir(dir, recurse, all):
	tfiles = []
	rfiles = []
	if not recurse:
		tfiles = listdir(dir)
	else:
		for root, dirs, files in walk(dir):
			tfiles.append(root)
			for file in files:
				tfiles.append(join(root, file))
		tfiles[:] = [relpath(path, dir) for path in tfiles]
		if(tfiles[0] == "."):
			tfiles.pop(0)
	if not all:
		for f in tfiles:
			if f.startswith('.'):
				pass
			else:
				rfiles.append(f)
	else:
		rfiles = tfiles
	return rfiles

# Calculate a sha1 digest from the encoded filesize in bytes,
# plus the first and last SAMPLESIZE bytes of file
# this is the -f --fast method
# returns the calculated hex encoded digest
def shallow_digest(file_to_digest):
	# seed the random number generator
	random.seed(SEED)
	hasher = hashlib.sha1()
	size = getsize(file_to_digest)
	
	if DEBUG: print(f"size: {size}")
	# check if size <= 10 MB
	if size <= (10 * 1024 * 1024):
		if DEBUG: print("using regular digest")
		# return regular digest
		with open(file_to_digest, 'rb', BUFFERING) as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		digest = hasher.hexdigest()
		afile.close()
	else:
		with open(file_to_digest, "rb", BUFFERING) as afile:
			hasher.update(str.encode(str(size)))
			buf = afile.read(SAMPLESIZE)
			hasher.update(buf)
			afile.seek(size - SAMPLESIZE)
			buf = afile.read(SAMPLESIZE)
			hasher.update(buf)			
		afile.close()
	digest = hasher.hexdigest()
	if DEBUG: print(digest)
	return digest

# Calulate a total size from a list of files
def total_files(path, files):
	total = 0
	for f in files:
		total = total + getsize(path + f)
	return total

# Classes

# Utility class for calculating elapsed time between events
# Typical usage is to instantiate, reset, and get elapsed time.
#
# To instantiate prior to use:
#	timer = ElapsedTime()
# To reset and establish a reference time:
#	timer.reset()
# To get the elapsed time since the reference:
#	timer.elapsed()
#
class ElapsedTime:
	last_time = time.time()
	
	# class method to show elapsed time
	def elapsed(self):
		elapsed = time.time() - ElapsedTime.last_time
		ElapsedTime.last_time = time.time()
		return elapsed

	# class method to print elapsed time in (XXs) form
	def display(self, prefix, suffix, args):
		if not args['brief']:
			e = round(self.elapsed(), 2)
			print(f"{prefix}({e}s){suffix}", end="")

	# class method to reset time
	def reset(self):
		last_time = time.time()
	

# Main program

# save the start date time for reporting
# save the start time for calculating runtime
# instantiate the ElapseTime utility class
start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
start_time = time.time()
timer = ElapsedTime()

# grab the arguments, validate them, and store them in args dictionary
args = get_arguments()

# display the welcome banner
display_welcome(SW_VERSION, CREATED, UPDATED, args)

# reset the timer
timer.reset()

# get the source files
[src_files, src_files_bytes, num_src_files] = get_files(args['srcdir'], "src", args)
timer.display(f" {num_src_files} files found ", ".\n", args)

# calculate src sha1s
[src_files_dict, revidx_src_files] = calculate_sha1s(args['srcdir'], "src", src_files, args)
timer.display(f" done ", ".\n", args)

# get the destination files
[dst_files, dst_files_bytes, num_dst_files] = get_files(args['dstdir'], "dst", args)
timer.display(f" {num_dst_files} files found ", ".\n", args)

# calculate dst sha1s
[dst_files_dict, revidx_dst_files] = calculate_sha1s(args['dstdir'], "dst", dst_files, args)
timer.display(f" done ", ".\n", args)

# get all duplicates in src
src_only_duplicates = get_duplicates(src_files_dict, revidx_src_files, "src", args)
timer.display(f"done ", ".\n", args)

# get all duplicates in dst
dst_only_duplicates = get_duplicates(dst_files_dict, revidx_dst_files, "dst", args)
timer.display(f"done ", ".\n", args)

# Compare the files in src to those in dst
[src_only, src_digest_diff] = compare_directories(src_files_dict, revidx_dst_files, dst_files_dict, exact_match, match_name_diff_digest, "src", "dst", args)
timer.display(f"done ", ".\n", args)

# Compare the files in dst to those in src
[dst_only, dst_digest_diff] = 	compare_directories(dst_files_dict, revidx_src_files, src_files_dict, exact_match, match_name_diff_digest, "dst", "src", args)
timer.display(f"done ", ".\n", args)

# Reconcile differences
if not args['brief']: print(f"Reconciling differences ...", end="")
for k,v in src_digest_diff.items():
	 for j,u in dst_digest_diff.items():
		 if(k == j):
			 diff_name_match_digest.append([k, v, u])
elapsedtime = round(timer.elapsed(), 2)
if not args['brief']: print(f"done ({elapsedtime}s).\n")

# Count the src only duplicates found
# Create revidx_src_only_duplicates, a reverse index for searching src_only_duplicates by value
revidx_src_only_duplicates = defaultdict(set)
for key, value in src_only_duplicates.items():
	revidx_src_only_duplicates[value].add(key)

# create a sorted list of unique src only duplicate digests
tvals = []
for i in src_only_duplicates.values():
	if i not in tvals:
		tvals.append(i)
tvals.sort()
num_src_only_duplicates = len(src_only_duplicates)

# Display the list of src only duplicates
if not args['brief']:
	print(f"Duplicates found in {args['srcdir']}: {num_src_only_duplicates} files found.")
	for v in tvals:
		keys = sorted(revidx_src_only_duplicates.get(v))
		if keys is not None:
			for f in keys:
				print(f"{v} {f}")
	print()


# Count the dst only duplicates found
# Create revidx_dst_only_duplicates, a reverse index for searching dst_only_duplicates by value
revidx_dst_only_duplicates = defaultdict(set)
for key, value in dst_only_duplicates.items():
	revidx_dst_only_duplicates[value].add(key)

# create a sorted list of unique dst only duplicate digests
tvals = []
for i in dst_only_duplicates.values():
	if i not in tvals:
		tvals.append(i)
tvals.sort()
num_dst_only_duplicates = len(dst_only_duplicates)

# Display the list of dst only duplicates
if not args['brief']:
	print(f"Duplicates found in {args['dstdir']}: {num_dst_only_duplicates} files found.")
	for v in tvals:
		keys = sorted(revidx_dst_only_duplicates.get(v))
		if keys is not None:
			for f in keys:
				print(f"{v} {f}")
	print()

# Get counts of buckets 
num_src_only_files = len(src_only)
num_dst_only_files = len(dst_only)
num_exact_match = len(exact_match)
num_diff_name_match_digest = len(diff_name_match_digest) * 2
num_match_name_diff_digest = len(match_name_diff_digest) * 2

# Print buckets
if not args['brief']: 
	print(f"Exact matches: {num_exact_match} files found.")
	display_dictionary(exact_match, "kv")

	print(f"Only in {args['srcdir']}: {num_src_only_files} files found.")
	display_dictionary(src_only, "kv")

	print(f"Only in {args['dstdir']}: {num_dst_only_files} files found.")
	display_dictionary(dst_only, "kv")

	print(f"Same names but different digests: {num_match_name_diff_digest} files found.")
	for f in sorted(match_name_diff_digest):
		print(f"{f[0]} src:{f[1]}")
		print(f"{f[0]} dst:{f[2]}")
	print()

	print(f"Different names but same digests: {num_diff_name_match_digest} files found.")
	for f in sorted(diff_name_match_digest):
		print(f"{f[0]} {f[1]}")
		print(f"{f[0]} {f[2]}")
	print()

# Display Summary
if not args['brief']: print("Summary\n-------")

print(f"Started at {start_date}")
totalfiles = num_src_files + num_dst_files
print(f"{totalfiles} files analyzed.")
print(f"{num_src_files} files found in {args['srcdir']}.")
print(f"{num_dst_files} files found in {args['dstdir']}.")
print(f"{num_src_only_duplicates} duplicate files found in {args['srcdir']}.")
print(f"{num_dst_only_duplicates} duplicate files found in {args['dstdir']}.")
print(f"{num_exact_match} exact matches found.")
print(f"{num_src_only_files} files only exist in {args['srcdir']}.")
print(f"{num_dst_only_files} files only exist in {args['dstdir']}.")
print(f"{num_match_name_diff_digest} files have same names but different digests.")
print(f"{num_diff_name_match_digest} files have different names but same digest.")

final = time.time()

totaltime = round(final - start_time, 2)
print("Finished at ", end="")
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
if not args['brief']: print()

if not args['brief']: print(f"Total running time: {totaltime}s.")

