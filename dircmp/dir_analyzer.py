import re
import time
from datetime import datetime

from elapsed_time import ElapsedTime
from utils import Utils

#------------------------------------------------
#-- class DirAnalyzer
#--
#-- uses argparse.ArgumentParser to parse command line arguments into a dictionary - ARGS
#--
#-- constructor ARGS:
#--     none
#--
#-- methods:
#--     get_diff_names_same_digests_list
#--     get_files_list
#--     get_duplicates_dict
#--     compare_directories
#--     display_duplicates_dict
#--     display_welcome
#--     analyze
#--     display_results
#------------------------------------------------
class DirAnalyzer:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.first_only = {}                                                # files only found in first
        self.second_only = {}                                               # files only found in second
        self.exact_match = {}                                               # dictionary of exact matche
        self.first_digest_diff = {}                                         #
        self.second_digest_diff = {}                                        #
        self.diff_name_match_digest = []                                    #
        self.match_name_diff_digest = []                                    #
        self.first_only_duplicates = {}                                     # dictionary of duplicated found in first
        self.second_only_duplicates = {}                                    # dictionary of duplicates found in second
        self.num_second_files = 0                                           # number of files in second
        self.num_second_dirs = 0                                            # number of directories in second
        self.start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')   # datetime of istantiation
        self.start_time = time.time()                                       # start time for elapsed calculation
        self.timer = ElapsedTime(self.logger, self.config)                            # create the elapsed time timer

        self.num_first_only_files = []
        self.num_second_only_files = []
        self.num_exact_match = 0
        self.num_first_only_duplicates = 0
        self.num_second_only_duplicates = 0
        self.num_diff_name_match_digest = 0
        self.num_match_name_diff_digest = 0

        #--------------------------------------------
    #-- compare_directories(self, ldict, rrevidx, rdict, firsttxt, secondtxt)
    #--
    #-- description:
    #--     compares two directories for [exact match, same digest different name, same name different digests, only in]
    #--     this method gets called twice, once to compare first with second and again to compare second with first
    #--
    #-- parameters:
    #--     ldict - filename and digests for first
    #--     rrevidx - a dictionary of digests with filenames for comparison
    #--     rdict - filename and digests for second
    #--     firsttxt - a string to display on output for the first directory
    #--     secondtxt - a string to display on output for the second directory
    #--
    #-- returns:
    #--     only - filenames and digests of files only found in first
    #--     digest_diff - a dictionary of digests with mismatched names
    #--
    #--  globals referenced:
    #--     none
    #--
    #-- instance variables referenced:
    #--     ARGS_dict - brief, compact, firstdir, seconddir
    #--
    #-- instance variables affected:
    #--     exact_match
    #--     match_name_diff_digest
    #--------------------------------------------
    def _compare_directories(self, ldict, rrevidx, rdict, firsttxt, secondtxt):
        only = {}
        digest_diff = {}
        if not (self.config.brief or self.config.compact):
            self.logger.info(f"Comparing {firsttxt} to {secondtxt} ...")
        # look for first files in second
        for key in ldict.keys():
            ahash = ldict[key]

            # is the digest from first found in second?
            second_match_digest = rrevidx.get(ahash)
            if second_match_digest is not None:
                for fil in second_match_digest:
                    # does it have the same name in first and second?
                    if key == fil:
                        # if so, [exact match]
                        self.exact_match[key] = ahash
                    else:
                        # otherwise, [same digest different name]
                        # Is this digest already in diffs?
                        if ahash not in digest_diff:
                            # add the new digest to diffs
                            digest_diff[ahash] = []
                        # is the first filename in diffs already?
                        if f"{firsttxt}:{key}" not in digest_diff[ahash]:
                            # no? add it to the diffs
                            digest_diff[ahash].append(f"{firsttxt}:{key}")
                        # is the second filename in diffs already?
                        if f"{secondtxt}:{fil}" not in digest_diff[ahash]:
                            # no? add it to the diffs
                            digest_diff[ahash].append(f"{secondtxt}:{fil}")
            else:
                # check if filename from first found in second [digest mismatch]
                skey = re.sub(r'^' + re.escape(self.config.firstdir), self.config.seconddir, key)

                if skey in rdict.keys():
                    # check if this is already in same name different digest dictionary
                    # this is a hack to prevent displaying the same record twice
                    found = False
                    for k, lv, rv in self.match_name_diff_digest:
                        if skey == k:
                            found = True
                            break
                        else:
                            pass
                    if not found:
                        # go ahead and add it
                        self.match_name_diff_digest.append([key, ahash, rdict[skey]])
                # otherwise, the filename only exists in first [Only in]
                else:
                    only[key] = ahash

        return [only, digest_diff]

    # --------------------------------------------
    # -- analyze(self)
    # --
    # -- description:
    # --    organize and perform the analysis
    # --
    # -- parameters:
    # --     none
    # --
    # -- returns:
    # --     none
    # --
    # --  globals referenced:
    # --     none
    # --
    # -- instance variables referenced:
    # --     ARGS_dict, ARGS_dict - firstdir, single, seconddir
    # --     get_files_list

    # -- instance variables affected:


    # --     none
    # --------------------------------------------
    def analyze(self):
        # get the source files
        [self.first_files, self.first_files_bytes, self.num_first_dirs, self.num_first_files] = Utils.get_files_list(self.config.firstdir, "first", self.logger, self.config)
        self.timer.display(f" {self.num_first_files} files found ", "")

        # calculate first sha1s
        [self.first_files_dict, self.revidx_first_files] = Utils.calculate_sha1s(self.config.firstdir, "first", self.first_files, self.first_files_bytes, self.logger, self.config)
        self.timer.display(f" done ", "")

        if not self.config.single:
            # get the destination files
            [self.second_files, self.second_files_bytes, self.num_second_dirs, self.num_second_files] = Utils.get_files_list(self.config.seconddir, "second", self.logger, self.config)
            self.timer.display(f" {self.num_second_files} files found ", "")

            # calculate second sha1s
            [self.second_files_dict, self.revidx_second_files] = Utils.calculate_sha1s(self.config.seconddir, "second", self.second_files,
                                                                    self.first_files_bytes, self.logger, self.config)
            self.timer.display(f" done ", "")

            # get all duplicates in first
            self.first_only_duplicates = Utils.get_duplicates_dict(self.first_files_dict, self.revidx_first_files, "first", self.logger, self.config)
            self.timer.display(f"done ", "")

            # get all duplicates in second
            self.second_only_duplicates = Utils.get_duplicates_dict(self.second_files_dict, self.revidx_second_files, "second", self.logger, self.config)
            self.timer.display(f"done ", "")

            # Compare the files in first to those in second
            [self.first_only, self.first_digest_diff] = self._compare_directories(self.first_files_dict, self.revidx_second_files, self.second_files_dict,
                                                                 "first", "second")
            self.timer.display(f"done ", "")

            # Compare the files in second to those in first
            [self.second_only, self.second_digest_diff] = self._compare_directories(self.second_files_dict, self.revidx_first_files, self.first_files_dict,
                                                                 "second", "first")
            self.timer.display(f"done ", "")

            # Get list of files with different names but same digest
            self.diff_name_match_digest = Utils.get_diff_names_same_digests_list(self.first_digest_diff, self.second_digest_diff, self.logger, self.config)
            self.timer.display(f"done ", ".")
        else:
            # just get duplicates in first
            self.first_only_duplicates = Utils.get_duplicates_dict(self.first_files_dict, self.revidx_first_files, "first", self.logger, self.config)
            self.timer.display(f"done ", ".")

        # Get counts of buckets
        self.num_first_only_files = len(self.first_only)
        self.num_second_only_files = len(self.second_only)
        self.num_exact_match = len(self.exact_match)
        self.num_first_only_duplicates = len(self.first_only_duplicates)
        self.num_second_only_duplicates = len(self.second_only_duplicates)

        for k, v in self.diff_name_match_digest:
            for f in v:
                self.num_diff_name_match_digest += 1

        self.num_match_name_diff_digest = len(self.match_name_diff_digest) * 2

    def display_results(self):
        # Display buckets
        if not self.config.brief:
            Utils.display_duplicates_dict(self.first_only_duplicates, self.config.firstdir, self.logger, self.config)
            if not self.config.single:
                Utils.display_duplicates_dict(self.second_only_duplicates, self.config.seconddir, self.logger, self.config)
                Utils.display_dictionary(self.exact_match, "Exact matches", self.num_exact_match, self.logger, self.config, "kv", "vk")
                Utils.display_dictionary(self.first_only, f"Only in {self.config.firstdir}",
                                           self.num_first_only_files, self.logger, self.config,"kv", "vk")
                Utils.display_dictionary(self.second_only, f"Only in {self.config.seconddir}",
                                           self.num_second_only_files, self.logger, self.config, "kv", "vk")

                self.logger.info(f"Same names but different digests: {self.num_match_name_diff_digest} files found.")
                for f in sorted(self.match_name_diff_digest):
                    self.logger.info(f"{f[0]} first:{f[1]}")
                    self.logger.info(f"{f[0]} second:{f[2]}")
                

                self.logger.info(f"Different names but same digests: {self.num_diff_name_match_digest} files found.")
                for e in sorted(self.diff_name_match_digest):
                    # self.logger.info(f"{f[0]} {f[1]}")
                    # self.logger.info(f"{f[0]} {f[2]}")
                    for f in e[1]:
                        self.logger.info(f"{e[0]} {f}")
                

        # Display Summary
        if not (self.config.brief or self.config.compact):
            self.logger.info("Summary")
        if not self.config.compact:
            self.logger.info(f"Started at {self.start_date}")
        totalfiles = self.num_first_files + self.num_second_files
        totaldirs = self.num_first_dirs + self.num_second_dirs
        if self.config.single:
            self.logger.info(f"{totaldirs + 1} dirs, {totalfiles} files analyzed including {self.config.firstdir}.")
        else:
            self.logger.info(
                f"{totaldirs + 2} dirs, {totalfiles} files analyzed including {self.config.firstdir} and {self.config.seconddir}.")
        self.logger.info(f"{self.num_first_dirs} dirs, {self.num_first_files} files found in {self.config.firstdir}.")
        if not self.config.single:
            self.logger.info(f"{self.num_second_dirs} dirs, {self.num_second_files} files found in {self.config.seconddir}.")
            self.logger.info(f"{self.num_first_only_duplicates} duplicate files found in {self.config.firstdir}.")
            self.logger.info(f"{self.num_second_only_duplicates} duplicate files found in {self.config.seconddir}.")
            self.logger.info(f"{self.num_exact_match} exact matches found.")
            self.logger.info(f"{self.num_first_only_files} files only exist in {self.config.firstdir}.")
            self.logger.info(f"{self.num_second_only_files} files only exist in {self.config.seconddir}.")
            self.logger.info(f"{self.num_match_name_diff_digest} files have same names but different digests.")
            self.logger.info(f"{self.num_diff_name_match_digest} files have different names but same digest.")
        else:
            self.logger.info(f"{self.num_first_only_duplicates} duplicate files found in {self.config.firstdir}.")

        final = time.time()

        totaltime = round(final - self.start_time, 2)
        if not self.config.compact:
            outstr = "Finished at "
            outstr += datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.logger.info(outstr)
        if not (self.config.brief or self.config.compact):
            
            self.logger.info(f"Total running time: {totaltime}s.")