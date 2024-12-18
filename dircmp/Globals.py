from Utilities import Utilities as utils

# about constants
__author__ = "Will Senn"
__version__ = "0.7.4"
CREATED = "20191210"
UPDATED = "20241217"

# Logic Constants
BLOCKSIZE = 65536
SAMPLESIZE = (1 * 1024 * 1024)
BUFFERING = -1  # 0 for no bufferning, -1 for default
SEED = (10 * 1024 * 1024)

# arguments as parsed
ARGS = utils.parse_arguments(__version__ )
