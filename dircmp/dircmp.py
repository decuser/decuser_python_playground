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

from DirectoryAnalyzer import DirectoryAnalyzer
from Globals import ARGS, __version__, CREATED, UPDATED
from Utilities import Utilities as utils

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
def display_welcome():
    print("\n+----------------------------------+")
    print(f"| Welcome to dircmp version {__version__}  |")
    print(f"| Created by Will Senn on {CREATED} |")
    print(f"| Last updated {UPDATED}            |")
    print("+----------------------------------+")
    utils.display_command_line()
    if not ARGS['brief']:
        if ARGS['debug']:
            print(f"** Debug: True **")
        print("Digest: sha1")
        print(f"Source (first): {ARGS['firstdir']}")
        if not ARGS['single']:
            print(f"Destination (second): {ARGS['seconddir']}")
        print(f"Compact mode: {ARGS['compact']}")
        print(f"Single directory mode: {ARGS['single']}")
        print(f"Show all files: {ARGS['all']}")
        print(f"Recurse subdirectories: {ARGS['recurse']}")
        print(f"Calculate shallow digests: {ARGS['fast']}\n")

#------------------------------------------------
#-- main program
#------------------------------------------------
display_welcome()

da = DirectoryAnalyzer()
da.analyze()
da.display_results()
