
import Image, ImageDraw
from regions import regions as get_regions
from tiles import WIDTH, HEIGHT, TILE_WIDTH, TILE_HEIGHT
regions = get_regions()
import sys

MAP = Image.open(sys.argv[1])

for name, region in regions.items():
    print name
    ax = int(region['x'] * WIDTH)
    ay = int(region['y'] * HEIGHT)
    width = int(region['width'] * WIDTH)
    height = int(region['height'] * HEIGHT)
    bx = ax + width
    by = ay + height
    if width < TILE_WIDTH:
        d = (TILE_WIDTH - width) / 2
        ax = ax - d
        bx = ax + TILE_WIDTH
        width = TILE_WIDTH
    if height < TILE_HEIGHT:
        d = (TILE_HEIGHT - height) / 2
        ay = ay - d
        by = ay + TILE_HEIGHT
        height = TILE_HEIGHT
    if width < height:
        d = (height - width) / 2
        ax = ax - d
        bx = ax + height
    if height < width:
        d = (width - height) / 2
        ay = ay - d
        by = ay + width
    assert (bx - ax) == (by - ay), (bx - ax, by - ay)

    map = MAP.crop((
        ax,
        ay,
        bx,
        by
    )).resize(
        (TILE_WIDTH, TILE_HEIGHT),
        Image.ANTIALIAS,
    )

    map.save("build/regions/%s.png" % name)

