import hashlib
import sys
import os

file = sys.argv[1]

rx = hashlib.md5(open(file,'r').read()).hexdigest()
tx = hashlib.md5('This line is for test\n').hexdigest()

if(rx==tx):
    os.system('echo \'Verified: No errors during transmission\' >> results.txt')
else:
    os.system('echo \'Verification failed\' >> results.txt')
