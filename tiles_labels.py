
from levels import LEVELS
from tiles import walk, TILE_WIDTH, TILE_HEIGHT
from over import over
from fade import fade
import Image

for quadkey in walk():
    scale = len(quadkey)
    levels = LEVELS[scale]
    print quadkey, levels
    image = Image.new("RGBA", (TILE_WIDTH, TILE_HEIGHT), (255, 255, 255, 0))
    for level, factor in levels:
        faded = fade(
            Image.open("build/labels-dark/%d-%s.png" % (level, quadkey)),
            factor
        )
        image = over(faded, image)
    image.save("build/tiles/l%s.png" % quadkey)

