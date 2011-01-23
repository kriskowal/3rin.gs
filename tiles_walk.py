#!/usr/bin/env python
from tiles import walk
import sys
if len(sys.argv) > 1:
    scales = range(int(sys.argv[1])+1)
else:
    scales = None
for quadkey in walk(scales = scales):
    print quadkey
