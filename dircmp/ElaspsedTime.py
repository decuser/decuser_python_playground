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
    def __init__(self, args):
        self.args_dict = args

    last_time = time.time()

    # class method to show elapsed time
    @property
    def elapsed(self):
        elapsed = time.time() - ElapsedTime.last_time
        ElapsedTime.last_time = time.time()
        return elapsed

    # class method to print elapsed time in (XXs) form
    def display(self, prefix, suffix):
        if not (self.args_dict['brief'] or self.args_dict['compact']):
            e = round(self.elapsed, 2)
            print(f"{prefix}({e}s){suffix}", end="")

    # class method to reset time
    def reset(self):
        self.last_time = time.time()