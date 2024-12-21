#!/usr/bin/env python
#--------------------------------------------------------------------
# dircmp.py
#
# Description:
# This script compares two directory trees, listing differences in
# filenames and file contents (based on SHA-1 digests). It identifies
# files that are unique to each tree and those that have the same
# content but different names. Output can be customized for different
# use cases.
#
# Canonical source: https://github.com/decuser/decuser_python_playground.git
#
# Quirks:
# - "Only in" refers to file contents, not filenames. Files with the same
#   content in different directories but different names will be listed
#   under "Different names but same digests" instead of "Only in."
#   Example:
#   - A file `only_in_src` in the source directory (containing 'a') and
#     a file `only_in_dst` in the destination directory (also containing 'a')
#     would be listed as 2 files under "Different names but same digests",
#     not under "Only in src" or "Only in dst."
#   - Future enhancement: Support for "Names only in" and "Content only in."
#
# Changelog:
# 20241220 v0.7.5 - Refactored globals, config, and logging
# 20241217 v0.7.4 - Refactor prior to GUI integration
# 20210804 v0.7.3 - Added compact output
# 20210804 v0.7.2 - Bugfix: Issue with directories added to filelist
# 20210804 v0.7.1 - Bugfix: -b -s flags not working
# 20210802 v0.7.0 - Added single directory support and fixed counting
# 20200620 v0.6.2 - Added version argument
# 20191218 v0.6.1 - Bugfixes: Empty source dir and hidden files issue
# 20191218 v0.6.0 - Refactored, embraced global data structures
# 20191216 v0.5.1 - Added fast digest support
# 20191212 v0.5.0 - Added recursion, hidden file support, and version scheme change
# 20191210 v0.4.0 - Refactor, comments, added same name diff digest
# 20191210 v0.3.0 - Added argparse functionality and brief mode
# 20191210 v0.2.0 - Added duplicate checking in src and dst
# 20191210 v0.1.0 - Initial working version

# Wishlist:
# - Support for "Names only in" (in progress)
# - Progress indication during SHA-1 calculation (completed)
# - Shallow digest (fast version) (completed)
# - Recursive directory and hidden file support (completed)
# - Brief mode (completed)
#--------------------------------------------------------------------

import sys
from datetime import datetime

from dir_analyzer import DirAnalyzer
from utils import Utils
from app_config import ArgumentParser
from logger_config import setup_logger

def display_welcome(logger, config):
    """
    Display a banner.

    Parameters:
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.

    Returns:
        None
    """
    logger.info("+----------------------------------+")
    logger.info(f"| Welcome to dircmp version {config.__version__}  |")
    logger.info(f"| Created by Will Senn on {config.CREATED} |")
    logger.info(f"| Last updated {config.UPDATED}            |")
    logger.info("+----------------------------------+")
    Utils.display_command_line(logger)
    if not config.brief:
        if config.debug:
            logger.debug(f"** Debug: True **")
        logger.info("Digest: sha1")
        logger.info(f"Source (first): {config.firstdir}")
        if not config.single:
            logger.info(f"Destination (second): {config.seconddir}")
        logger.info(f"Compact mode: {config.compact}")
        logger.info(f"Single directory mode: {config.single}")
        logger.info(f"Show all files: {config.all}")
        logger.info(f"Recurse subdirectories: {config.recurse}")
        logger.info(f"Calculate shallow digests: {config.fast}")


def main():
    """
     The main entry point for the script. It parses command-line arguments, sets up logging,
     displays a welcome message, and triggers the directory comparison and result display.

     It initializes the `DirAnalyzer` class, performs the analysis, and logs the start and finish times.

     Returns:
         None
     """
    parser = ArgumentParser(version='0.7.4')
    try:
        config = parser.parse_arguments()
        logger = setup_logger(config.debug, "dircmp", "dircmp.log")

        logger.info("Started at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        display_welcome(logger, config)
        da = DirAnalyzer(logger, config)
        da.analyze()
        da.display_results()

        logger.info("Finished at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
