import hashlib
import random
import sys
from collections import defaultdict
from os import listdir, walk
from os.path import getsize, isdir, join, isfile, relpath, split

class Utils:
    # Caculate a sha1 digest from file entire contents of file
    # this is the default method
    # returns the calculated hex encoded digest
    @staticmethod
    def calculate_full_digest(file_to_digest, config):
        hasher = hashlib.sha1()
        with open(file_to_digest, 'rb') as afile:
            buf = afile.read(config.BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(config.BLOCKSIZE)
        digest = hasher.hexdigest()
        afile.close()
        return digest

    # Calculate sha1 digests
    # return a dictionary of files and digests and a reverse index of the dictionary
    @staticmethod
    def calculate_sha1s(dir_to_parse, display, files, src_files_bytes, logger, config):
        if not (config.brief or config.compact):
            logger.info(f"Calculating sha1 digests in {display} ")
        files_dict = {}
        current_progress = 0
        for f in files:
            if isfile(dir_to_parse + f):
                if config.fast:
                    files_dict[f] = Utils.calculate_shallow_digest(dir_to_parse + f, logger, config)
                else:
                    files_dict[f] = Utils.calculate_full_digest(dir_to_parse + f, config)
                current_progress = current_progress + getsize(dir_to_parse + f)
                Utils.display_progress(current_progress, src_files_bytes, 50, logger, config)

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
    def calculate_shallow_digest(file_to_digest, logger, config):
        # seed the random number generator
        random.seed(config.SEED)
        hasher = hashlib.sha1()
        size = getsize(file_to_digest)

        logger.debug(f"size: {size}")

        # check if size <= 10 MB
        if size <= (10 * 1024 * 1024):
            logger.debug("using regular digest")

            # return regular digest
            with open(file_to_digest, 'rb', config.BUFFERING) as afile:
                buf = afile.read(config.BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(config.BLOCKSIZE)
            hasher.hexdigest()
            afile.close()
        else:
            with open(file_to_digest, "rb", config.BUFFERING) as afile:
                hasher.update(str.encode(str(size)))
                buf = afile.read(config.SAMPLESIZE)
                hasher.update(buf)
                afile.seek(size - config.SAMPLESIZE)
                buf = afile.read(config.SAMPLESIZE)
                hasher.update(buf)
            afile.close()
        digest = hasher.hexdigest()
        logger.debug(digest)
        return digest

    # Calulate a total size from a list of files
    @staticmethod
    def calculate_total_size_of_files(path, files):
        total = 0
        for f in files:
            total = total + getsize(path + f)
        return total

    @staticmethod
    def display_command_line(logger):
        outstr = ""
        outstr += "Arguments:"
        for i in range(1, len(sys.argv)):
            outstr+= sys.argv[i]
            if i < len(sys.argv):
                outstr += " "
        logger.info(outstr)

    # Display a dictionary in specified order, default is key, value
    @staticmethod
    def display_dictionary(dict_to_display, display, num, logger, config, sortorder="kv", displayorder="kv"):
        if not config.brief:
            logger.info(f"{display}: {num} files found.")
        if sortorder == "kv":
            for k, v in sorted(dict_to_display.items(), key=lambda x: (x[0], x[1])):
                if displayorder == "kv":
                    logger.info(f"{k} {v}")
                else:
                    logger.info(f"{v} {k}")

        elif sortorder == "vk":
            for k, v in sorted(dict_to_display.items(), key=lambda x: (x[1], x[0])):
                if displayorder == "kv":
                    logger.info(f"{k} {v}")
                else:
                    logger.info(f"{v} {k}")


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
    # --  globals referenced:
    # --     none
    # --
    # -- instance variables referenced:
    # --     ARGS_dict - brief
    # --
    # -- instance variables affected:
    # --     none
    # --------------------------------------------
    @staticmethod
    def display_duplicates_dict(duplicates, dir_to_display, logger, config):
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
        if not config.brief:
            logger.info(f"Duplicates found in {dir_to_display}: {num_duplicates} files found.")
            for v in tvals:
                keys = sorted(revidx_duplicates.get(v))
                if keys is not None:
                    for f in keys:
                        logger.info(f"{v} {f}")


    # Display dots when doing long-running tasks (needs improvements)
    @staticmethod
    def display_progress(curr, total, inc, logger, config):
        if config.brief or config.compact:
            return
        if config.debug:
            logger.debug(f"curr: {curr}")
            logger.debug(f"total: {total}")
            logger.debug(f"inc: {inc}")
        if total - curr > 0:
            # fudge curr as simple fix for div by zero
            # per_progress = int((total / (curr + .00001)) * 100)
            pass    # preparatory to the move to gui, and after adding logging, just gonna pass on printing dots
            #if curr % (100 / inc):
            #    print(".", end="")
            #    sys.stdout.flush()

    # --------------------------------------------
    # -- get_diff_names_same_digests_list(self, ldigests, rdigests)
    # --
    # -- description:
    # --     this is probably the most complex comparison returning a list of lists where the idea is to note
    # --     the files having different names but the same digest
    # --
    # -- parameters:
    # --     ldigests - a list of digests from first
    # --     rdigests - a list of digests from second
    # --
    # -- returns:
    # --     digest - a list containing lists that contain a digest and the files matching that digest but with different names
    # --
    # -- instance variables referenced:
    # --     ARGS_dict - brief, compact
    # --
    # -- instance variables affected:
    # --     none
    # --------------------------------------------
    @staticmethod
    def get_diff_names_same_digests_list(ldigests, rdigests, logger, config):
        if not (config.brief or config.compact):
            logger.info(f"Checking for different names, same digest ...")
        digest = []
        for k, v in ldigests.items():
            for j, u in rdigests.items():
                if k == j:
                    nlist = Utils.get_unique_values_list(v + u)
                    nlist.sort(reverse=True, key=lambda name: (name[0:3]))
                    nlist.sort(key=lambda e: e.split(':')[-1])
                    nlist.sort(reverse=True, key=lambda e: e.split(':')[0])
                    digest.append([k, nlist])
        return digest


    # --------------------------------------------
    # -- get_duplicates_dict(self, dict_to_analyze, revidx, display)
    # --
    # -- description:
    # --     takes a dictionary of filenames and digests and reverse index (digests with filenames) and
    # --         scans for matching digests, building the duplicates dictionary to return
    # --
    # -- parameters:
    # --     dict_to_analyze - a dictionary of filenames and digests
    # --     revidx - a dictionary of digests with filenames for dupe checking
    # --     display - a string to display on output
    # --
    # -- returns:
    # --     duplicates - a dictionary of filenames with digests of duplicates (same digest)
    # --
    # --  globals referenced:
    # --     none
    # --
    # -- instance variables referenced:
    # --     ARGS_dict - brief, compact
    # --
    # -- instance variables affected:
    # --     none
    # --------------------------------------------
    # Analyze first directory for files having duplicate contents
    # return dictionary of duplicates
    @staticmethod
    def get_duplicates_dict(dict_to_analyze, revidx, display, logger, config):
        if not (config.brief or config.compact):
            logger.info(f"Analyzing {display} directory ...")

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
    # -- get_files_list(self, dir_to_analyze, displayname)
    # --
    # -- description:
    # --     get list of files and directories contained in a directory, count them and calculate the size
    # --
    # -- parameters:
    # --     dir_to_analyze - the name of a directory to analyze with trailing slash
    # --     displayname - a string to logger.info... Scanning {displayname}
    # --
    # -- returns:
    # --     files - a list of files in the directory
    # --     files_bytes - number of bytes in the files
    # --     num_dirs  - number of directories in the directory
    # --     num_files - number of files in the directory
    # --
    # --  globals referenced:
    # --     none
    # --
    # -- instance variables referenced:
    # --     none
    # --
    # -- instance variables affected:
    # --     none
    # --------------------------------------------
    @staticmethod
    def get_files_list(dir_to_analyze, displayname, logger, config):
        if not (config.brief or config.compact):
            logger.info(f"Scanning {displayname} ...")
        [num_dirs, num_files, files] = Utils.get_files_recursively(dir_to_analyze, config.recurse,
                                                                   config.all)
        files_bytes = Utils.calculate_total_size_of_files(dir_to_analyze, files)
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
    def validate_directories(args):
        if not isdir(args.firstdir):
            raise ValueError(f"{args.firstdir} is not a directory")
        if not args.single and not isdir(args.seconddir):
            raise ValueError(f"{args.seconddir} is not a directory")

