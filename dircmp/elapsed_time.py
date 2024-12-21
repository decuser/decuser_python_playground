import time

class ElapsedTime:
    """
    Utility class for calculating elapsed time between events.

    This class allows you to measure the time between specific events by resetting
    the reference time and then retrieving the elapsed time since that reference.

    Typical usage:
    - Instantiate: `timer = ElapsedTime()`
    - Reset and establish reference time: `timer.reset()`
    - Get elapsed time: `timer.elapsed()`

    Methods:
    - reset(): Resets the reference time.
    - elapsed(): Returns the elapsed time since the last reset.
    """

    def __init__(self, logger, config):
        """
        Initializes the ElapsedTime object with the provided logger and config.

        Parameters:
        logger (Logger): The logger instance used for logging output.
        config (Config): The configuration object for the operation.
        """

        self.logger = logger
        self.config = config
        self.reset()  # Ensure the timer is initialized with a starting point

    def reset(self):
        """Resets the reference time."""
        self.last_time = time.time()

    @property
    def elapsed(self):
        elapsed = time.time() - self.last_time
        self.reset()  # Reset the timer after calculating elapsed time
        return elapsed

    # class method to logger.info elapsed time in (XXs) form
    def display(self, prefix, suffix):
        if not (self.config.brief or self.config.compact):
            e = round(self.elapsed, 2)
            self.logger.info(f"{prefix}({e}s){suffix}")
