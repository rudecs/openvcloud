#!/usr/bin/env/python
import sys


file1 = sys.argv[1]
file2 = sys.argv[2]

with open(file1) as f1:
       with open(file2) as f2:
              if f1.read() == f2.read():
                 print('Two files are identical')