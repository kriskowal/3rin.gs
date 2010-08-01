
# -*- coding: UTF-8 -*-

import csv
from re import compile as re

SINDARIN = "Sindarin [Ñoldorin] {Unknown/Other}"
ROMAN = "English [Westron] {Rohirric}"
OTHER = "Quenya [Khuzdul]"
PREFIX = "File Prefix"
SCALE = "Scale"
TYPE = "Type"
SINDARIN_LABEL_PAGES = "S page"
ISSUES = "Outstanding Issues"
NOTES = "Location"

FILE = 'locations.csv'

def locations():
    def item(row):
        data = dict()
        parts = row[PREFIX].split('-')
        language_key = parts.pop()
        name = "-".join(parts)
        data['name'] = name
        return name, row
    return map(item, csv.DictReader(open(FILE)))

def names():
    for canonical, data in locations():
        sindarin = data[SINDARIN]
        for language in [SINDARIN, ROMAN, OTHER]:
            if data[language]:
                yield canonical, data[language], language
        
if __name__ == '__main__':
    _csv = csv.writer(open('names-0.0.csv', 'w'))
    _csv.writerow((
        'Name',
        'Language',
        'Canonical'
    ))
    for canonical, name, language in names():
        print canonical, name, language
        _csv.writerow((name, language, canonical))

