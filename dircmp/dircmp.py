#!/usr/bin/env python
#--------------------------------------------------------------------
#-- dircmp.py
#--
#-- canonical source located at https://github.com/decuser/decuser_python_playground.git
#--
#-- quirks
#-- 20210803 "Only in" refers to file content, not filename, so a filename
#-- might exist in only one of the trees being compared, but if its contents match a
#-- file in the other tree, it will not be listed in "Only in". It will be noted in
#-- "Different names but same digests"
#-- For example:
#-- in src, there's a file named only_in_src that contains the letter 'a'
#-- in dst, there's a file named only_in_dst that contains the letter 'a'
#-- The comparison would show 0 files Only in src, 0 files Only in dst and
#-- 2 files Different names but same digests. To be clear, the program
#-- privileges content over names. An enhancement would be to support
#-- Names only in and Content only in...
#--
#-- Changelog
#-- 20241217 0.7.4 started refactor prior to going gui
#-- 20210804 0.7.3 added compact output - good for testing and looks good, too :)
#-- 20210804 0.7.2 bugfix unlisted - issue with directories added to filelist
#-- 20210804 0.7.1 bugfix 14 -b -s not working
#-- 20210802 0.7.0 added support for single directory and fixed counting
#-- 20200620 0.6.2 added version argument
#-- 20191218 0.6.1 bugfixes 7 empty source dir div/zero, 8 hidden files included erroneously
#-- 20191218 0.6.0 refactored, embraced global data structures after back and forth
#-- 20191216 0.5.1 added fast digest support, cleaned up a little
#-- 20191212 0.5.0 added recursion and hidden file support, changed version scheme
#-- 	to support more minor update versions
#-- 20191210 0.4 refactored, added comments, added same name diff digest
#-- 20191210 0.3 Added argparse functionality and brief mode support
#-- 20191210 0.2 Added duplicate checking in src and dst individually
#-- 20191210 0.1 Initial working SW_VERSION
#--
#-- Wishlist
#-- 20210803 support names only in
#-- done 20210802 fixed counting
#-- done 20210730 added single directory analysis support
#-- done 20191216 shallow digest (fast version)
#-- done 20191216 progress indication during sha1 calc (simple version)
#-- done 20191212 wds recursion and hidden file support
#-- done 20191210 wds brief mode (suppress detailed lists)
#--------------------------------------------------------------------
import sys
from datetime import datetime

from dir_analyzer import DirAnalyzer
from utils import Utils
from app_config import ArgumentParser
from logger_config import setup_logger

# --------------------------------------------
# -- display_welcome()
# --
# -- description:
# --    display a banner
# --
# -- parameters:
# --     none
# --
# -- returns:
# --     none
# --
# --  globals referenced:
# --     __version__
# --     CREATED
# --     UPDATED
# --
# -- instance variables referenced:
# --     ARGS_dict - brief, debug, firstdir, single, seconddir, compact, all, recurse, fast
# --
# -- instance variables affected:
# --     none
# --------------------------------------------
def display_welcome(logger, config):
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
    parser = ArgumentParser(version='0.7.4')
    try:
        config = parser.parse_arguments()
        logger = setup_logger(config.debug, "dircmp", "dircmp.log")

        logger.info("Started at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        display_welcome(logger, config)
        da = DirAnalyzer(logger, config)
        da.analyze()
        print()
        da.display_results()

        logger.info("Finished at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
