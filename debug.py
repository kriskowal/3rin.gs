
# inputs:
#  locations.tsv
#  names.tsv
#  links.tsv
#  regions.svg

# place names come from:
#  the Sindarin, Quenya, Khuzdul, Rohirric, Westron, &c columns in locations.tsv
#  the Name column in names.tsv
#  the ' / ' delimited Names column of links.tsv

# canonical names come from:
#  the index columns of
#   names.tsv
#   locations.tsv
#   links.tsv
#  rect[id] in regions.svg
#  file names in archive/labels

# DEBUG

# place names that don't
#  have a row in names.tsv
#  have articles on TolkienGateway (links.tsv)
#  have articles on EncyclopediaArda (links.tsv)

# canonical names that don't
#  have a row in locations.tsv
#  have a label in latin letters
#  have a label in the tengwar
#  have a region in regions.svg

from locations import locations as get_locations, CANONICAL, SINDARIN, ROMAN, OTHER; locations = get_locations()
from regions import regions2 as get_regions; regions = get_regions()
from links import links as get_links; links = get_links()
from names import names as get_names; names = get_names()
from labels import abnormal_labels as get_abnormal_labels,\
    normalized_labels as get_normalized_labels
normalized_labels = [label for name, label in get_normalized_labels()]
abnormal_labels = [label for name, label in get_abnormal_labels()]
postpone_canonical_names = set(name.strip() for name in open('postpone.txt'))

def canonical_names():
    canonical_names = set()

    source_pairs = (
        #('location', set(zip(*locations)[0])),
        ('regions', regions.keys()),
        #('encarda', set(
        #    link.canonical
        #    for link_list in links.values()
        #    for link in link_list
        #    if link.source == 'Encyclopedia Arda'
        #    and link.mappable
        #    and link.canonical
        #)),
        #('tolkiengateway', set(
        #    link.canonical
        #    for link_list in links.values()
        #    for link in link_list
        #    if link.source == 'Tolkien Gateway'
        #    and link.mappable
        #    and link.canonical
        #)),
        #('names', names.keys()),
        ('abnormal-labels', set(
            label['prefix']
            for label in abnormal_labels
        )),
        ('normalized-labels', set(
            label['prefix']
            for label in normalized_labels
        )),
    )

    for source_name, source_canonical_names in source_pairs:
        canonical_names.update(source_canonical_names)

    canonical_names.difference_update(postpone_canonical_names)

    sources = dict()
    for canonical_name in canonical_names:
        name_sources = sources[canonical_name] = []
        for source_name, source_canonical_names in source_pairs:
            if canonical_name in source_canonical_names:
                name_sources.append(source_name)

    for source_name, source_canonical_names in source_pairs:
        print 'missing %s: %s\n' % (
            source_name,
            ", ".join(
                "%s (%s)" % (
                    canonical_name,
                    ", ".join(sources[canonical_name])
                )
                for canonical_name in 
                sorted(canonical_names.difference(source_canonical_names))
            )
        )

def place_names():
    place_names = set()
    source_pairs = (
        ('encarda', set(
            name 
            for links in links.values()
            for link in links
            if link.source == 'Encyclopedia Arda'
            for name in link.names
            if link.mappable
        )),
        ('tolkiengateway', set(
            name 
            for links in links.values()
            for link in links
            if link.source == 'Tolkien Gateway'
            for name in link.names
            if link.mappable
        )),
        ('names', set(
            name['Name']
            for names in names.values()
            for name in names
        )),
    )
    for source_name, source_place_names in source_pairs:
        place_names.update(source_place_names)
        
    sources = dict()
    for place_name in place_names:
        name_sources = sources[place_name] = []
        for source_name, source_place_names in source_pairs:
            if place_name in source_place_names:
                name_sources.append(source_name)

    for source_name, source_place_names in source_pairs:
        print 'missing %s: %s\n' % (
            source_name,
            ", ".join(
                "%s (%s)" % (
                    place_name,
                    ", ".join(sources[place_name])
                )
                for place_name in 
                sorted(place_names.difference(source_place_names))
            )
        )

def redundant_language_names():
    # this function prints error messages
    from names import language_names
    language_names(debug = True)

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

