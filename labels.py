
# -*- coding: UTF-8 -*-

from locations import locations as get_locations, SCALE
from glob import glob
from re import compile as re
from subprocess import Popen
from os import stat, makedirs
from os.path import isfile
import errno
import csv

normalized_labels_re = re(r'labels/(.*)\-(..)-normalized\.png')
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
    for file_name in glob("labels/*-normalized.png"):
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
    _makedirs("build/labels/")
    for prefix in prefixes:
        label = labels[prefix]
        location = locations[prefix]
        print label['prefix']
        scale = "20%" if int(location[SCALE]) > 3 else "100%"
        normalized = label["normalized"]
        thumbnail = label["thumbnail"]
        resized = label["resized"]
        if not isfile(thumbnail):
            Popen(["convert", "-scale", "6%", normalized, thumbnail]).communicate()
        if not isfile(resized):
            Popen(["convert", "-scale", scale, normalized, resized]).communicate()

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

def _makedirs(path):
    try:
        makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

if __name__ == "__main__":
    store()

