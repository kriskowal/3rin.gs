
import Image, ImageDraw
from regions import regions as get_regions
from over import over
regions = get_regions()

GEOGRAPHY = Image.open("build/ennorath-geography-16000.png")
LABELS = Image.open("build/ennorath-labels-16000.png")
WIDTH, HEIGHT = (int(n) for n in LABELS.size)
T_WIDTH = 200
T_HEIGHT = 200

for name, region in regions.items():
    print name
    ax = int(region['x'] * WIDTH)
    ay = int(region['y'] * HEIGHT)
    width = int(region['width'] * WIDTH)
    height = int(region['height'] * HEIGHT)
    bx = ax + width
    by = ay + height
    if width < T_WIDTH:
        d = (T_WIDTH - width) / 2
        ax = ax - d
        bx = ax + T_WIDTH
        width = T_WIDTH
    if height < T_HEIGHT:
        d = (T_HEIGHT - height) / 2
        ay = ay - d
        by = ay + T_HEIGHT
        height = T_HEIGHT
    if width < height:
        d = (height - width) / 2
        ax = ax - d
        bx = ax + height
    if height < width:
        d = (width - height) / 2
        ay = ay - d
        by = ay + width
    assert (bx - ax) == (by - ay), (bx - ax, by - ay)

	backdrop = Image.new(
		"RGBA",
		(T_WIDTH, T_HEIGHT),
		(255, 255, 255, 0)
	)

    labels = LABELS.crop((
        ax,
        ay,
        bx,
        by
    )).resize(
        (T_WIDTH, T_HEIGHT),
        Image.ANTIALIAS,
    )

    geography = GEOGRAPHY.crop((
        ax,
        ay,
        bx,
        by
    )).resize(
        (T_WIDTH, T_HEIGHT),
        Image.ANTIALIAS,
    )

	backdrop = over(geography, backdrop)
    backdrop = over(labels, backdrop)
    backdrop.save("build/regions/%s.png" % name)

