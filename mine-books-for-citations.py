
import tsv
import codecs
from glob import glob
from os.path import join, dirname, basename
from re import escape, compile as re, IGNORECASE
DIR = join(dirname(__file__), "archive", "books")

import books as BOOKS
books = BOOKS.books()

file = codecs.open("names.tsv", "r", "utf-8")
NAMES = list(tsv.DictReader(file))

canonicals = {}
for name in NAMES:
    canonicals.setdefault(name["Name"].lower(), set()).add(name["Canonical"])

# grand regular expression for finding all names
names_expression = ur"(?<![A-Za-z])(?:%s)(?![A-Za-z])" % u"|".join(
    escape(name["Name"]).replace(ur"\ ", ur"\s+")
    for name in sorted(
        NAMES,
        key=lambda name: -len(name["Name"])
    )
    if not name["Constructed"]
)
names_re = re(names_expression)
names_insensitive_re = re(names_expression, IGNORECASE)

space_re = re(ur"\s+")

contained = dict(
    (content, abbreviation)
    for abbreviation, book in books.items()
    for content in book["Contains"].split(", ")
)
contained["LR/Index"] = "LR"

def heredity(book):
    yield book
    while book in contained:
        book = contained[book]
        yield str(book)

# (canonical, name) -> sensitive -> book:dict -> positions:set
computed = {}
for file_name in glob(join(DIR, "*.txt")):
    book = basename(file_name).replace(".txt", "")
    book = {"LR-Index": "LR/Index", "Etym": "Etym."}.get(book, book)
    books = set(heredity(book))
    text = codecs.open(file_name, "r", "latin1").read()
    length = len(text)

    for sensitive, expression in (
        (True, names_re),
        (False, names_insensitive_re),
    ):
        for match in expression.finditer(text):
            name = match.group(0)
            position = match.start()
            name = space_re.sub(" ", name)
            name_lower = name.lower()
            for canonical in canonicals[name_lower]:
                key = canonical, name_lower
                at = computed.setdefault(key, {}).setdefault(sensitive, {})
                for book in books:
                    print book, name, canonical, position
                    at.setdefault(book, set()).add(position)

for (canonical, name), sensitivity in computed.items():
    sensitive = sensitivity.get(True, {})
    insensitive = sensitivity.get(False, {})
    for book, positions in insensitive.items():
        positions.difference_update(sensitive.get(book, set()))

def citations():
    for name in NAMES:
        key = (name["Canonical"], name["Name"].lower())
        at = computed.get(key, {})
        sensitive, insensitive = (
            ", ".join(
                "%s#%d" % (book, len(positions))
                for book, positions in sorted(
                    at.get(sensitivity, {}).items(),
                    key = lambda (book, positions): BOOKS.book_index(book)
                )
                if len(positions)
            )
            for sensitivity in (True, False)
        )
        yield name["Canonical"], name["Name"], sensitive, insensitive

codecs.open("names-citations.tsv", "w", "utf-8").write(tsv.format(citations()))

