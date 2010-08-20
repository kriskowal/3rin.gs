
# -*- coding: UTF-8 -*-

import Image
from locations import locations as get_locations, SCALE
from regions import regions2 as get_regions
from glob import glob
from re import compile as re
from os import stat
from os.path import isfile
import csv
from utils import makedirs
from scale import scale_command

normalized_labels_re = re(r'archive/labels/(.*)\-(..)-normalized\.png')
abnormal_labels_re = re(r'archive/labels/(.*)\-([seku][lt]).png')
languages = {
    "s": "Sindarin",
    "e": "English",
    "k": "Khuzdul",
    "u": "Unknown",
}
alphabets = {
    "l": "Latin",
    "t": "Tengwar",
}

def normalized_labels():
    for file_name in glob("archive/labels/*-normalized.png"):
        parts = normalized_labels_re.match(file_name).groups()
        prefix, suffix = parts
        _language, _letters = suffix
        language = languages[_language]
        letters = alphabets[_letters]
        mode = "General Use" if letters == "Tengwar" else None
        mtime = stat(file_name)[9]
        yield prefix, {
            "prefix": prefix,
            "language": language,
            "letters": letters,
            "mode": mode,
            "mtime": mtime,
            "normalized": file_name,
            "thumbnail": "build/labels/%s-%s-thumbnail.png" % parts,
            "resized": "build/labels/%s-%s-resized.png" % parts,
        }

def normalized_labels_dict():
    return dict(normalized_labels())

def abnormal_labels():
    for file_name in glob("archive/labels/*-??.png"):
        match = abnormal_labels_re.match(file_name)
        if not match:
            continue
        parts = match.groups()
        normalized = "archive/labels/%s-%s-normalized.png" % parts
        if isfile(normalized):
            continue
        prefix, suffix = parts
        _language, _letters = suffix
        letters = alphabets[_letters]
        mode = "General Use" if letters == "Tengwar" else None
        mtime = stat(file_name)[9]
        language = languages[_language]
        yield prefix, {
            "prefix": prefix,
            "language": language,
            "letters": letters,
            "mode": mode,
            "mtime": mtime,
            "abnormal": file_name,
            "normalized": normalized,
            "thumbnail": "build/labels/%s-%s-thumbnail.png" % parts,
            "resized": "build/labels/%s-%s-resized.png" % parts,
        }

def abnormal_labels_dict():
    return dict(abnormal_labels())

def abnormal_labels_list():
    return sorted(abnormal_labels())

def differences():
    locations = dict((key, value) for key, value in get_locations() if key)
    labels = normalized_labels_dict()
    location_prefixes = set(locations.keys())
    label_prefixes = set(labels.keys())
    print 'missing location data:'
    for label in sorted(label_prefixes.difference(location_prefixes)):
        print '    %s' % label
    print 'missing normalized labels:'
    for label in sorted(location_prefixes.difference(label_prefixes)):
        print '    %s' % label
    
def build():
    locations = dict((key, value) for key, value in get_locations() if key)
    labels = normalized_labels_dict()
    location_prefixes = set(locations.keys())
    label_prefixes = set(labels.keys())
    prefixes = location_prefixes.intersection(label_prefixes)
    prefixes = sorted(prefixes, key = lambda prefix: -labels[prefix]['mtime'])
    makedirs("build/labels/")
    for prefix in prefixes:
        label = labels[prefix]
        location = locations[prefix]
        print label['prefix']
        scale = .2 if int(location[SCALE]) > 3 else 1
        normalized = label["normalized"]
        thumbnail = label["thumbnail"]
        resized = label["resized"]
        scale_command(normalized, thumbnail, .6)
        scale_command(normalized, resized, scale)

def store():
    locations = dict((key, value) for key, value in get_locations() if key)
    labels = normalized_labels_dict()
    location_prefixes = set(locations.keys())
    label_prefixes = set(labels.keys())
    prefixes = location_prefixes.intersection(label_prefixes)
    prefixes = sorted(prefixes, key = lambda prefix: -labels[prefix]['mtime'])
    writer = csv.writer(open('labels.csv', 'w'))
    writer.writerow((
        'Canonical',
        'Language',
        'Letters',
        'Mode',
        'Last Modified',
    ))
    for prefix in prefixes:
        writer.writerow((
            prefix,
            labels[prefix]['language'],
            labels[prefix]['letters'],
            labels[prefix]['mode'],
            labels[prefix]['mtime'],
        ))

def labels():
    return dict(
        ((label['Canonical'], label['Language'], label['Letters'], label['Mode']), label)
        for label in csv.DictReader(open('labels.csv'))
    )

class Label(object):
    @property
    def original(self):
        return 'build/labels-original/%s-%s' % self.parts
    @property
    def embedded(self):
        return 'build/labels-embedded/%s-%s' % self.parts
    @property
    def thumbnail(self):
        return 'build/labels/%s-%s.png' % self.parts

def labels2():
    pngs = set(glob("archive/labels/*.png"))
    normalized_pngs = set(glob("archive/labels/*-normalized.png"))
    abnormal_pngs = pngs.difference(normalized_pngs)
    for abnormal in sorted(abnormal_pngs):
        match = abnormal_labels_re.match(abnormal)
        if not match:
            continue
        parts = match.groups()
        canonical, (_language, _letters) = parts
        language = languages[_language]
        letters = alphabets[_letters]
        normalized = "archive/labels/%s-%s-normalized.png" % parts
        yield type("%s-%s%s" % (canonical, _language, _letters), (Label,), {
            "canonical": canonical,
            "parts": parts,
            "language": language,
            "letters": letters,
            "source": normalized if isfile(normalized) else abnormal,
            "normalized": isfile(normalized),
        })

def build2():
    regions = get_regions()
    for label in labels2():
        source = Image.open(label.source)
        region = regions[label.canonical]
        width, height = source.size
        print label.parts, source.size, region

def main():
    import sys
    from pprint import pprint
    if len(sys.argv) < 2:
        command = 'build'
    else:
        command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

