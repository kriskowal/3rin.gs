
import darken
from tiles import walk

def command(source, target, factor):
    for quadkey in walk():
        print quadkey
        darken.command(
            source + "-" + quadkey + ".png",
            target + "-" + quadkey + ".png",
            factor
        )

def main():
    import sys
    command(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()

