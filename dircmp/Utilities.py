import argparse
import hashlib
import random
import sys
from collections import defaultdict
from os import listdir, walk
from os.path import getsize, isdir, join, isfile, relpath, split
import  Globals

class Utilities:

    @staticmethod
    def calculate_full_digest(file_to_digest):
        hasher = hashlib.sha1()
        with open(file_to_digest, 'rb') as afile:
            buf = afile.read(Globals.BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(Globals.BLOCKSIZE)
        digest = hasher.hexdigest()
        afile.close()
        return digest

    # Calculate sha1 digests
    # return a dictionary of files and digests and a reverse index of the dictionary
    @staticmethod
    def calculate_sha1s(dir_to_parse, display, files, src_files_bytes):
        if not (Globals.ARGS['brief'] or Globals.ARGS['compact']):
            print(f"Calculating sha1 digests in {display} ", end="")
        files_dict = {}
        current_progress = 0
        for f in files:
            if isfile(dir_to_parse + f):
                if Globals.ARGS['fast']:
                    files_dict[f] = Utilities.calculate_shallow_digest(dir_to_parse + f)
                else:
                    files_dict[f] = Utilities.calculate_full_digest(dir_to_parse + f)
                current_progress = current_progress + getsize(dir_to_parse + f)
                Utilities.display_progress(current_progress, src_files_bytes, 50)

        # Create revidx_src_files, a reverse index for searching src_files_dict by value
        revidx = defaultdict(set)
        for key, value in files_dict.items():
            revidx[value].add(key)

        return [files_dict, revidx]

    # Calculate a sha1 digest from the encoded filesize in bytes,
    # plus the first and last SAMPLESIZE bytes of file
    # this is the -f --fast method
    # returns the calculated hex encoded digest
    @staticmethod
    def calculate_shallow_digest(file_to_digest):
        # seed the random number generator
        random.seed(Globals.SEED)
        hasher = hashlib.sha1()
        size = getsize(file_to_digest)

        if Globals.ARGS['debug']:
            print(f"size: {size}")
        # check if size <= 10 MB
        if size <= (10 * 1024 * 1024):
            if Globals.ARGS['debug']:
                print("using regular digest")
            # return regular digest
            with open(file_to_digest, 'rb', Globals.BUFFERING) as afile:
                buf = afile.read(Globals.BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(Globals.BLOCKSIZE)
            hasher.hexdigest()
            afile.close()
        else:
            with open(file_to_digest, "rb", Globals.BUFFERING) as afile:
                hasher.update(str.encode(str(size)))
                buf = afile.read(Globals.SAMPLESIZE)
                hasher.update(buf)
                afile.seek(size - Globals.SAMPLESIZE)
                buf = afile.read(Globals.SAMPLESIZE)
                hasher.update(buf)
            afile.close()
        digest = hasher.hexdigest()
        if Globals.ARGS['debug']:
            print(digest)
        return digest

    # Calulate a total size from a list of files
    @staticmethod
    def calculate_total_size_of_files(path, files):
        total = 0
        for f in files:
            total = total + getsize(path + f)
        return total

    @staticmethod
    def display_command_line():
        print("Arguments:", end=" ")
        for i in range(1, len(sys.argv)):
            print(sys.argv[i], end="")
            if i < len(sys.argv):
                print(" ", end="")
        print()

    # Display a dictionary in specified order, default is key, value
    @staticmethod
    def display_dictionary(dict_to_display, display, num, sortorder="kv", displayorder="kv",):
        if not Globals.ARGS['brief']:
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
            if not (Globals.ARGS['brief'] or Globals.ARGS['compact']):
                print()

    # --------------------------------------------
    # -- display_duplicates_dict(self, duplicates, dir_to_display)
    # --
    # -- description:
    # --    display a dictionary of duplicates
    # --
    # -- parameters:
    # --     duplicates - filename and digests for first
    # --     dir_to_display - the name of directory with duplicates
    # --
    # -- returns:
    # --     none
    # --
    #--  globals referenced:
    #--     none
    #--
    # -- instance variables referenced:
    # --     ARGS_dict - brief
    # --
    # -- instance variables affected:
    # --     none
    # --------------------------------------------
    @staticmethod
    def display_duplicates_dict(duplicates, dir_to_display):
        revidx_duplicates = defaultdict(set)
        for key, value in duplicates.items():
            revidx_duplicates[value].add(key)

        # create a sorted list of get_unique_values_list first only duplicate digests
        tvals = []
        for i in duplicates.values():
            if i not in tvals:
                tvals.append(i)
        tvals.sort()
        num_duplicates = len(duplicates)

        # Display the list of first only duplicates
        if not Globals.ARGS['brief']:
            print(f"Duplicates found in {dir_to_display}: {num_duplicates} files found.")
            for v in tvals:
                keys = sorted(revidx_duplicates.get(v))
                if keys is not None:
                    for f in keys:
                        print(f"{v} {f}")
            print()

    # Display dots when doing long-running tasks (needs improvements)
    @staticmethod
    def display_progress(curr, total, inc):
        if Globals.ARGS['brief'] or Globals.ARGS['compact']:
            return
        if Globals.ARGS['debug']:
            print(f"curr: {curr}")
            print(f"total: {total}")
            print(f"inc: {inc}")
        if total - curr > 0:
            # fudge curr as simple fix for div by zero
            # per_progress = int((total / (curr + .00001)) * 100)
            if curr % (100 / inc):
                print(".", end="")
                sys.stdout.flush()

    # --------------------------------------------
    #-- get_diff_names_same_digests_list(self, ldigests, rdigests)
    #--
    #-- description:
    #--     this is probably the most complex comparison returning a list of lists where the idea is to note
    #--     the files having different names but the same digest
    #--
    #-- parameters:
    #--     ldigests - a list of digests from first
    #--     rdigests - a list of digests from second
    #--
    #-- returns:
    #--     digest - a list containing lists that contain a digest and the files matching that digest but with different names
    #--
    #-- instance variables referenced:
    #--     ARGS_dict - brief, compact
    #--
    #-- instance variables affected:
    #--     none
    # --------------------------------------------
    @staticmethod
    def get_diff_names_same_digests_list(ldigests, rdigests):
        if not (Globals.ARGS['brief'] or Globals.ARGS['compact']):
            print(f"Checking for different names, same digest ...", end="")
        digest = []
        for k, v in ldigests.items():
            for j, u in rdigests.items():
                if k == j:
                    nlist = Utilities.get_unique_values_list(v + u)
                    nlist.sort(reverse=True, key=lambda name: (name[0:3]))
                    nlist.sort(key=lambda e: e.split(':')[-1])
                    nlist.sort(reverse=True, key=lambda e: e.split(':')[0])
                    digest.append([k, nlist])
        return digest

    #--------------------------------------------
    #-- get_duplicates_dict(self, dict_to_analyze, revidx, display)
    #--
    #-- description:
    #--     takes a dictionary of filenames and digests and reverse index (digests with filenames) and
    #--         scans for matching digests, building the duplicates dictionary to return
    #--
    #-- parameters:
    #--     dict_to_analyze - a dictionary of filenames and digests
    #--     revidx - a dictionary of digests with filenames for dupe checking
    #--     display - a string to display on output
    #--
    #-- returns:
    #--     duplicates - a dictionary of filenames with digests of duplicates (same digest)
    #--
    #--  globals referenced:
    #--     none
    #--
    #-- instance variables referenced:
    #--     ARGS_dict - brief, compact
    #--
    #-- instance variables affected:
    #--     none
    #--------------------------------------------
    # Analyze first directory for files having duplicate contents
    # return dictionary of duplicates
    @staticmethod
    def get_duplicates_dict(dict_to_analyze, revidx, display):
        if not (Globals.ARGS['brief'] or Globals.ARGS['compact']):
            print(f"Analyzing {display} directory ...", end="")

        duplicates = {}
        # look for duplicate content in first
        for key in dict_to_analyze.keys():
            ahash = dict_to_analyze[key]
            match_digest = revidx.get(ahash)
            if match_digest is not None:
                for fil in match_digest:
                    if key != fil:
                        duplicates[key] = ahash
        return duplicates

    # --------------------------------------------
    #-- get_files_list(self, dir_to_analyze, displayname)
    #--
    #-- description:
    #--     get list of files and directories contained in a directory, count them and calculate the size
    #--
    #-- parameters:
    #--     dir_to_analyze - the name of a directory to analyze with trailing slash
    #--     displayname - a string to print... Scanning {displayname}
    #--
    #-- returns:
    #--     files - a list of files in the directory
    #--     files_bytes - number of bytes in the files
    #--     num_dirs  - number of directories in the directory
    #--     num_files - number of files in the directory
    #--
    #--  globals referenced:
    #--     none
    #--
    #-- instance variables referenced:
    #--     none
    #--
    #-- instance variables affected:
    #--     none
    #--------------------------------------------
    @staticmethod
    def get_files_list(dir_to_analyze, displayname):
        if not (Globals.ARGS['brief'] or Globals.ARGS['compact']):
            print(f"Scanning {displayname} ...", end="")
        [num_dirs, num_files, files] = Utilities.get_files_recursively(dir_to_analyze, Globals.ARGS['recurse'], Globals.ARGS['all'])
        files_bytes = Utilities.calculate_total_size_of_files(dir_to_analyze, files)
        return [files, files_bytes, num_dirs, num_files]

    # Create a list of dirs and files from a root
    @staticmethod
    def get_files_recursively(dir_to_analyze, recurse, all_flag):
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

    @staticmethod
    # function to get get_unique_values_list values from a list
    def get_unique_values_list(list1):
        # insert the list to the set
        list_set = set(list1)
        # convert the set to the list
        unique_list = (list(list_set))
        return unique_list

    @staticmethod
    def parse_arguments(version):
        # positional arguments:
        #  firstdir			a source directory
        #  seconddir			a destination directory
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
        parser.add_argument('firstdir', metavar='firstdir', type=str,
                            help='a source directory')
        parser.add_argument('seconddir', nargs="?", metavar='seconddir', type=str,
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
                            version='%(prog)s {version}'.format(version=version))
        args = vars(parser.parse_args())
        args['firstdir'] = join(args['firstdir'], '')
        if not args['single']:
            if not args['seconddir']:
                print(f"Destination missing")
                sys.exit()
            args['seconddir'] = join(args['seconddir'], '')

        # check if first and second exist and are directories
        # bail otherwise
        if not isdir(args['firstdir']):
            print(f"{args['firstdir']} is not a directory")
            sys.exit()

        if not args['single'] and not isdir(args['seconddir']):
            print(f"{args['seconddir']} is not a directory")
            sys.exit()

        return args

        # Caculate a sha1 digest from file entire contents of file
        # this is the default method
        # returns the calculated hex encoded digest
