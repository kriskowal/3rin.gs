
import tsv
import codecs
FILE = 'books.tsv'

def books():
    def item(row):
        name = row["Abbreviation"]
        return name, row
    return dict(map(item, tsv.DictReader(codecs.open(FILE, 'r', 'utf-8'))))

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

