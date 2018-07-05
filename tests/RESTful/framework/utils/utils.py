import uuid, random, os
import logging
import signal,time
from testconfig import config
from testcases import *

class Utils:
    def __init__(self):
        pass
        
    def random_string(self, length=10):
        return str(uuid.uuid4()).replace('-', '')[0:length]

