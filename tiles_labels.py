
from levels import LEVELS
from tiles import walk, TILE_WIDTH, TILE_HEIGHT
from over import over
from fade import fade
import Image

def command(source, target):
    for quadkey in walk():
        scale = len(quadkey)
        levels = LEVELS[scale]
        print quadkey, levels
        image = Image.new("RGBA", (TILE_WIDTH, TILE_HEIGHT), (255, 255, 255, 0))
        for level, factor in levels:
            faded = fade(
                Image.open("%s/%d-%s.png" % (source, level, quadkey)),
                factor
            )
            image = over(faded, image)
        image.save("%s%s.png" % (target, quadkey))

def main():
    import sys
    command(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()

