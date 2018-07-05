import logging
import os

# Initiate testsuite logger
logger = logging.getLogger('openvcloud_testsuite')
if not os.path.exists('logs/openvcloud_testsuite.log'):
    os.mkdir('logs')
handler = logging.FileHandler('logs/openvcloud_testsuite.log')
formatter = logging.Formatter('%(asctime)s [%(testid)s] [%(levelname)s] %(message)s',
                              '%d-%m-%Y %H:%M:%S %Z')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
