import asyncio
import hashlib
import random
import sys
import time
from collections import defaultdict
from os import walk, scandir
from os.path import getsize, isdir, join, isfile, relpath

class Utils:
    @staticmethod
    def calculate_full_digest(file_to_digest, config):
        """
        Calculates the SHA-1 digest of a file's entire contents.

        This is the default method for generating the digest of a file.

        Parameters:
        file_to_digest (str): The path to the file whose digest is to be calculated.
        config (Config): The configuration object that may influence the digest calculation.

        Returns:
        str: The calculated hex-encoded SHA-1 digest of the file's contents.
        """
        hasher = hashlib.sha1()
        with open(file_to_digest, 'rb') as afile:
            buf = afile.read(config.BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(config.BLOCKSIZE)
        digest = hasher.hexdigest()
        afile.close()
        return digest

    @staticmethod
    def calculate_sha1s(dir_to_parse, display, files, num_files, src_files_bytes, logger, config):
        """
        Calculates SHA-1 digests for files in a given directory.

        This method generates a dictionary of file names and their corresponding SHA-1 digests,
        as well as a reverse index of the dictionary.

        Parameters:
        dir_to_parse (str): The directory to parse for files.
        display (bool): Flag indicating whether to display progress or results.
        files (list): List of files to process.
        src_files_bytes (dict): A dictionary mapping file names to their byte content.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        tuple: A tuple containing:
            - digests_dict (dict): A dictionary mapping file names to their SHA-1 digests.
            - reverse_index (dict): A reverse index of the file-to-digest dictionary.
        """
        if not (config.brief or config.compact):
            logger.info(f"Calculating sha1 digests in {display} ")
        files_dict = {}
        current_progress = 0
        increment = num_files // 10  # Define increment as 1% of total size

        for f in files:
            if isfile(dir_to_parse + f):
                if config.fast:
                    files_dict[f] = Utils.calculate_shallow_digest(dir_to_parse + f, logger, config)
                else:
                    files_dict[f] = Utils.calculate_full_digest(dir_to_parse + f, config)

                current_progress += 1

                # Only log if progress exceeds last logged progress by increment
                if current_progress % increment == 0:
                    Utils.display_progress(current_progress, num_files, logger, config)

            else:
                logger.debug(f"Not a file: {dir_to_parse + f}")

        # Create revidx_src_files, a reverse index for searching src_files_dict by value
        revidx = defaultdict(set)
        for key, value in files_dict.items():
            revidx[value].add(key)

        return [files_dict, revidx]

    @staticmethod
    def calculate_shallow_digest(file_to_digest, logger, config):
        """
        Calculates a SHA-1 digest from the encoded file size in bytes,
        plus the first and last SAMPLESIZE bytes of the file.

        This is the -f --fast method.

        Parameters:
        file_to_digest (str): The path to the file whose digest is to be calculated.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        str: The calculated hex-encoded SHA-1 digest.
        """

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

    @staticmethod
    def calculate_total_size_of_files(path, files):
        """
        Calculates the total size of a list of files.

        Parameters:
        path (str): The directory path where the files are located.
        files (list): A list of file names to calculate the total size for.

        Returns:
        int: The total size of the files in bytes.
        """
        total = 0
        for f in files:
            total = total + getsize(path + f)
        return total

    @staticmethod
    def display_command_line(logger):
        """
        Displays the command line arguments that were passed to the program.

        Parameters:
        logger (Logger): The logger instance used for logging output.

        Returns:
        None
        """
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
        """
        Displays a dictionary in a specified order.

        Parameters:
        dict_to_display (dict): The dictionary to be displayed.
        display (bool): Flag indicating whether to display the dictionary.
        num (int): Number of entries to display.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.
        sortorder (str, optional): The order to sort the dictionary, either "kv" for key-value or "vk" for value-key. Defaults to "kv".
        displayorder (str, optional): The order in which to display dictionary entries, either "kv" for key-value or "vk" for value-key. Defaults to "kv".

        Returns:
        None
        """
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

    @staticmethod
    def display_duplicates_dict(duplicates, dir_to_display, logger, config):
        """
        Displays a dictionary of duplicates.

        Parameters:
        duplicates (dict): A dictionary mapping file names to their corresponding digests.
        dir_to_display (str): The name of the directory containing the duplicates.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        None
        """
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
    def display_progress(curr, total, logger, config):
        """
        Displays progress of a long-running task by outputting updates.

        Parameters:
        curr (int): The current progress or step.
        total (int): The total number of steps.
        inc (int): The increment step for progress.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        None
        """
        if config.brief or config.compact:
            return
        if config.debug:
            logger.debug(f"curr: {curr}")
            logger.debug(f"total: {total}")

        # Display the progress (you can adjust this to be more concise if needed)
        per_progress = int((curr / total) * 100)  # Percentage progress
        logger.info(f"Progress: {curr}/{total} files ({per_progress}%)")

    @staticmethod
    def find_files_same_digests_diff_names(ldigests, rdigests, logger, config):
        """
        Compares two lists of digests and returns files with the same digest but different names.

        Parameters:
        ldigests (list): A list of digests from the first set of files.
        rdigests (list): A list of digests from the second set of files.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        list: A list of lists where each sublist contains a digest and the files that share the same digest but have different names.
        """

        # Log the action if neither brief nor compact modes are enabled
        if not (config.brief or config.compact):
            logger.info(f"Checking for different names, same digest ...")

        # Initialize a list to hold the final results
        digest = []

        # Iterate over each digest in the first source (ldigests)
        for k, v in ldigests.items():
            # Check if the digest also exists in the second source (rdigests)
            if k in rdigests:
                # Combine the lists of file names from both sources for this matching digest amd remove duplicates
                nlist = list(dict.fromkeys(v + rdigests[k]))

                # Sort the combined list:
                # - First, sort by the part before the colon (reverse order)
                # - Second, sort by the part after the colon (ascending order)
                nlist.sort(key=lambda e: (e.split(':')[0], e.split(':')[-1]), reverse=True)

                # Append the sorted list of names along with the digest to the result list
                digest.append([k, nlist])

        # Return the list of digests and their corresponding sorted names
        return digest


    @staticmethod
    def get_duplicates_dict(dict_to_analyze, revidx, display, logger, config):
        """
        Scans a dictionary of filenames and digests, and identifies files with matching digests.

        Parameters:
        dict_to_analyze (dict): A dictionary of filenames and their corresponding digests.
        revidx (dict): A reverse index of digests with filenames for duplicate checking.
        display (str): A string to display on output.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        dict: A dictionary mapping filenames to their corresponding digests of duplicate files (same digest).
        """
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

    @staticmethod
    def get_files_list(dir_to_analyze, displayname, logger, config):
        """
        Retrieves a list of files and directories in a specified directory,
        and calculates the total size and counts of files and directories.

        Parameters:
        dir_to_analyze (str): The directory to analyze, including the trailing slash.
        displayname (str): A string to log, indicating the directory being scanned.
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

        Returns:
        tuple: A tuple containing:
            - files (list): A list of files in the directory.
            - files_bytes (int): Total size in bytes of the files.
            - num_dirs (int): The number of directories in the directory.
            - num_files (int): The number of files in the directory.
        """
        if not (config.brief or config.compact):
            logger.info(f"Scanning {displayname} ...")
        result = Utils.get_files_recursively(dir_to_analyze, config.recurse, config.all, logger)
        files_bytes = Utils.calculate_total_size_of_files(dir_to_analyze, result["files"])
        return [result["files"], files_bytes, result["directory_count"], result["file_count"]]

    @staticmethod
    def get_files_recursively(dir_to_analyze, recurse=False, all_flag=False, logger=None):
        """
        Creates a list of directories and files from a specified root directory, optionally
        including subdirectories and all files based on the flags.

        Parameters:
        dir_to_analyze (str): The root directory to analyze.
        recurse (bool, optional): Whether to include subdirectories. Defaults to False.
        all_flag (bool, optional): Whether to include all files, including hidden ones. Defaults to False.
        logger (Logger, optional): Logger instance to log progress.

        Returns:
        dict: A dictionary with the counts of directories and files, and a list of file paths.
        """
        start_time = time.time()
        scanned_files = 0
        scanned_dirs = 0
        total_files = 0
        total_dirs = 0
        all_files = []

        def should_include(name):
            return all_flag or not name.startswith('.')

        def count_and_filter_entries(path):
            nonlocal scanned_files, scanned_dirs
            file_count, dir_count, entries = 0, 0, []
            with scandir(path) as it:
                for entry in it:
                    if should_include(entry.name):
                        if entry.is_dir():
                            dir_count += 1
                        if entry.is_file():
                            file_count += 1
                            entries.append(entry.path)
            scanned_files += file_count
            scanned_dirs += dir_count
            return file_count, dir_count, entries

        if not recurse:
            file_count, dir_count, entries = count_and_filter_entries(dir_to_analyze)
            all_files.extend(relpath(e, dir_to_analyze) for e in entries)
            total_files += file_count
            total_dirs += dir_count
        else:
            for root, dirs, files in walk(dir_to_analyze):
                if not should_include(root):
                    continue
                rel_root = relpath(root, dir_to_analyze)
                if rel_root != ".":
                    all_files.append(rel_root)
                for file in files:
                    if should_include(file):
                        total_files += 1
                        all_files.append(relpath(join(root, file), dir_to_analyze))
                for dir in dirs:
                    if should_include(dir):
                        total_dirs += 1

        return {"directory_count": total_dirs, "file_count": total_files, "files": all_files}

    @staticmethod
    def validate_directories(dirs):
        """
        Validates a list of directories to ensure they exist.

        Parameters:
        dirs (list): A list of directory paths to validate.

        Returns:
        bool: True if all directories exist, False otherwise.
        """

        for dir in dirs:
            if not isdir(dir):
                raise ValueError(f"{dir} is not a directory")

