import os
import sys
import datetime

from loguru import logger

#  ********** LOGGER CONFIG ********************************
PATH = os.getcwd()
if not os.path.exists('./logs'):
    os.mkdir("./logs")
today = datetime.datetime.today().strftime("%Y-%m-%d")
file_path = os.path.join(os.path.relpath(PATH, start=None), 'logs', today, 'secondary_server.log')
logger.remove()
LOG_LEVEL: str = "WARNING"
DEBUG_LEVEL: str = "INFO"
logger.add(sink=file_path, enqueue=True, level=LOG_LEVEL, rotation="50 MB")
logger.add(sink=sys.stdout, level=DEBUG_LEVEL)
logger.configure(
    levels=[
        dict(name="DEBUG", color="<white>"),
        dict(name="INFO", color="<fg #afffff>"),
        dict(name="WARNING", color="<light-yellow>"),
        dict(name="ERROR", color="<red>"),
    ]
)
logger.info(f'Start logging to: {file_path}')
#  ********** END OF LOGGER CONFIG *************************
