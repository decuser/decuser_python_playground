# decuser_python_playground
A repository for python scripts of interest

# First up - dircmp.py, a utility to compare to directories
This utility doesn't recurse subdirectories, but what it does do is:

* Calculate sha1 checksums for all non-hidden files in a src and dst directory
* Gets a list and count of files that:
** Only exist in src
** Only exist in dst
** Exist in both
** Are duplicates in src
** Are duplicates in dst
** Have the same name in both, but different checksums
** Have the same checksums, but different names


