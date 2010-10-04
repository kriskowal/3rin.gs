
import tsv

def names():
    entires = {}
    for line in tsv.DictReader(open("names.tsv")):
        entry = entires.setdefault(line[u"Canonical"], [])
        entry.append(dict(line))
    return entires

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

