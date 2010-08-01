
"""
Constructs build/data.json, a data file used by the client side
JavaScript, ultimately deployed as www/data.json.

The file contains, presently, two poritions:

    regions: maps the canonical names of regions to their
    bounding boxes in abbreviated x,y,h,w keyed format
    with 6 digit precision for lighter transport.

    neighborhods: maps quadkeys to a short list of
    relevant canonical location names, heuristically
    determined my a weighted combination of the difference
    in area between the quad and the given region, and
    the difference in position squared.  By squaring
    the difference in position, the relevance of
    area and position should remain in proportion since
    they are both units of area, given a manually tuned
    multiplicative factor.

"""

DEPTH = 6
SCALE = 2.
SIZE = 16000
PRECISION = 7

try:
    import json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import simplejson as json
from regions import regions as get_regions

regions = sorted(
    get_regions().values(),
    key = lambda region: -min(region['height'], region['width'])
)

def quad(regions, prefix, x, y, width, height, depth = 0):
    if depth > DEPTH:
        return
    _width, _height = width / SCALE, height / SCALE
    _region = {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
    }
    _regions = sorted(
        (
            region for region in regions
            if intersect(_region, region)
        ),
        key = keyator(_region)
    )
    yield prefix, list(
        r["name"]
        for r in _regions[:5]
    )

    for _y in range(2):
        for _x in range(2):
            for r in quad(
                _regions,
                prefix + "0123"[_y * 2 + _x],
                x + _x * _width,
                y + _y * _height,
                _width,
                _height,
                depth + 1,
            ):
                yield r

def within(outer, inner):
    return (
        inner["x"] >= outer["x"] and
        inner["y"] >= outer["y"] and
        inner["x"] + inner["width"] < outer["x"] + outer["width"] and
        inner["y"] + inner["height"] < outer["y"] + outer["height"]
    )

def intersect(a, b):
    return not (
        a["x"] + a["width"] < b["x"] or
        a["y"] + a["height"] < b["y"] or
        a["x"] > b["x"] + b["width"] or
        a["y"] > b["y"] + b["height"]
    )

def center(region):
    return (
        region["x"] + region["width"] / 2.,
        region["y"] + region["height"] / 2.,
    )

def distance((ax, ay), (bx, by)):
    return ((bx - ax) ** 2 + (by - ay) ** 2) ** .5

def area(region):
    return region["width"] * region["height"]

def keyator(_region):
    _center = center(_region)
    _area = area(_region)
    def key(region):
        return (
            distance(center(region), _center) ** 2 * .75 +
            abs(area(region) - _area)
        )
    return key

neighborhoods = {}
for quadkey, neighborhood in quad(regions, "", 0, 0, 1, 1):
    if neighborhood:
        if quadkey:
            for parent in reversed(list(
                quadkey[:n]
                for n in range(len(quadkey))
            )):
                if not parent in neighborhoods:
                    continue
                if not neighborhoods[parent] == neighborhood:
                    neighborhoods[quadkey] = neighborhood
                break
        else:
            neighborhoods[quadkey] = neighborhood

json.dump({
    "regions": dict(
        (region["name"], {
            "x": "%%0.%df" % PRECISION % region["x"],
            "y": "%%0.%df" % PRECISION % region["y"],
            "h": "%%0.%df" % PRECISION % region["height"],
            "w": "%%0.%df" % PRECISION % region["width"],
        })
        for region in regions
    ),
    "neighborhoods": neighborhoods,
}, open("build/data.json", "w"))

