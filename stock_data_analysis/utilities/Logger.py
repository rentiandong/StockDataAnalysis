import logging
import datetime
import os

log_folder_name = 'logs'
if not os.path.exists(log_folder_name):
    os.mkdir(log_folder_name)

log_file_name = os.path.join(log_folder_name, '{}.log'.format(datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')))
if not os.path.exists(log_file_name):
    with open(log_file_name, 'w'):
        pass

LOG_FORMAT = '%(asctime)s %(name)s: %(message)s'
logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=LOG_FORMAT)


class Logger:
    def __init__(self, logger_name: str):
        self._logger = logging.getLogger(logger_name)

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
