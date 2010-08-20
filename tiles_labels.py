
from levels import LEVELS
from tiles import walk, TILE_WIDTH, TILE_HEIGHT
from over import over
from fade import fade
from darken import darken
import Image

def command(source, target):
    for quadkey in walk():
        file_name = "%s%s.png" % (target, quadkey)
        print file_name
        scale = len(quadkey)
        levels = LEVELS[scale]
        image = Image.new("RGBA", (TILE_WIDTH, TILE_HEIGHT), (255, 255, 255, 0))
        for level, factor in levels:
            export = Image.open("%s/%d-%s.png" % (source, level, quadkey))
            faded = fade(export, factor)
            dark = darken(faded, .5)
            image = over(dark, image)
        image.save(file_name)

def main():
    import sys
    command(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()

