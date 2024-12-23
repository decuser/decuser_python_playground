#!/usr/bin/env python
# canonical source located at https://github.com/decuser/decuser_python_playground.git

# quirks
# 20210803 "Only in" refers to file content, not filename, so a filename
# might exist in only one of the trees being compared, but if its contents match a
# file in the other tree, it will not be listed in "Only in". It will be noted in
# "Different names but same digests"
# For example:
# in src, there's a file named only_in_src that contains the letter 'a'
# in dst, there's a file named only_in_dst that contains the letter 'a'
# The comparison would show 0 files Only in src, 0 files Only in dst and
# 2 files Different names but same digests. To be clear, the program
# privileges content over names. An enhancement would be to support
# Names only in and Content only in...

# Changelog
#
# 20210804 0.7.3 added compact output - good for testing and looks good, too :)
# 20210804 0.7.2 bugfix unlisted - issue with directories added to filelist
# 20210804 0.7.1 bugfix 14 -b -s not working
# 20210802 0.7.0 added support for single directory and fixed counting
# 20200620 0.6.2 added version argument
# 20191218 0.6.1 bugfixes 7 empty source dir div/zero, 8 hidden files included erroneously
# 20191218 0.6.0 refactored, embraced global data structures after back and forth
# 20191216 0.5.1 added fast digest support, cleaned up a little
# 20191212 0.5.0 added recursion and hidden file support, changed version scheme
# 	to support more minor update versions
# 20191210 0.4 refactored, added comments, added same name diff digest
# 20191210 0.3 Added argparse functionality and brief mode support
# 20191210 0.2 Added duplicate checking in src and dst individually
# 20191210 0.1 Initial working SW_VERSION

# Wishlist
# 20210803 support names only in
# done 20210802 fixed counting
# done 20210730 added single directory analysis support
# done 20191216 shallow digest (fast version)
# done 20191216 progress indication during sha1 calc (simple version)
# done 20191212 wds recursion and hidden file support
# done 20191210 wds brief mode (suppress detailed lists)

import argparse
import hashlib
import random
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from os import listdir, walk
from os.path import isfile, join, isdir, relpath, getsize, split
from functools import cmp_to_key

# Constants
BLOCKSIZE = 65536
SAMPLESIZE = (1 * 1024 * 1024)
BUFFERING = -1  # 0 for no bufferning, -1 for default
SEED = (10 * 1024 * 1024)
SW_VERSION = "0.7.3"
__version__ = SW_VERSION
CREATED = "20191210"
UPDATED = "20210805"

# Global Data Structures
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

# Calculate sha1 digests
# return a dictionary of files and digests and a reverse index of the dictionary
def calculate_sha1s(dir_to_parse, display, files):
	if not (args['brief'] or args['compact']):
		print(f"Calculating sha1 digests in {display} ", end="")
	files_dict = {}
	current_progress = 0
	for f in files:
		if isfile(dir_to_parse + f):
			if args['fast']:
				files_dict[f] = shallow_digest(dir_to_parse + f)
			else:
				files_dict[f] = full_digest(dir_to_parse + f)
			current_progress = current_progress + getsize(dir_to_parse + f)
			display_progress(current_progress, src_files_bytes, 50)

	# Create revidx_src_files, a reverse index for searching src_files_dict by value
	revidx = defaultdict(set)
	for key, value in files_dict.items():
		revidx[value].add(key)

	return [files_dict, revidx]

# Compare the files in two dictionaries
def compare_directories(ldict, rrevidx, rdict, srctxt, dsttxt):
	only = {}
	digest_diff = {}
	if not (args['brief'] or args['compact']):
		print(f"Comparing {srctxt} to {dsttxt} ...", end="")
	# look for src files in dst
	for key in ldict.keys():
		ahash = ldict[key]
		dst_match_digest = rrevidx.get(ahash)
		if dst_match_digest is not None:
			for fil in dst_match_digest:
				if key == fil:
					exact_match[key] = ahash
				else:
					if ahash not in digest_diff:
						digest_diff[ahash] = []
					if f"{srctxt}:{key}" not in digest_diff[ahash]:
						digest_diff[ahash].append(f"{srctxt}:{key}")
					if f"{dsttxt}:{fil}" not in digest_diff[ahash]:
						digest_diff[ahash].append(f"{dsttxt}:{fil}")
		else:
			# check if filename is in dst (digest mismatch)
			skey = re.sub(r'^' + re.escape(args['srcdir']), args['dstdir'], key)
			if skey in rdict.keys():
				# a hack to prevent displaying the same record twice
				found = False
				for k, lv, rv in match_name_diff_digest:
					if skey == k:
						found = True
						break
					else:
						pass
				if not found:
					match_name_diff_digest.append([key, ahash, rdict[skey]])
			else:
				only[key] = ahash

	return [only, digest_diff]

# Display a dictionary in specified order, default is key, value
def display_dictionary(dict_to_display, display, num, sortorder="kv", displayorder="kv"):
	if not args['brief']:
		print(f"{display}: {num} files found.")
	if sortorder == "kv":
		for k, v in sorted(dict_to_display.items(), key=lambda x: (x[0], x[1])):
			if displayorder == "kv":
				print(f"{k} {v}")
			else:
				print(f"{v} {k}")
		print()
	elif sortorder == "vk":
		for k, v in sorted(dict_to_display.items(), key=lambda x: (x[1], x[0])):
			if displayorder == "kv":
				print(f"{k} {v}")
			else:
				print(f"{v} {k}")
		if not (args['brief'] or args['compact']):
			print()

# Display duplicates in a directory, given a dictionary of duplicates
def display_duplicates(duplicates, dir_to_display):
	revidx_duplicates = defaultdict(set)
	for key, value in duplicates.items():
		revidx_duplicates[value].add(key)

	# create a sorted list of unique src only duplicate digests
	tvals = []
	for i in duplicates.values():
		if i not in tvals:
			tvals.append(i)
	tvals.sort()
	num_duplicates = len(duplicates)

	# Display the list of src only duplicates
	if not args['brief']:
		print(f"Duplicates found in {dir_to_display}: {num_duplicates} files found.")
		for v in tvals:
			keys = sorted(revidx_duplicates.get(v))
			if keys is not None:
				for f in keys:
					print(f"{v} {f}")
		print()

# Display dots when doing long running tasks (needs improvements)
def display_progress(curr, total, inc):
	if (args['brief'] or args['compact']):
		return
	if args['debug']:
		print(f"curr: {curr}")
		print(f"total: {total}")
		print(f"inc: {inc}")
	if total - curr > 0:
		# fudge curr as simple fix for div by zero
		# per_progress = int((total / (curr + .00001)) * 100)
		if curr % (100 / inc):
			print(".", end="")
			sys.stdout.flush()

# Display welcome banner
def display_welcome():
	print("\n+----------------------------------+")
	print(f"| Welcome to dircmp version {SW_VERSION}  |")
	print(f"| Created by Will Senn on {CREATED} |")
	print(f"| Last updated {UPDATED}            |")
	print("+----------------------------------+")
	display_command_line()
	if not args['brief']:
		if args['debug']:
			print(f"** Debug: True **")
		print("Digest: sha1")
		print(f"Source (src): {args['srcdir']}")
		if not args['single']:
			print(f"Destination (dst): {args['dstdir']}")
		print(f"Compact mode: {args['compact']}")
		print(f"Single directory mode: {args['single']}")
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
	#	-b, --brief		Brief mode - suppress file lists
	#	-a, --all		Include hidden files in comparisons
	#	-r, --recurse	Recurse subdirectories
	#	-f, --fast		Perform shallow digests (super fast, but less accurate)
	#	-d, --debug		Debug mode
	#   -c, --compact   Compact mode
	#   -s, --single	Analyze single directory
	#	-v, --Version	Show the program version number
	parser = argparse.ArgumentParser(
		description='Compare 2 directories using sha1 checksums.')
	parser.add_argument('srcdir', metavar='srcdir', type=str,
						help='a source directory')
	parser.add_argument('dstdir', nargs="?", metavar='dstdir', type=str,
						help='a destination directory')
	parser.add_argument('-b', '--brief', action='store_true',
						help='Brief mode - suppress file lists')
	parser.add_argument('-a', '--all', action='store_true',
						help='Include hidden files in comparisons')
	parser.add_argument('-r', '--recurse', action='store_true',
						help='Recurse subdirectories')
	parser.add_argument('-f', '--fast', action='store_true',
						help='Perform shallow digests (super fast, but less accurate)')
	parser.add_argument('-d', '--debug', action='store_true',
						help='Debug mode')
	parser.add_argument('-c', '--compact', action='store_true',
						help='Compact mode')
	parser.add_argument('-s', '--single', action='store_true',
						help='Single directory mode')
	parser.add_argument('-v', '--version', action='version',
						version='%(prog)s {version}'.format(version=__version__))
	args = vars(parser.parse_args())
	args['srcdir'] = join(args['srcdir'], '')
	if not args['single']:
		if not args['dstdir']:
			print(f"Destination missing")
			sys.exit()
		args['dstdir'] = join(args['dstdir'], '')

	# check if src and dst exist and are directories
	# bail otherwise
	if not isdir(args['srcdir']):
		print(f"{args['srcdir']} is not a directory")
		sys.exit()

	if not args['single'] and not isdir(args['dstdir']):
		print(f"{args['dstdir']} is not a directory")
		sys.exit()

	return args

def display_command_line():
	print("Arguments:", end=" ")
	for i in range(1, len(sys.argv)):
		print(sys.argv[i], end="")
		if i < len(sys.argv):
			print(" ", end="")
	print()

# Reconcile differences
def get_diff_names_same_digests(ldigests, rdigests):
	if not (args['brief'] or args['compact']):
		print(f"Checking for different names, same digest ...", end="")
	digest = []
	for k, v in ldigests.items():
		for j, u in rdigests.items():
			if k == j:
				nlist = unique(v + u)
				nlist.sort(reverse=True, key=lambda name: (name[0:3]))
				nlist.sort(key=lambda e: e.split(':')[-1])
				nlist.sort(reverse=True, key=lambda e: e.split(':')[0])
				digest.append([k, nlist])
	return digest

# function to get unique values from a list
def unique(list1):
	# insert the list to the set
	list_set = set(list1)
	# convert the set to the list
	unique_list = (list(list_set))
	return unique_list

# Analyze src directory for files having duplicate contents
# return dictionary of duplicates
def get_duplicates(dict_to_analyze, revidx, display):
	if not (args['brief'] or args['compact']):
		print(f"Analyzing {display} directory ...", end="")

	duplicates = {}
	# look for duplicate content in src
	for key in dict_to_analyze.keys():
		ahash = dict_to_analyze[key]
		match_digest = revidx.get(ahash)
		if match_digest is not None:
			for fil in match_digest:
				if key != fil:
					duplicates[key] = ahash
	return duplicates

# Read the source files into src_files list and count them
def get_files(dir_to_analyze, displayname):
	if not (args['brief'] or args['compact']):
		print(f"Scanning {displayname} ...", end="")
	[num_dirs, num_files, files] = recurse_subdir(dir_to_analyze, args['recurse'], args['all'])
	files_bytes = total_files(dir_to_analyze, files)
	return [files, files_bytes, num_dirs, num_files]

# Create a list of dirs and files from a root
def recurse_subdir(dir_to_analyze, recurse, all_flag):
	dir_count = 0
	file_count = 0
	tfiles = []
	rfiles = []
	if not recurse:
		tfiles = listdir(dir_to_analyze)
		for file in tfiles:
			if isdir(join(dir_to_analyze, file)):
				if all_flag or not file.startswith('.'):
					dir_count += 1
			if isfile(join(dir_to_analyze, file)):
				if all_flag or not file.startswith('.'):
					file_count += 1
					rfiles.append(file)
	else:
		for root, dirs, files in walk(dir_to_analyze):
			[head, tail] = split(root)
			if all_flag or not (root.startswith('.') or tail.startswith('.')):
				tfiles.append(root)
				for file in files:
					if all_flag or not file.startswith('.'):
						file_count += 1
						tfiles.append(join(root, file))
				for dir in dirs:
					if all_flag or not dir.startswith('.'):
						dir_count += 1
		for idx in range(0, len(tfiles)):
			tfiles[idx] = relpath(tfiles[idx], dir_to_analyze)
		if tfiles[0] == ".":
			tfiles.pop(0)
		rfiles = tfiles
	return [dir_count, file_count, rfiles]

# Calculate a sha1 digest from the encoded filesize in bytes,
# plus the first and last SAMPLESIZE bytes of file
# this is the -f --fast method
# returns the calculated hex encoded digest
def shallow_digest(file_to_digest):
	# seed the random number generator
	random.seed(SEED)
	hasher = hashlib.sha1()
	size = getsize(file_to_digest)

	if args['debug']:
		print(f"size: {size}")
	# check if size <= 10 MB
	if size <= (10 * 1024 * 1024):
		if args['debug']:
			print("using regular digest")
		# return regular digest
		with open(file_to_digest, 'rb', BUFFERING) as afile:
			buf = afile.read(BLOCKSIZE)
			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(BLOCKSIZE)
		hasher.hexdigest()
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
	if args['debug']:
		print(digest)
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
	@property
	def elapsed(self):
		elapsed = time.time() - ElapsedTime.last_time
		ElapsedTime.last_time = time.time()
		return elapsed

	# class method to print elapsed time in (XXs) form
	def display(self, prefix, suffix):
		if not (args['brief'] or args['compact']):
			e = round(self.elapsed, 2)
			print(f"{prefix}({e}s){suffix}", end="")

	# class method to reset time
	def reset(self):
		self.last_time = time.time()

# Main program

num_dst_files = 0
num_dst_dirs = 0

# save the start date time for reporting
# save the start time for calculating runtime
# instantiate the ElapseTime utility class
start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
start_time = time.time()
timer = ElapsedTime()

# grab the arguments, validate them, and store them in args dictionary
args = get_arguments()

# display the welcome banner
display_welcome()

# reset the timer
timer.reset()

# get the source files
[src_files, src_files_bytes, num_src_dirs, num_src_files] = get_files(args['srcdir'], "src")
timer.display(f" {num_src_files} files found ", ".\n")

# calculate src sha1s
[src_files_dict, revidx_src_files] = calculate_sha1s(args['srcdir'], "src", src_files)
timer.display(f" done ", ".\n")

if not args['single']:
	# get the destination files
	[dst_files, dst_files_bytes, num_dst_dirs, num_dst_files] = get_files(args['dstdir'], "dst")
	timer.display(f" {num_dst_files} files found ", ".\n")

	# calculate dst sha1s
	[dst_files_dict, revidx_dst_files] = calculate_sha1s(args['dstdir'], "dst", dst_files)
	timer.display(f" done ", ".\n")

	# get all duplicates in src
	src_only_duplicates = get_duplicates(src_files_dict, revidx_src_files, "src")
	timer.display(f"done ", ".\n")

	# get all duplicates in dst
	dst_only_duplicates = get_duplicates(dst_files_dict, revidx_dst_files, "dst")
	timer.display(f"done ", ".\n")

	# Compare the files in src to those in dst
	[src_only, src_digest_diff] = compare_directories(src_files_dict, revidx_dst_files, dst_files_dict, "src", "dst")
	timer.display(f"done ", ".\n")

	# Compare the files in dst to those in src
	[dst_only, dst_digest_diff] = compare_directories(dst_files_dict, revidx_src_files, src_files_dict, "dst", "src")
	timer.display(f"done ", ".\n")

	# Get list of files with different names but same digest
	diff_name_match_digest = get_diff_names_same_digests(src_digest_diff, dst_digest_diff)
	timer.display(f"done ", ".\n\n")
else:
	# just get duplicates in src
	src_only_duplicates = get_duplicates(src_files_dict, revidx_src_files, "src")
	timer.display(f"done ", ".\n\n")

# Get counts of buckets 
num_src_only_files = len(src_only)
num_dst_only_files = len(dst_only)
num_exact_match = len(exact_match)
num_src_only_duplicates = len(src_only_duplicates)
num_dst_only_duplicates = len(dst_only_duplicates)

num_diff_name_match_digest = 0
for k, v in diff_name_match_digest:
	for f in v:
		num_diff_name_match_digest += 1

num_match_name_diff_digest = len(match_name_diff_digest) * 2

# Print buckets
if not args['brief']:
	display_duplicates(src_only_duplicates, args['srcdir'])
	if not args['single']:
		display_duplicates(dst_only_duplicates, args['dstdir'])
		display_dictionary(exact_match, "Exact matches", num_exact_match, "kv", "vk")
		display_dictionary(src_only, f"Only in {args['srcdir']}", num_src_only_files, "kv", "vk")
		display_dictionary(dst_only, f"Only in {args['dstdir']}", num_dst_only_files, "kv", "vk")

		print(f"Same names but different digests: {num_match_name_diff_digest} files found.")
		for f in sorted(match_name_diff_digest):
			print(f"{f[0]} src:{f[1]}")
			print(f"{f[0]} dst:{f[2]}")
		print()

		print(f"Different names but same digests: {num_diff_name_match_digest} files found.")
		for e in sorted(diff_name_match_digest):
			#print(f"{f[0]} {f[1]}")
			#print(f"{f[0]} {f[2]}")
			for f in e[1]:
				print(f"{e[0]} {f}")
		print()

# Display Summary
if not (args['brief'] or args['compact']):
	print("Summary\n-------")
if not args['compact']:
	print(f"Started at {start_date}")
totalfiles = num_src_files + num_dst_files
totaldirs = num_src_dirs + num_dst_dirs
if args['single']:
	print(f"{totaldirs + 1} dirs, {totalfiles} files analyzed including {args['srcdir']}.")
else:
	print(f"{totaldirs + 2} dirs, {totalfiles} files analyzed including {args['srcdir']} and {args['dstdir']}.")
print(f"{num_src_dirs} dirs, {num_src_files} files found in {args['srcdir']}.")
if not args['single']:
	print(f"{num_dst_dirs} dirs, {num_dst_files} files found in {args['dstdir']}.")
	print(f"{num_src_only_duplicates} duplicate files found in {args['srcdir']}.")
	print(f"{num_dst_only_duplicates} duplicate files found in {args['dstdir']}.")
	print(f"{num_exact_match} exact matches found.")
	print(f"{num_src_only_files} files only exist in {args['srcdir']}.")
	print(f"{num_dst_only_files} files only exist in {args['dstdir']}.")
	print(f"{num_match_name_diff_digest} files have same names but different digests.")
	print(f"{num_diff_name_match_digest} files have different names but same digest.")
else:
	print(f"{num_src_only_duplicates} duplicate files found in {args['srcdir']}.")

final = time.time()

totaltime = round(final - start_time, 2)
if not args['compact']:
	print("Finished at ", end="")
	print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
if not (args['brief'] or args['compact']):
	print()
	print(f"Total running time: {totaltime}s.")
