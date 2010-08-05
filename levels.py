
"""
This document describes the relationship between various
labeling levels in labels-st.svg and how opaque they should
be at each zoom level (scale).  These data are used to compose
the scaled tiles from the level tiles, by tiles_labels.py.
"""

LEVELS = dict((
    (0, ( # at scale 0, where the whole map is 256x256px, and the quadkey is 0 long
        (1, 1), # only level 1 should be visible, and it should be completely opaque
    )),
    (1, ( # at scale 1, where the whole map is four quads, and the quadkey is 1 long
        (1, 1),
        (2, .8), # level 2 should be 80% opaque
        (3, .6),
    )),
    (2, (
        (1, 1),
        (2, 1),
        (3, .6),
        (4, .6),
    )),
    (3, (
        (1, .6),
        (2, .8),
        (3, 1),
        (4, .8),
        (5, .6),
    )),
    (4, (
        (2, .8),
        (3, .9),
        (4, 1),
        (5, .8),
        (6, .6),
    )),
    (5, (
        (3, .6),
        (4, 1),
        (5, 1),
        (6, 1),
        (7, .8),
    )),
    (6, (
        (4, .8),
        (5, 1),
        (6, 1),
        (7, 1),
        (8, 1),
    )),
    (7, (
        (5, .8),
        (6, .9),
        (7, 1),
        (8, 1),
    )),
))

