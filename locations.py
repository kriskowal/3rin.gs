
# -*- coding: UTF-8 -*-

import tsv
from re import compile as re

SINDARIN = u"Sindarin [Ñoldorin] {Unknown/Other}"
ROMAN = u"English [Westron] {Rohirric}"
OTHER = u"Quenya [Khuzdul]"
PREFIX = u"Canonical"
SCALE = u"Scale"
TYPE = u"Type"
SINDARIN_LABEL_PAGES = u"S page"
ISSUES = u"Outstanding Issues"
LOCATION = u"Location"
NOTES = u"Notes"

FILE = 'locations.tsv'

def locations():
    def item(row):
        data = dict()
        parts = row[PREFIX].split('-')
        language_key = parts.pop()
        name = "-".join(parts)
        data['name'] = name
        return name, row
    return map(item, tsv.DictReader(open(FILE)))

def names():
    for canonical, data in locations():
        for language in [SINDARIN, ROMAN, OTHER]:
            print data
            if data[language]:
                yield canonical, data[language], language

def names_list():
    return list(names())

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

