import os
import user
import platform
import logging
import logging.handlers

HOST = '172.24.12.42'

MAX_FAILS = 5
INTERVAL = 30
MAX_INTERVAL = 200
MIN_INTERVAL = 20

MAX_LOGCOUNT=50000

if platform.system() == 'Windows':
	try:
		data_dir = os.environ['APPDATA']
	except KeyError:
		data_dir = os.path.join(user.home, 'CompressorLogs')
else:
	pass
	
LOG_FILENAME = os.path.join(data_dir, 'SAMConnect.log')


logger = logging.getLogger('SAMConnect')
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000000, backupCount=5)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)-14s: %(levelname)-10s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)-14s: %(levelname)-10s %(message)s')



def debug(msg):
	logger.debug(msg)
	
def error(msg):
	logger.error(msg)
	