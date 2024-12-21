import argparse
from os.path import join
from utils import Utils

class AppConfig:
    def __init__(self, firstdir, seconddir=None, brief=False, compact=False, debug=False, recurse=False, fast=False, all=False, single=False):
        """
        Initializes the AppConfig object with the specified configuration options.

        Parameters:
        firstdir (str): The first directory path.
        seconddir (str, optional): The second directory path. Defaults to None.
        brief (bool, optional): Whether to enable brief mode. Defaults to False.
        compact (bool, optional): Whether to enable compact mode. Defaults to False.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
        recurse (bool, optional): Whether to enable recursion. Defaults to False.
        fast (bool, optional): Whether to enable fast mode. Defaults to False.
        all (bool, optional): Whether to include all items. Defaults to False.
        single (bool, optional): Whether to restrict to a single item. Defaults to False.
        """

        self.__author__ = "Will Senn"
        self.__version__ = "0.7.5"
        self.CREATED = "20191210"
        self.UPDATED = "20241220"

        # Logic Constants
        self.BLOCKSIZE = 65536
        self.SAMPLESIZE = (1 * 1024 * 1024)
        self.BUFFERING = -1  # 0 for no buffering, -1 for default
        self.SEED = (10 * 1024 * 1024)
        self.PROGRESS_UPDATE_INTERVAL = 1

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
        """
        Initializes the ArgumentParser with the specified version.

        Parameters:
        version (str): The version of the application or configuration.
        """
        self.version = version

    def parse_arguments(self):
        """
        Parses command-line arguments and updates the config accordingly.

        This method processes the arguments passed to the application and configures the
        configuration based on the provided options.
        """
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

        # Ensure these are valid string paths, defaulting to an empty string if None or empty.
        args.firstdir = join(args.firstdir or '', '')
        args.seconddir = join(args.seconddir or '', '')

        Utils.validate_directories([args.firstdir, args.seconddir])

        return AppConfig(**vars(args))
