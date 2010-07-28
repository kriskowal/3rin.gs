
import Image, ImageColor, ImageFont, ImageDraw

TILE_HEIGHT = 200
TILE_WIDTH = 200
SCALE = 2
DEPTH = None

def quad(crop, prefix, suffix, x, y, width, height, depth = 0):
    if DEPTH is not None and depth > DEPTH:
        return
    if width < TILE_WIDTH or height < TILE_HEIGHT:
        return
    _width, _height = width / SCALE, height / SCALE
    print prefix + suffix, x, y, width, height
    crop.resize((TILE_WIDTH, TILE_HEIGHT), Image.ANTIALIAS).save(prefix + suffix)
    for _y in range(2):
        for _x in range(2):
            _crop = crop.crop((
                _x * _width,
                _y * _height,
                _x * _width + _width,
                _y * _height + _height,
            ))
            quad(
                _crop,
                prefix + "0123"[_y * 2 + _x],
                suffix,
                x + _x * _width,
                y + _y * _height,
                _width,
                _height,
                depth + 1
            )

def seed(file_name, prefix, suffix):
    image = Image.open(file_name)
    width, height = (int(n) for n in image.size)
    quad(image, prefix, suffix, 0, 0, width, height)

seed("build/ennorath-geography-16000.png", "build/tiles/g", ".png")
#seed("build/ennorath-labels-16000.png", "build/tiles/l", ".png")

