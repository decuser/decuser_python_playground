import time

# Utility class for calculating elapsed time between events
# Typical usage is to instantiate, reset, and get elapsed time.
#
# To instantiate prior to use:
#	timer = ElapsedTime()
# To reset and establish a reference time:
#	timer.reset()
# To get the elapsed time since the reference:
#	timer.elapsed()
#
class ElapsedTime:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    last_time = time.time()

    # class method to show elapsed time
    @property
    def elapsed(self):
        elapsed = time.time() - ElapsedTime.last_time
        ElapsedTime.last_time = time.time()
        return elapsed

    # class method to logger.info elapsed time in (XXs) form
    def display(self, prefix, suffix):
        if not (self.config.brief or self.config.compact):
            e = round(self.elapsed, 2)
            self.logger.info(f"{prefix}({e}s){suffix}")

    # class method to reset time
    def reset(self):
        self.last_time = time.time()