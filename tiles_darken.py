
import darken
from tiles import walk
from os.path import isfile

def command(source, target, factor):
    for quadkey in walk():
        source_file = source + quadkey + ".png"
        target_file = target + quadkey + ".png"
        if not isfile(source_file):
            continue
        print source_file, target_file
        darken.command(source_file, target_file, factor)

def main():
    import sys
    command(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()

