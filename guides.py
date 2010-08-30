

from tiles import WIDTH, TILE_WIDTH

# as measured as the with of the 1000 mile guide on geography.svg,
# which was in turn calibrated by the red and black milage guide
# and the attested distance of 120 miles between the far downs and
# the brandywine bridge.
points_per_thousand_miles = 3230.6
# this is the height and width of the map as measured in the svg's units
map_points = 7200.
# normal units assume the full map is exactly 1 normal unit wide and tall
normal_thousand_miles = points_per_thousand_miles / map_points

miles_per_league = 3.
miles_per_kilometer = 0.621371192
normal_mile = normal_thousand_miles / 1000.
normal_league = normal_mile / miles_per_league
normal_kilometer = normal_mile / miles_per_kilometer

finest_pixels_per_mile = normal_mile * WIDTH
finest_pixels_per_league = normal_league * WIDTH
finest_pixels_per_kilometer = normal_kilometer * WIDTH

finest_miles_per_tile = TILE_WIDTH / finest_pixels_per_mile
finest_leagues_per_tile = TILE_WIDTH / finest_pixels_per_league
finest_kilometers_per_tile = TILE_WIDTH / finest_pixels_per_kilometer

# these are preferred units of miles
units = [
    10. ** (n + 1) * x / y
    for n in range(5)
    for (x, y) in [
        (1, 10),
        (1, 4),
        (1, 2),
        (3, 4),
    ]
]

#nearest_unit_for_each_scale = dict(
#    ((zoom, unit), nearest(units, unit, measure))
#    for unit, measure in (
#        ('mile', finest_pixels_per_mile),
#        ('kilometer', finest_pixels_per_kilometer),
#        ('league', finest_pixels_per_league),
#    )
#    for zoom in range(8)
#)


