# decuser_python_playground
A repository for python scripts of interest

# News
20241221 I am in the process of refactoring the program in anticipation of adding a GUI (tkinter). Before I start on the GUI transition, I am modularizing, formalizing the configuration, adding logging (with all output being through the logger, vastly improving the progress tracking, adding explanatory comments, and generally making the code better. A lot of this is complete, but in testing. Once it's tested, I will merge it into master and it will become the next version, may as well call it version 1 at that point. The GUI version will most definitely be version 2. If you want to see the new code, as I work on it (I commit when I think it's working, but occasionally, it's got bugs), it's the pre-gui branch.

# Version History
* 20241220 v0.7.5 - Refactored globals, config, and logging
* 20241217 v0.7.4 - Refactor prior to GUI integration
* 20210804 v0.7.3 - Added compact output
* 20210804 v0.7.2 - Bugfix: Issue with directories added to filelist
* 20210804 v0.7.1 - Bugfix: -b -s flags not working
* 20210802 v0.7.0 - Added single directory support and fixed counting
* 20200620 v0.6.2 - Added version argument
* 20191218 v0.6.1 - Bugfixes: Empty source dir and hidden files issue
* 20191218 v0.6.0 - Refactored, embraced global data structures
* 20191216 v0.5.1 - Added fast digest support
* 20191212 v0.5.0 - Added recursion, hidden file support, and version scheme change
* 20191210 v0.4.0 - Refactor, comments, added same name diff digest
* 20191210 v0.3.0 - Added argparse functionality and brief mode
* 20191210 v0.2.0 - Added duplicate checking in src and dst
* 20191210 v0.1.0 - Initial working version

# First up - dircmp.py, a *nix utility to compare two directories
What it does is:

* Calculate sha1 checksums for all non-hidden files in a src and dst directory
* Supports recursion
* Supports hidden directories and files
* Supports fast digests (not terribly accurate, but sufficient for quick scanning)
* Supports single directory analysis
* Gets a list and count of files that:
  * Only exist in src
  * Only exist in dst
  * Exist in both
  * Are duplicates in src
  * Are duplicates in dst
  * Have the same name in both, but different checksums
  * Have the same checksums, but different names

## Systems Tested
* Tuxedo OS 202412 with Python 3.9.21
* Linux Mint 22 with Python 3.9.21
* Mac OS X 10.16.7 with Python 3.9.21
* Mac OS X 10.14.6 with Python 3.9.4
* 10.15.1 Catalina with Python 3.7.3
* Linux Mint 19.2 Tina with Python 3.7.5

## Notes
I was tired of trying to understand other compare utilities that didn't seem to do quite what I wanted them to. This utility lets me see exactly what the state of the two directories are relative to each other. I use it to detect duplicates and to bring to directory trees into synchronization.

The utility isn't optimized, but it's good for most work. One of these days, I'll have to do some optimization. That said, it's very accurate. 

## Test Run
```
git clone https://github.com/decuser/decuser_python_playground.git
cd decuser_python_playground
git branch -v -a
git switch pre-gui
cd dircmp
python dircmp.py tests/src tests/dst
2024-12-21 22:52:43,414 - dircmp - INFO - Started at 2024-12-21 22:52:43.414957
2024-12-21 22:52:43,415 - dircmp - INFO - +----------------------------------+
2024-12-21 22:52:43,415 - dircmp - INFO - | Welcome to dircmp version 0.7.5  |
2024-12-21 22:52:43,415 - dircmp - INFO - | Created by Will Senn on 20191210 |
2024-12-21 22:52:43,415 - dircmp - INFO - | Last updated 20241220            |
2024-12-21 22:52:43,415 - dircmp - INFO - +----------------------------------+
2024-12-21 22:52:43,415 - dircmp - INFO - Arguments:tests/src tests/dst
2024-12-21 22:52:43,415 - dircmp - INFO - Digest: sha1
2024-12-21 22:52:43,415 - dircmp - INFO - Source (first): tests/src/
2024-12-21 22:52:43,415 - dircmp - INFO - Destination (second): tests/dst/
2024-12-21 22:52:43,415 - dircmp - INFO - Compact mode: False
2024-12-21 22:52:43,415 - dircmp - INFO - Single directory mode: False
2024-12-21 22:52:43,415 - dircmp - INFO - Show all files: False
2024-12-21 22:52:43,415 - dircmp - INFO - Recurse subdirectories: False
2024-12-21 22:52:43,415 - dircmp - INFO - Calculate shallow digests: False
2024-12-21 22:52:43,415 - dircmp - INFO - Scanning first ...
2024-12-21 22:52:43,415 - dircmp - INFO -  9 files found (0.0s)
2024-12-21 22:52:43,415 - dircmp - INFO - Calculating sha1 digests in first
2024-12-21 22:52:43,416 - dircmp - INFO - Processed 135.0 Byte for digest (135.0 Byte of files), 0.0 Byte remaining (9/9 files processed).
2024-12-21 22:52:43,416 - dircmp - INFO -  done (0.0s)
2024-12-21 22:52:43,416 - dircmp - INFO - Scanning second ...
2024-12-21 22:52:43,416 - dircmp - INFO -  7 files found (0.0s)
2024-12-21 22:52:43,416 - dircmp - INFO - Calculating sha1 digests in second
2024-12-21 22:52:43,416 - dircmp - INFO - Processed 130.0 Byte for digest (130.0 Byte of files), 0.0 Byte remaining (7/7 files processed).
2024-12-21 22:52:43,416 - dircmp - INFO -  done (0.0s)
2024-12-21 22:52:43,416 - dircmp - INFO - Analyzing first directory ...
2024-12-21 22:52:43,417 - dircmp - INFO - done (0.0s)
2024-12-21 22:52:43,417 - dircmp - INFO - Analyzing second directory ...
2024-12-21 22:52:43,417 - dircmp - INFO - done (0.0s)
2024-12-21 22:52:43,417 - dircmp - INFO - Comparing first to second ...
2024-12-21 22:52:43,417 - dircmp - INFO - done (0.0s)
2024-12-21 22:52:43,417 - dircmp - INFO - Comparing second to first ...
2024-12-21 22:52:43,417 - dircmp - INFO - done (0.0s)
2024-12-21 22:52:43,417 - dircmp - INFO - Checking for different names, same digest ...
2024-12-21 22:52:43,417 - dircmp - INFO - done (0.0s).
2024-12-21 22:52:43,417 - dircmp - INFO - Duplicates found in tests/src/: 6 files found.
2024-12-21 22:52:43,417 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both
2024-12-21 22:52:43,417 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both_copy
2024-12-21 22:52:43,417 - dircmp - INFO - c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src
2024-12-21 22:52:43,417 - dircmp - INFO - c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src_copy
2024-12-21 22:52:43,417 - dircmp - INFO - da39a3ee5e6b4b0d3255bfef95601890afd80709 empty
2024-12-21 22:52:43,417 - dircmp - INFO - da39a3ee5e6b4b0d3255bfef95601890afd80709 empty_in_both
2024-12-21 22:52:43,417 - dircmp - INFO - Duplicates found in tests/dst/: 2 files found.
2024-12-21 22:52:43,417 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both
2024-12-21 22:52:43,417 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both_copy
2024-12-21 22:52:43,417 - dircmp - INFO - Exact matches: 4 files found.
2024-12-21 22:52:43,417 - dircmp - INFO - 75093aa729169179c9dbbca6aa2d95a97865ca03 b_same_in_both
2024-12-21 22:52:43,417 - dircmp - INFO - da39a3ee5e6b4b0d3255bfef95601890afd80709 empty_in_both
2024-12-21 22:52:43,417 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both
2024-12-21 22:52:43,417 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both_copy
2024-12-21 22:52:43,417 - dircmp - INFO - Only in tests/src/: 2 files found.
2024-12-21 22:52:43,417 - dircmp - INFO - c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src
2024-12-21 22:52:43,418 - dircmp - INFO - c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src_copy
2024-12-21 22:52:43,418 - dircmp - INFO - Only in tests/dst/: 1 files found.
2024-12-21 22:52:43,418 - dircmp - INFO - 36969b074153d1e76fbd43fb3d3c59802b5f730d only_in_dst
2024-12-21 22:52:43,418 - dircmp - INFO - Same names but different digests: 2 files found.
2024-12-21 22:52:43,418 - dircmp - INFO - in_both_diff_content first:e3bbf99ae9bb23804155b25a82a943e8757fc07a
2024-12-21 22:52:43,418 - dircmp - INFO - in_both_diff_content second:2690814b054f2ddf3435a30a65506ce4bedba1d2
2024-12-21 22:52:43,418 - dircmp - INFO - Different names but same digests: 8 files found.
2024-12-21 22:52:43,418 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed second:same_in_both_copy
2024-12-21 22:52:43,418 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed second:same_in_both
2024-12-21 22:52:43,418 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed first:same_in_both_copy
2024-12-21 22:52:43,418 - dircmp - INFO - 0026a27ffa78a4a4963175c35fbee11c332049ed first:same_in_both
2024-12-21 22:52:43,418 - dircmp - INFO - 6476df3aac780622368173fe6e768a2edc3932c8 second:in_dst_same_content_diff_name
2024-12-21 22:52:43,418 - dircmp - INFO - 6476df3aac780622368173fe6e768a2edc3932c8 first:in_src_same_content_diff_name
2024-12-21 22:52:43,418 - dircmp - INFO - da39a3ee5e6b4b0d3255bfef95601890afd80709 second:empty_in_both
2024-12-21 22:52:43,418 - dircmp - INFO - da39a3ee5e6b4b0d3255bfef95601890afd80709 first:empty
2024-12-21 22:52:43,418 - dircmp - INFO - Summary
2024-12-21 22:52:43,418 - dircmp - INFO - Started at 2024-12-21 22:52:43.415547
2024-12-21 22:52:43,418 - dircmp - INFO - 4 dirs, 16 files analyzed including tests/src/ and tests/dst/.
2024-12-21 22:52:43,418 - dircmp - INFO - 0 dirs, 9 files found in tests/src/.
2024-12-21 22:52:43,418 - dircmp - INFO - 2 dirs, 7 files found in tests/dst/.
2024-12-21 22:52:43,418 - dircmp - INFO - 6 duplicate files found in tests/src/.
2024-12-21 22:52:43,418 - dircmp - INFO - 2 duplicate files found in tests/dst/.
2024-12-21 22:52:43,418 - dircmp - INFO - 4 exact matches found.
2024-12-21 22:52:43,418 - dircmp - INFO - 2 files only exist in tests/src/.
2024-12-21 22:52:43,418 - dircmp - INFO - 1 files only exist in tests/dst/.
2024-12-21 22:52:43,418 - dircmp - INFO - 2 files have same names but different digests.
2024-12-21 22:52:43,418 - dircmp - INFO - 8 files have different names but same digest.
2024-12-21 22:52:43,418 - dircmp - INFO - Finished at 2024-12-21 22:52:43.418874
2024-12-21 22:52:43,418 - dircmp - INFO - Total running time: 0.0s.
2024-12-21 22:52:43,418 - dircmp - INFO - Finished at 2024-12-21 22:52:43.418949
```
## Known Issues

* the comparison effectively ignores empty directories - git ignores them too and this 
	makes git hosted tests problematic for this sorta thing

## Quirks

* 20210803 "Only in" refers to file content, not filename, so a filename might exist in only one of the trees being compared, but if its contents match a file in the other tree, it will not be listed in "Only in". It will be noted in "Different names but same digests"

For example: In src, there's a file named only_in_src that contains the letter 'a'. In dst, there's a file named only_in_dst that contains the letter 'a'. The comparison would show 0 files Only in src, 0 files Only in dst and 2 files Different names but same digests. To be clear, the program privileges content over names. An enhancement would be to support Names only in and Content only in...
