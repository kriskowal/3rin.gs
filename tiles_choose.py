
from shutil import copy
from tiles import walk

def command(target, sources):
    for quadkey in walk():
        source = sources[len(quadkey)]
        source_file = source + quadkey + ".png"
        target_file = target + quadkey + ".png"
        print target_file, source_file
        copy(source_file, target_file)

def main():
    import sys
    command(sys.argv[1], dict(
        (int(scale), input)
        for scales, input in (
            input.split(':', 1)
            for input in sys.argv[2:]
        )
        for scale in scales.split(',')
    ))

if __name__ == '__main__':
    main()

