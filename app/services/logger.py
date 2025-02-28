import logging
from termcolor import colored


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_message = super().format(record)
        if record.levelname == "ERROR":
            log_message = colored(log_message, "red")
        return log_message


# def log_with_color(message, level):
#     if level == "ERROR":
#         return colored(message, "red")
#     return message

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)

logger = logging.getLogger(__name__)
logger.addHandler(console_handler)
