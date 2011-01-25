
import tsv
import codecs
from glob import glob
from os.path import join, dirname, basename
from re import escape, compile as re
DIR = join(dirname(__file__), "archive", "books")

file = codecs.open("names.tsv", "r", "utf-8")
names = list(tsv.DictReader(file))

computed = {}
for file_name in glob(join(DIR, "*.txt")):
    book = basename(file_name).replace(".txt", "")
    book = {"LR-Index": "LR"}.get(book, book)
    text = codecs.open(file_name, "r", "latin1").read()
    for name in names:
        found = len(re(r'\b%s\b' % escape(name["Name"]).replace(" ", r"\s*")).findall(text))
        if found:
            print book, name["Name"], name["Canonical"], found
            computed.setdefault((name["Canonical"], name["Name"]), list()).append("%s#%d" % (book, found))

def citations():
    for name in names:
        key = (name["Canonical"], name["Name"])
        books = ", ".join(computed.get(key, []))
        yield name["Canonical"], name["Name"], books

codecs.open("names-citations.tsv", "w", "utf-8").write(tsv.format(citations()))

