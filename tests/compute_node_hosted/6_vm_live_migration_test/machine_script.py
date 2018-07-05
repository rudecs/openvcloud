#!/usr/bin/env/python
import sys
import os

testname = sys.argv[1]
os.system('fio --ioengine=libaio --direct=1 --gtod_reduce=1 --name=%s --size=1G --readwrite=randrw'%(testname))




