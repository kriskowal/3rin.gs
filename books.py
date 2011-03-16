
import tsv
import codecs
FILE = 'books.tsv'

def books_iter():
    def item(row):
        name = row["Abbreviation"]
        return name, row
    return map(item, tsv.DictReader(codecs.open(FILE, 'r', 'utf-8')))

def books():
    return dict(books_iter())

BOOKS_LIST = list(zip(*books_iter())[0])

def book_index(book):
    try:
        return BOOKS_LIST.index(book)
    except ValueError:
        return len(BOOKS_LIST)

def books_list():
    return BOOKS_LIST

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

