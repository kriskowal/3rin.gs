
import over
from tiles import walk
from os.path import isfile

def command(a, b, target):
    for quadkey in walk():
        a_file = a + quadkey + ".png"
        b_file = b + quadkey + ".png"
        target_file = target + quadkey + ".png"
        print target_file
        over.command(a_file, b_file, target_file)

def main():
    import sys
    command(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()

