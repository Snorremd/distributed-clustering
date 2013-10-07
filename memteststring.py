import gc

__author__ = 'snorre'

import time
time.sleep(5)
print "Create number list"
numbers = range(10000000) # Loads of numbers
time.sleep(5)
print "Remove reference to numbers"
del numbers # the huge string is automatically GC'd here
gc.collect()
time.sleep(10)
print "Done"