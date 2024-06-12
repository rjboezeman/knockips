import logging

class ColorFormatter(logging.Formatter):
    # Define your color codes for different log levels
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m'  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        # Apply color to the levelname only
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

# Setup the logger
loglevel = logging.INFO
log = logging.getLogger('knockip')

log.setLevel(loglevel)
log.propagate = False  # prevent double logging

# Create a custom handler
handler = logging.StreamHandler()
formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

# Configure basicConfig for the root logger to ensure consistency
logging.basicConfig(level=loglevel, handlers=[handler])


# Ensure the root logger is also configured
root_log = logging.getLogger()
root_log.setLevel(loglevel)
root_log.handlers = [handler]

# Example log messages to test colors
# log.debug("This is a debug message")
# log.info("This is an info message")
# log.warning("This is a warning message")
# log.error("This is an error message")
# log.critical("This is a critical message")
