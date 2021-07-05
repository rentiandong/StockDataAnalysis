import logging
import datetime
import os
import sys

log_folder_name = 'logs'
if not os.path.exists(log_folder_name):
    os.mkdir(log_folder_name)

log_file_name = os.path.join(log_folder_name, '{}.log'.format(datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')))
if not os.path.exists(log_file_name):
    with open(log_file_name, 'w'):
        pass

# set up root logger, as other loggers automatically inherit from it
# https://stackoverflow.com/questions/47422689/python-logging-how-to-inherit-root-logger-level-handler
LOG_FORMATTER = logging.Formatter('%(asctime)s %(name)s: %(message)s')

root_logger = logging.getLogger()
file_handler = logging.FileHandler(log_file_name)
file_handler.setFormatter(LOG_FORMATTER)
root_logger.addHandler(file_handler)


class Logger:
    def __init__(self, logger_name: str, print_to_console: bool = True):
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

        if print_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(LOG_FORMATTER)
            self._logger.addHandler(console_handler)

    def log_debug(self, message: str) -> None:
        self._logger.debug(message)

    def log_info(self, message: str) -> None:
        self._logger.info(message)

    def log_warning(self, message: str) -> None:
        self._logger.warning(message)

    def log_error(self, message: str) -> None:
        self._logger.error(message)

    def log_critical(self, message: str) -> None:
        self._logger.critical(message)
