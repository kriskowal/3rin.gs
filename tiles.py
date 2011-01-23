
import Image

HEIGHT = WIDTH = 32768
TILE_HEIGHT = 256
TILE_WIDTH = 256
SCALE = 2
DEPTH = None

def contains((outer_left, outer_top, outer_width, outer_height), (inner_left, inner_top)):
    """
        >>> contains((0, 0, 1, 1), (0, 0))
        True
        >>> contains((0, 0, 1, 1), (.5, .5))
        True
        >>> contains((0, 0, 1, 1), (0, .5))
        True
        >>> contains((0, 0, 1, 1), (.5, 0))
        True
        >>> contains((0, 0, 1, 1), (0, 1))
        False
        >>> contains((0, 0, 1, 1), (1, 1))
        False
        >>> contains((0, 0, 1, 1), (1, 0))
        False
        >>> contains((0, 0, 1, 1), (-1, -1))
        False
    """
    return (
        inner_left >= outer_left and
        inner_left < outer_left + outer_width and
        inner_top >= outer_top and
        inner_top < outer_top + outer_height
    )

def overlap(outer, (inner_left, inner_top, inner_width, inner_height)):
    """
        >>> overlap((0, 0, 2, 2), (0, 0, 2, 2))
        True
        >>> overlap((0, 0, 2, 2), (1, 1, 2, 2))
        True
        >>> overlap((0, 0, 2, 2), (2, 2, 2, 2))
        False
        >>> overlap((0, 0, 2, 2), (-1, -1, 2, 2))
        True
    """
    return any(contains(outer, corner) for corner in [
        (left, top)
        for left in (inner_left, inner_left + inner_width)
        for top in (inner_top, inner_top + inner_height)
    ])

def walk(
    quadkey = "",
    x = 0,
    y = 0,
    width = WIDTH,
    height = HEIGHT,
    depth = 0,
    region = None,
    scales = None,
):
    """
        >>> list(walk(region = (0, 0, 0, 0)))
        ['', '0', '00', '000', '0000', '00000', '000000', '0000000']
        >>> list(walk(region = (0, 0, 0, 0), scales = (0,)))
        ['']
        >>> list(walk(region = (-1, -1, 0, 0), scales = (0,)))
        []
        >>> list(walk(region = (WIDTH / 2, HEIGHT / 2, 0, 0), scales = (0, 1,)))
        ['', '3']
        >>> list(walk(region = (WIDTH / 2, HEIGHT / 2, 0, 0), scales = (1,)))
        ['3']
        >>> list(walk(scales = (0, 1,)))
        ['', '0', '1', '2', '3']
        >>> list(walk(scales = (1,)))
        ['0', '1', '2', '3']
    """
    if DEPTH is not None and depth > DEPTH:
        return
    if width < TILE_WIDTH or height < TILE_HEIGHT:
        return
    if region is not None:
        if not overlap((x, y, width, height), region):
            return
    _width, _height = width / SCALE, height / SCALE
    if scales is not None:
        scale = len(quadkey)
        if scale in scales:
            yield quadkey
    else:
        yield quadkey
    for _y in range(2):
        for _x in range(2):
            for tile in walk(
                quadkey + "0123"[_y * 2 + _x],
                x + _x * _width,
                y + _y * _height,
                _width,
                _height,
                depth = depth + 1,
                region = region,
                scales = scales,
            ):
                yield tile

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

def coord(key, region):
    """
        >>> coord("", (0, 0, 1, 1))
        (0, 0, 1, 1)
        >>> coord("0", (0, 0, 2, 2))
        (0, 0, 1, 1)
        >>> coord("1", (0, 0, 2, 2))
        (1, 0, 1, 1)
        >>> coord("3", (0, 0, 2, 2))
        (1, 1, 1, 1)
    """
    x, y, width, height = region
    for s in key:
        width /= 2
        height /= 2
        s = int(s)
        x += bool(s & 1) * width
        y += bool(s & 2) * height
    return (x, y, width, height)

def command(source, target):
    seed(source, target, ".png")

def main():
    import sys
    command(sys.argv[1], sys.argv[2])

def test():
    from doctest import testmod
    testmod()

if __name__ == '__main__':
    main()

