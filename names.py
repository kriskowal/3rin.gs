
import tsv
import codecs

def names():
    entires = {}
    for line in tsv.DictReader(codecs.open("names.tsv", "r", "utf-8")):
        entry = entires.setdefault(line[u"Canonical"], [])
        entry.append(dict(line))
    return entires

def names_to_canonicals():
    return dict(names_to_canonicals_iter())

def names_to_canonicals_iter():
    for canonical, _names in names().items():
        for name in _names:
            yield name["Name"], canonical

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

