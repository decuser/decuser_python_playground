#!/usr/bin/env python

# Changelog
#
# 20191216 0.5.1 added fast digest support, cleaned up a little
# 20191212 0.5.0 added recursion and hidden file support, changed version scheme
#                to support more minor update versions
# 20191210 0.4 refactored, added comments, added same name diff digest
# 20191210 0.3 Added argparse functionality and brief mode support
# 20191210 0.2 Added duplicate checking in src and dst individually
# 20191210 0.1 Initial working SW_VERSION

# Wishlist
# shallow digest ('random' 100 megs for large files)
# progress indication during sha1 calcs (simple version, dot every 1%, calc after file)
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

DEBUG = False
BLOCKSIZE = 65536
SW_VERSION = "0.5.0"

# declare some data structures
src_only = {}
dst_only = {}
match_name_digest = {}
src_digest_diff = {}
dst_digest_diff = {}
diff_name_match_digest = []
match_name_diff_digest = []
src_only_duplicates = {}
dst_only_duplicates = {}

# seed the random number generator
random.seed((10 * 1024 * 1024))

# a method to caculate a complete digest, slow, but accurate, this is the default
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
		
# a method to calculate a shallow digest (quick, dirty, and not terribly accurate)
# but it ought to be good enough for a fast comparison
# it is definitely not a tamper or bitrot detection algorithm, but it should detect normal
# filesystem changes like overwrites and chunked changes
# it only performs the shallow digest on files bigger than 100 megs
# the algorithm is only invoked with the -f --fast option 
def shallow_digest(file_to_digest):
    hasher = hashlib.sha1()
    
    size = getsize(file_to_digest)
    if DEBUG: print(f"size: {size}")
    # check if size <= 100 MB
    if size <= (100 * 1024 * 1024):
        if DEBUG: print("using regular digest")
        # return regular digest
        with open(file_to_digest, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        digest = hasher.hexdigest()
        afile.close()
    else:
        numiters = int(size / (10 * 1024 * 1024))
        if DEBUG: print(f"numiters: {numiters}")
        cutpoints = [(i * (10 * 1024 * 1024)) for i in range(0, numiters)]
        numcuts = len(cutpoints)     
        with open(file_to_digest, "rb") as afile:
            for i in range(0, numcuts):
                if i < numcuts - 1:
                    for x in random.sample(range(cutpoints[i], cutpoints[i + 1]), 256):
                        afile.seek(x)
                        buf = afile.read(1)
                        hasher.update(buf)
                else:
                    for x in random.sample(range(cutpoints[i], size - 1), 256):
                        afile.seek(x)
                        buf = afile.read(1)
                        hasher.update(buf)
        afile.close()
    digest = hasher.hexdigest()
    if DEBUG: print(digest)
    return digest

# display dictionary in value, key order
def display_dictionary(dict):
    for k, v in sorted(dict.items(), key=lambda x: (x[1], x[0])):
        print(f"{v} {k}")
    print()

# Class useful for calculating elapsed time
# provides rough calculations
# Create an instance anytime
# but call reset just before you want to
# calculate an elapsed time
# usage:
#	instantiate: timer = ElapsedTime()
#   reset timer: timer.reset()
#   get elapsed time: timer.elapsed()
class ElapsedTime:
	last_time = time.time()
	
	# method to show data
	def elapsed(self):
		elapsed = time.time() - ElapsedTime.last_time
		ElapsedTime.last_time = time.time()
		return elapsed
	
	def reset(self):
		last_time = time.time()

# Function to determine if we are running in a notebook or not
def isnotebook():
	try:
		shell = get_ipython().__class__.__name__
		if shell == 'ZMQInteractiveShell':
			return True	  # Jupyter notebook or qtconsole
		elif shell == 'TerminalInteractiveShell':
			return False  # Terminal running IPython
		else:
			return False  # Other type (?)
	except NameError:
		return False	  # Probably standard Python interpreter

# instantiate the ElapseTime utility class
timer = ElapsedTime()

# save the start time for calculating runtime
starttime = time.time()

# save the start date time for reporting
startdt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

# is this a notebook?
if(isnotebook()):
	homedir = str(Path.home())
	srcpath = homedir + "/src/"
	dstpath = homedir + "/dst/"
	brief = 'False'
# otherwise, assume it's a command line, get the arguments
else:
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
	srcpath = join(args['srcdir'], '')
	dstpath = join(args['dstdir'], '')
	brief = args['brief']
	all = args['all']
	recurse = args['recurse']
	fast = args['fast']

	# check if src and dst exist and ar directories
	if(not isdir(srcpath)):
		print(f"{srcpath} is not a directory")
		sys.exit()

	if(not isdir(dstpath)):
		print(f"{dstpath} is not a directory")
		sys.exit()

# print a welcome banner
print("\n+------------------------------------+")
print(f"|   Welcome to dircmp version {SW_VERSION}  |")
print("|  Created by Will Senn on 20191210  |")
print("|       Last updated 20191212        |")
print("+------------------------------------+")
if not brief: 
	print("Digest: sha1")
	print(f"Source (src): {srcpath}\nDestination (dst): {dstpath}")
	print(f"Show all files: {all}")
	print(f"Recurse subdirectories: {recurse}\n")
# reset the elapsed time and start the real work
timer.reset()

# method to walk a dir and create a list of dirs and files
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

# Read the source files into src_files list and count them
if not brief: print(f"Scanning src ...", end="")
src_files = recurse_subdir(srcpath, recurse, all)
num_src_files = len(src_files)
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f" {num_src_files} files found ({elapsedtime}s).")

# Calculate sha1 digests for the src_files and create src_files_dict
if not brief: print(f"Calculating sha1 digests in src ... ", end="")
src_files_dict={}
for f in src_files:
	if isfile(srcpath + f):
		if fast:
			src_files_dict[f] =shallow_digest(srcpath + f)
		else:
			src_files_dict[f] =full_digest(srcpath + f)
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).")

# Create revidx_src_files, a reverse index for searching src_files_dict by value
revidx_src_files = defaultdict(set)
for key, value in src_files_dict.items():
	revidx_src_files[value].add(key)

# Read the destination files into dst_files list and count them
if not brief: print(f"Scanning dst ...", end="")
dst_files = recurse_subdir(dstpath, recurse, all)
num_dst_files = len(dst_files)
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f" {num_dst_files} files found ({elapsedtime}s).")

# Calculate sha1 digests for the dst_files and create dst_files_dict
if not brief: print(f"Calculating sha1 digests in dst... ", end="")
dst_files_dict = {}
for f in dst_files:
	if isfile(dstpath + f):
		if fast:
			dst_files_dict[f] = shallow_digest(dstpath + f)
		else:
			dst_files_dict[f] = full_digest(dstpath + f)
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).")

# Create revidx_dst_files, a reverse index for searching dst_files_dict by value
revidx_dst_files = defaultdict(set)
for key, value in dst_files_dict.items():
	revidx_dst_files[value].add(key)

# Analyze src directory for files having duplicate contents
# add them to src_only_duplicates
if not brief: print(f"Analyzing src directory ...", end="")
# look for duplicate content in src
for key in src_files_dict.keys():
	srchash = src_files_dict[key]
	src_match_digest = revidx_src_files.get(srchash)
	if src_match_digest is not None:
		for fil in src_match_digest:
			if(key != fil):
				src_only_duplicates[key] = srchash
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).")

# Analyze dst directory for files having duplicate contents
# add them to dst_only_duplicates
if not brief: print(f"Analyzing dst directory ...", end="")
# look for duplicate content in src
for key in dst_files_dict.keys():
	dsthash = dst_files_dict[key]
	dst_match_digest = revidx_dst_files.get(dsthash)
	if dst_match_digest is not None:
		for fil in dst_match_digest:
			if(key != fil):
				dst_only_duplicates[key] = dsthash
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).")

# Compare the files in src to those in dst
if not brief: print(f"Comparing src to dst ...", end="")
# look for src files in dst
for key in src_files_dict.keys():
	srchash = src_files_dict[key]
	dst_match_digest = revidx_dst_files.get(srchash)
	if dst_match_digest is not None:
		for fil in dst_match_digest:
			if(key == fil):
				match_name_digest[key] = srchash
			else:
				if fil in src_files_dict.keys():
					if(srchash != src_files_dict[fil]):
						src_digest_diff[srchash] = key
				else:
					src_digest_diff[srchash] = key
	else:
		# check if filename is in dst (digest mismatch)
		skey = re.sub(r'^' + re.escape(srcpath), dstpath, key)
		if(skey in dst_files_dict.keys()):
			match_name_diff_digest.append([key, srchash, dst_files_dict[skey]])
		else:
			src_only[key] = srchash
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).")

# Compare the files in dst to those in src
if not brief: print(f"Comparing dst to src ...", end="")
# look for src files in dst
for key in dst_files_dict.keys():
	dsthash = dst_files_dict[key]
	src_match_digest = revidx_src_files.get(dsthash)
	if src_match_digest is not None:
		for fil in src_match_digest:
			if(key == fil):
				match_name_digest[key] = dsthash
			else:
				if fil in dst_files_dict.keys():
					if(dsthash != dst_files_dict[fil]):
						dst_digest_diff[dsthash] = key
				else:
					dst_digest_diff[dsthash] = key
	else:
		# check if filename is not in src (digest mismatches handled in src loop)
		if(key not in src_files_dict.keys()):
			dst_only[key] = dsthash
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).")

# Reconcile differences
if not brief: print(f"Reconciling differences ...", end="")
for k,v in src_digest_diff.items():
	 for j,u in dst_digest_diff.items():
		 if(k == j):
			 diff_name_match_digest.append([k, v, u])
elapsedtime = round(timer.elapsed(), 2)
if not brief: print(f"done ({elapsedtime}s).\n")

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
if not brief:
	print(f"Duplicates found in {srcpath}: {num_src_only_duplicates} files found.")
	for v in tvals:
		keys = revidx_src_only_duplicates.get(v)
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
if not brief:
	print(f"Duplicates found in {dstpath}: {num_dst_only_duplicates} files found.")
	for v in tvals:
		keys = revidx_dst_only_duplicates.get(v)
		if keys is not None:
			for f in keys:
				print(f"{v} {f}")
	print()

# Get counts of buckets	
num_src_only_files = len(src_only)
num_dst_only_files = len(dst_only)
num_match_name_digest = len(match_name_digest)
num_diff_name_match_digest = len(diff_name_match_digest) * 2
num_match_name_diff_digest = len(match_name_diff_digest) * 2

# Print buckets
if not brief: 
	print(f"Exact matches: {num_match_name_digest} files found.")
	display_dictionary(match_name_digest)

	print(f"Only in {srcpath}: {num_src_only_files} files found.")
	display_dictionary(src_only)

	print(f"Only in {dstpath}: {num_dst_only_files} files found.")
	display_dictionary(dst_only)

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
if not brief: print("Summary\n-------")

print(f"Started at {startdt}")
totalfiles = num_src_files + num_dst_files
print(f"{totalfiles} files analyzed.")
print(f"{num_src_files} files found in {srcpath}.")
print(f"{num_dst_files} files found in {dstpath}.")
print(f"{num_src_only_duplicates} duplicate files found in {srcpath}.")
print(f"{num_dst_only_duplicates} duplicate files found in {dstpath}.")
print(f"{num_match_name_digest} exact matches found.")
print(f"{num_src_only_files} files only exist in {srcpath}.")
print(f"{num_dst_only_files} files only exist in {dstpath}.")
print(f"{num_match_name_diff_digest} files have same names but different digests.")
print(f"{num_diff_name_match_digest} files have different names but same digest.")

final = time.time()

totaltime = round(final - starttime, 2)
print("Finished at ", end="")
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
if not brief: print()

if not brief: print(f"Total running time: {totaltime}s.")

