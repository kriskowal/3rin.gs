import sys
from os import link, unlink
from os.path import samefile, isfile, getsize
from md5 import md5

def hash(file_name):
    m = md5()
    for read in open(file_name, 'rb'):
        m.update(read)
    return m.digest()

def samecontent(a, b):
    if getsize(a) != getsize(b):
        return False
    if getsize(a) > 1024 * 1024 * 8:
        return False # close enough; don't want to compare
    return open(a, 'rb').read() == open(b, 'rb').read()

hashes = {}

for line in sys.stdin:
    file_name = line.strip()
    if not isfile(file_name):
        continue
    file_hash = hash(file_name)
    if file_hash in hashes:
        if samefile(file_name, hashes[file_hash]):
            print file_name, 'same file', hashes[file_hash]
        elif samecontent(file_name, hashes[file_hash]):
            print file_name, 'same content', hashes[file_hash]
            unlink(file_name)
            link(hashes[file_hash], file_name)
    else:
        hashes[file_hash] = file_name

