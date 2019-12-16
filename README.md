# decuser_python_playground
A repository for python scripts of interest

# News
## 20191212.1302 dircmp.py version 0.5.0 ready with recursion, support for hidden files, and crude tests

# First up - dircmp.py, a *nix utility to compare two directories
This utility doesn't recurse subdirectories, but what it does do is:

* Calculate sha1 checksums for all non-hidden files in a src and dst directory
* Gets a list and count of files that:
  * Only exist in src
  * Only exist in dst
  * Exist in both
  * Are duplicates in src
  * Are duplicates in dst
  * Have the same name in both, but different checksums
  * Have the same checksums, but different names

## Systems Tested
* Mac OS X 10.15.1 Catalina with Python 3.7.3
* Linux Mint 19.2 Tina with Python 3.7.5

## Notes
I was tired of trying to understand other compare utilities that didn't seem to do quite what I wanted them to. I'm sure this is a bit of a hack, but it seems to work.

The utility isn't optimized, but it's ok for most work. One of these days, I'll have to do some optimization.

## Test Run
```
git clone https://github.com/decuser/decuser_python_playground.git
cd decuser_python_playground/dircmp
python dircmp.py tests/default/src tests/default/dst

	+------------------------------------+
	|   Welcome to dircmp version 0.5.0  |
	|  Created by Will Senn on 20191210  |
	|       Last updated 20191212        |
	+------------------------------------+
	Digest: sha1
	Source (src): tests/default/src/
	Destination (dst): tests/default/dst/
	Show all files: False
	Recurse subdirectories: False

	Scanning src ... 9 files found (0.0s).
	Calculating sha1 digests in src ... done (0.0s).
	Scanning dst ... 7 files found (0.0s).
	Calculating sha1 digests in dst... done (0.0s).
	Analyzing src directory ...done (0.0s).
	Analyzing dst directory ...done (0.0s).
	Comparing src to dst ...done (0.0s).
	Comparing dst to src ...done (0.0s).
	Reconciling differences ...done (0.0s).

	Duplicates found in tests/default/src/: 6 files found.
	0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both
	0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both_copy
	c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src
	c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src_copy
	da39a3ee5e6b4b0d3255bfef95601890afd80709 empty_in_both
	da39a3ee5e6b4b0d3255bfef95601890afd80709 empty

	Duplicates found in tests/default/dst/: 2 files found.
	0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both
	0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both_copy

	Exact matches: 4 files found.
	75093aa729169179c9dbbca6aa2d95a97865ca03 b_same_in_both
	da39a3ee5e6b4b0d3255bfef95601890afd80709 empty_in_both
	0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both
	0026a27ffa78a4a4963175c35fbee11c332049ed same_in_both_copy

	Only in tests/default/src/: 2 files found.
	c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src
	c62a323c301dfb0f3cc8e27609c7f507d1965b64 only_in_src_copy

	Only in tests/default/dst/: 1 files found.
	36969b074153d1e76fbd43fb3d3c59802b5f730d only_in_dst

	Same names but different digests: 2 files found.
	in_both_diff_content src:e3bbf99ae9bb23804155b25a82a943e8757fc07a
	in_both_diff_content dst:2690814b054f2ddf3435a30a65506ce4bedba1d2

	Different names but same digests: 2 files found.
	6476df3aac780622368173fe6e768a2edc3932c8 in_src_same_content_diff_name
	6476df3aac780622368173fe6e768a2edc3932c8 in_dst_same_content_diff_name

	Summary
	-------
	Started at 2019-12-12 13:07:32.001095
	16 files analyzed.
	9 files found in tests/default/src/.
	7 files found in tests/default/dst/.
	6 duplicate files found in tests/default/src/.
	2 duplicate files found in tests/default/dst/.
	4 exact matches found.
	2 files only exist in tests/default/src/.
	1 files only exist in tests/default/dst/.
	2 files have same names but different digests.
	2 files have different names but same digest.
	Finished at 2019-12-12 13:07:32.005493

	Total running time: 0.0s.

# Known Issues

* the comparison effectively ignores empty directories - git ignores them too and this makes git hosted tests problematic for this sorta thing
