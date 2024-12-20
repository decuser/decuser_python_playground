import argparse
from os.path import join
from utils import Utils

class AppConfig:
    def __init__(self, firstdir, seconddir=None, brief=False, compact=False, debug=False, recurse=False, fast=False, all=False, single=False):
        self.__author__ = "Will Senn"
        self.__version__ = "0.7.5"
        self.CREATED = "20191210"
        self.UPDATED = "20241220"

        # Logic Constants
        self.BLOCKSIZE = 65536
        self.SAMPLESIZE = (1 * 1024 * 1024)
        self.BUFFERING = -1  # 0 for no buffering, -1 for default
        self.SEED = (10 * 1024 * 1024)

        self.firstdir = firstdir
        self.seconddir = seconddir
        self.brief = brief
        self.compact = compact
        self.debug = debug
        self.recurse = recurse
        self.fast = fast
        self.all = all
        self.single = single

class ArgumentParser:
    def __init__(self, version):
        self.version = version

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Compare 2 directories using sha1 checksums.')
        parser.add_argument('firstdir', type=str, help='a source directory')
        parser.add_argument('seconddir', nargs="?", type=str, help='a destination directory')
        parser.add_argument('-b', '--brief', action='store_true', help='Brief mode')
        parser.add_argument('-c', '--compact', action='store_true', help='Compact mode')
        parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
        parser.add_argument('-r', '--recurse', action='store_true', help='Recurse subdirectories')
        parser.add_argument('-f', '--fast', action='store_true', help='Perform shallow digests')
        parser.add_argument('-a', '--all', action='store_true', help='Include hidden files')
        parser.add_argument('-s', '--single', action='store_true', help='Single directory mode')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version=self.version))

        args = parser.parse_args()
        args.firstdir = join(args.firstdir, '')
        args.seconddir = join(args.seconddir or '', '')
        Utils.validate_directories(args)

        return AppConfig(**vars(args))
