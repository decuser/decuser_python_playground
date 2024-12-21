import hashlib
import sys
import time
from collections import defaultdict
from os import scandir
from os.path import getsize, isdir, isfile, relpath


class Utils:
    @staticmethod
    def calculate_full_digest(
            config,
            logger,
            file_to_digest,
            start_time,
            total_files,
            total_files_processed,
            total_bytes,
            total_bytes_processed,
            total_bytes_remaining,
            total_bytes_accounted_for):
        """
         Calculates the SHA-1 digest of a file's entire contents.

         This is the default method for generating the digest of a file.

         Parameters:
             config (Config): Configuration object containing options like buffer size and progress interval.
             logger (Logger): Logger instance for progress and debug messages.
             file_to_digest (str): Path to the file whose digest is to be calculated.
             start_time (float): Start time of the operation, used for progress logging.
             total_files (int): Total number of files to process.
             total_files_processed (int): Number of files processed so far.
             total_bytes (int): Total bytes across all files being processed.
             total_bytes_processed (int): Total bytes processed across all files.
             total_bytes_remaining (int): Remaining bytes to be processed.
             total_bytes_accounted_for (int): Bytes accounted for by the digests so far.

         Returns:
             dict: A dictionary containing:
                 - 'start_time' (float): Updated start time for progress tracking.
                 - 'total_files_processed' (int): Updated count of processed files.
                 - 'total_bytes_processed' (int): Updated total bytes processed.
                 - 'total_bytes_remaining' (int): Updated remaining bytes.
                 - 'total_bytes_accounted_for' (int): Updated bytes accounted for by digests.
                 - 'digest' (str): Calculated SHA-1 digest (hex-encoded).
         """
        time_interval = config.PROGRESS_UPDATE_INTERVAL
        size = getsize(file_to_digest)
        total_bytes_accounted_for += size

        hasher = hashlib.sha1()

        with open(file_to_digest, 'rb') as afile:
            buf = afile.read(config.BLOCKSIZE)
            buflen = len(buf)
            total_bytes_processed += buflen
            total_bytes_remaining -= buflen
            while buflen > 0:
                hasher.update(buf)
                buf = afile.read(config.BLOCKSIZE)
                buflen = len(buf)
                total_bytes_processed += buflen
                total_bytes_remaining -= buflen
                elapsed_time = time.time() - start_time
                if elapsed_time >= time_interval:
                    percent = round((total_bytes_processed / total_bytes * 100), 2)
                    logger.info(
                        f"Processed {percent}% - {Utils.convert_bytes_to_human_readable(total_bytes_processed)} for digest "
                        f"({Utils.convert_bytes_to_human_readable(total_bytes_processed)} of {Utils.convert_bytes_to_human_readable(total_bytes)}), "
                        f"{Utils.convert_bytes_to_human_readable(total_bytes_remaining)} remaining "
                        f"({total_files_processed}/{total_files} files processed).")
                    start_time = time.time()

                if total_bytes_remaining < 0:
                    logger.debug(
                        f"total byte: {total_bytes} - total bytes processed {total_bytes_processed} = total bytes remaining {total_bytes_remaining}")

        total_files_processed += 1
        digest = hasher.hexdigest()
        logger.debug(f"Digest: {digest}")

        return {'start_time': start_time,
                'total_files_processed': total_files_processed,
                'total_bytes_processed': total_bytes_processed,
                'total_bytes_remaining': total_bytes_remaining,
                'total_bytes_accounted_for': total_bytes_processed,
                'digest': digest,
                }

    @staticmethod
    def calculate_sha1s(dir_to_parse, display, files, file_bytes, logger, config):
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

        # track cumulative vars (for use in calculating progress)
        # these are passed to the digest calculation routines and returned by them as a dictionary tuple
        start_time = time.time()  # time since last reset
        total_files = len(files)
        total_files_processed = 0  # files processed
        total_bytes = file_bytes
        total_bytes_processed = 0  # bytes processed
        total_bytes_remaining = file_bytes  # files left to process
        total_bytes_accounted_for = 0  # when doing shallow digests this keeps track of the full file size

        for f in files:
            if isfile(dir_to_parse + f):
                if config.fast:
                    results = Utils.calculate_shallow_digest(
                        config,
                        logger,
                        dir_to_parse + f,
                        start_time,
                        total_files,  # stays the same throughout calulation
                        total_files_processed,
                        total_bytes,  # stays the same throughout calculation
                        total_bytes_processed,
                        total_bytes_remaining,
                        total_bytes_accounted_for)

                    # Update variables based on the result
                    start_time = results['start_time']
                    total_files_processed = results['total_files_processed']
                    total_bytes_processed = results['total_bytes_processed']
                    total_bytes_remaining = results['total_bytes_remaining']
                    total_bytes_accounted_for = results['total_bytes_accounted_for']
                    files_dict[f] = results['digest']

                else:
                    results = Utils.calculate_full_digest(
                        config,
                        logger,
                        dir_to_parse + f,
                        start_time,
                        total_files,
                        total_files_processed,
                        total_bytes,
                        total_bytes_processed,
                        total_bytes_remaining,
                        total_bytes_accounted_for)
                    #                    total_files_processed = results['files_processed']
                    start_time = results['start_time']
                    total_files_processed = results['total_files_processed']
                    total_bytes_processed = results['total_bytes_processed']
                    total_bytes_remaining = results['total_bytes_remaining']
                    total_bytes_accounted_for = results['total_bytes_accounted_for']
                    files_dict[f] = results['digest']
            else:
                logger.debug(f"Not a file: {dir_to_parse + f}")

        logger.info(
            f"Processed {Utils.convert_bytes_to_human_readable(total_bytes_processed)} for digest "
            f"({Utils.convert_bytes_to_human_readable(total_bytes_accounted_for)} of files), "
            f"{Utils.convert_bytes_to_human_readable(total_bytes_remaining)} remaining "
            f"({total_files_processed}/{total_files} files processed).")

        # Create revidx_src_files, a reverse index for searching src_files_dict by value
        revidx = defaultdict(set)
        for key, value in files_dict.items():
            revidx[value].add(key)

        return [files_dict, revidx]

    @staticmethod
    def calculate_shallow_digest(
            config,
            logger,
            file_to_digest,
            start_time,
            total_files,
            total_files_processed,
            total_file_bytes,
            total_bytes_processed,
            total_bytes_remaining,
            total_bytes_accounted_for):
        """
        Calculates a fast SHA-1 digest for a file using a hybrid approach:
        - For files ≤ 10 MB: Reads and hashes the entire file.
        - For files > 10 MB: Hashes the file size (in bytes) along with the first and last
          `SAMPLESIZE` bytes of the file.

        This approach balances speed and integrity, making it suitable for scenarios
        where small files are more likely to be edited, and efficiency is prioritized
        for larger files.

        Parameters:
            file_to_digest (str): Path to the file whose digest is to be calculated.
            start_time (float): Start time of the operation, used for progress logging.
            total_files_processed (int): Number of files processed so far.
            total_files (int): Total number of files to process.
            total_bytes_processed (int): Total bytes processed across all files.
            total_file_bytes (int): Total bytes across all files being processed.
            total_bytes_remaining (int): Remaining bytes to be processed.
            total_bytes_accounted_for (int): Bytes accounted for by the digests so far.
            logger (Logger): Logger instance for progress and debug messages.
            config (Config): Configuration object containing options like buffer size,
                             sampling size, and progress interval.

        Returns:
            dict: A dictionary containing:
                - 'total_files_processed' (int): Updated count of processed files.
                - 'total_bytes_processed' (int): Updated total bytes processed.
                - 'total_bytes_remaining' (int): Updated remaining bytes.
                - 'digest' (str): Calculated SHA-1 digest (hex-encoded).
                - 'start_time' (float): Updated start time for progress tracking.
        """
        time_interval = config.PROGRESS_UPDATE_INTERVAL

        hasher = hashlib.sha1()
        size = getsize(file_to_digest)
        total_bytes_accounted_for += size
        logger.debug(f"size: {size}")

        # check if size <= 10 MB
        if size <= (10 * 1024 * 1024):
            logger.debug("using regular digest")

            # regular digest
            with open(file_to_digest, 'rb', config.BUFFERING) as afile:
                buf = afile.read(config.BLOCKSIZE)
                buflen = len(buf)
                while buflen > 0:
                    total_bytes_processed += buflen
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= time_interval:
                        percent = round((total_bytes_accounted_for / total_file_bytes * 100), 2)
                        logger.info(
                            f"Processed {percent}% - {Utils.convert_bytes_to_human_readable(total_bytes_processed)} for digest "
                            f"({Utils.convert_bytes_to_human_readable(total_bytes_accounted_for)} of files), "
                            f"{Utils.convert_bytes_to_human_readable(total_bytes_remaining)} remaining "
                            f"({total_files_processed}/{total_files} files processed).")
                        start_time = time.time()
                    hasher.update(buf)
                    buf = afile.read(config.BLOCKSIZE)
                    buflen = len(buf)
        else:
            with open(file_to_digest, "rb", config.BUFFERING) as afile:
                hasher.update(str.encode(str(size)))
                buf = afile.read(config.SAMPLESIZE)
                buflen = len(buf)
                total_bytes_processed += buflen
                hasher.update(buf)
                afile.seek(size - config.SAMPLESIZE)
                buf = afile.read(config.SAMPLESIZE)
                hasher.update(buf)
            elapsed_time = time.time() - start_time
            if elapsed_time >= time_interval:
                percent = round((total_bytes_accounted_for / total_file_bytes * 100), 2)
                logger.info(
                    f"Processed {percent}% - {Utils.convert_bytes_to_human_readable(total_bytes_processed)} for digest "
                    f"({Utils.convert_bytes_to_human_readable(total_bytes_accounted_for)} of files), "
                    f"{Utils.convert_bytes_to_human_readable(total_bytes_remaining)} remaining "
                    f"({total_files_processed}/{total_files} files processed).")
                start_time = time.time()
        total_bytes_remaining -= size
        total_files_processed += 1
        digest = hasher.hexdigest()
        logger.debug(digest)

        return {'start_time': start_time,
                'total_files_processed': total_files_processed,
                'total_bytes_processed': total_bytes_processed,
                'total_bytes_remaining': total_bytes_remaining,
                'total_bytes_accounted_for': total_bytes_accounted_for,
                'digest': digest,
                }

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
    def convert_bytes_to_human_readable(numbytes):
        """
        Return the given bytes as a human friendly kb, mb, gb, or tb string.

        xref: https://stackoverflow.com/a/31631711
        """
        numbytes = float(numbytes)
        kb = float(1024)
        mb = float(kb ** 2)  # 1,048,576
        gb = float(kb ** 3)  # 1,073,741,824
        tb = float(kb ** 4)  # 1,099,511,627,776

        if numbytes < kb:
            return '{0} {1}'.format(numbytes, 'Bytes' if 0 == numbytes > 1 else 'Byte')
        elif kb <= numbytes < mb:
            return '{0:.2f} KB'.format(numbytes / kb)
        elif mb <= numbytes < gb:
            return '{0:.2f} mb'.format(numbytes / mb)
        elif gb <= numbytes < tb:
            return '{0:.2f} gb'.format(numbytes / gb)
        elif tb <= numbytes:
            return '{0:.2f} tb'.format(numbytes / tb)

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
            outstr += sys.argv[i]
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

    @staticmethod
    def find_duplicates(dict_to_analyze, revidx, display, logger, config):
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
    def find_files(dir_to_analyze, displayname, logger, config):
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

        total_files = 0
        total_dirs = 0
        all_files = []

        def should_include(name):
            return config.all or not name.startswith('.')

        def process_directory(path, recurse=False):
            nonlocal total_files, total_dirs, all_files
            with scandir(path) as it:
                for entry in it:
                    if should_include(entry.name):
                        if entry.is_dir():
                            total_dirs += 1
                            if recurse:
                                process_directory(entry.path, recurse)
                        elif entry.is_file():
                            total_files += 1
                            all_files.append(relpath(entry.path, dir_to_analyze))

        if config.recurse:
            process_directory(dir_to_analyze, recurse=True)
        else:
            process_directory(dir_to_analyze, recurse=False)

        files_bytes = Utils.calculate_total_size_of_files(dir_to_analyze, all_files)
        return [all_files, files_bytes, total_dirs, total_files]

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
    def validate_directories(dirs):
        """
        Validates a list of directories to ensure they exist.

        Parameters:
        dirs (list): A list of directory paths to validate.

        Returns:
        bool: True if all directories exist, False otherwise.
        """

        for tdir in dirs:
            if not isdir(tdir):
                raise ValueError(f"{tdir} is not a directory")
