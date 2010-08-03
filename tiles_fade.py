
import fade
from tiles import walk
from os.path import isfile

def command(source, target):
    for quadkey in walk():
        for factor in (.75, .5, .25):
            args = (
                "%s-%s.png" % (source, quadkey),
                "%s-%2d-%s.png" % (target, factor * 100, quadkey),
                factor
            )
            assert isfile(args[0])
            print args
            fade.command(*args)
            assert isfile(args[1])

def main():
    import sys
    command(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()

