import Image
from tiles import walk, coord
from over import over
import sys
alphabet = sys.argv[1]
size = int(sys.argv[2])
height, width = [size] * 2
image = Image.new("RGBA", (width, height), "#ffffff")

#background = Image.open("www/parchment.jpg")
#for x in range(0, image.size[0], background.size[0]):
#    for y in range(0, image.size[1], background.size[1]):
#        print 'background', x, y
#        image.paste(background, (x, y))

for key in walk(scales = (6,)):
    x, y, w, h = box = coord(key, (0, 0, width, height))
    x2 = x + w
    y2 = y + h
    region = (x, y, x2, y2)
    print key, region
    base = image.crop(region)
    for file_name in (
        "build/geography-print-16384/t%s.png" % key,
        "build/labels-%s-dark-%s/t%s.png" % (alphabet, size, key),
    ):
        tile = Image.open(file_name)
        base = over(tile, base)
    image.paste(base, region)

image.save("build/print-%s-%s.png" % (alphabet, size))
