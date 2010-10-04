from BeautifulSoup import BeautifulSoup
import csv, sys, urlparse
from glob import glob
from re import compile as re
from pprint import pprint
from itertools import chain
import codecs

class Link(object):
    def __init__(self, canonical = None, mappable = None, mapped = None, names = None, description = None, href = None, source = None):
        if names is None: names = []
        self.canonical = canonical or ""
        self.mappable = mappable
        self.mapped = mapped
        self.names = names
        self.description = description or ""
        self.href = href or ""
        self.source = source
    def __repr__(self):
        return 'Link(%s)' % ", ".join(
            "%s=%r" % (key, value)
            for key, value in vars(self).items()
        )
    @property
    def name(self):
        return u" / ".join(self.names)

def LinkReader(file_name):
    file = codecs.open(file_name, "r", "utf-8")
    content = file.read()
    content = content.lstrip(unicode(codecs.BOM_UTF8, "utf-8"))
    rows = (
        [cell.strip('"') for cell in line.split(u"\t")]
        for line in content.split(u"\n")
        if line.strip()
    )
    headers = rows.next()
    return (
        dict(zip(headers, row))
        for row in rows
    )

def links():
    reader = LinkReader('links.tsv')
    articles = {}
    encardas = list(
        Link(
            canonical = entry['Canonical'],
            mappable = entry['Mappable'] == '1',
            mapped = entry['Mapped'] == '1',
            names = entry['Names'].split(u" / "),
            description = entry['Description'],
            href = entry['Link'],
            source = entry['Source'],
        ) for entry in reader
    )
    for encarda in encardas:
        articles.setdefault(encarda.canonical, []).append(encarda)
    return articles

def csv_row(row):
    return u",".join(
        u'''"%s"''' % cell.replace(u'"', u'""')
        for cell in row
    )

base_url = "http://www.glyphweb.com/ARDA/"
base_url_re = re(r"^http://www\.glyphweb\.com/ARDA/\w/.*")
def scrape_file(file_name):
    soup = BeautifulSoup(open(file_name).read())
    out = csv.writer(sys.stdout)
    for tag in soup.findAll('a', title=True):
        if all(isinstance(content, basestring) for content in tag.contents):
            href = tag['href']
            try:
                href = urlparse.urljoin(base_url, href)
                if base_url_re.match(href):
                    yield href, " ".join(tag.contents), tag['title'], 
            except UnicodeEncodeError:
                pass

def scrape_files():
    hrefs = {}
    for file_name in glob("build/encarda/*"):
        for href, title, description in scrape_file(file_name):
            titles, description = hrefs.setdefault(href, (set(), description))
            titles.add(title)
    return hrefs

def merge_csv_iter():
    """
    Merges locations scraped from the web with those already
    collected and annotated, producing a new encarda.csv to stdout.
    """
    already = {}
    for canonical, mappable, mapped, title, description, link in csv.reader(open('encarda.csv')):
        if any((canonical, mappable, mapped)):
            already[link] = (canonical, mappable, mapped)
    for href, (names, description) in scrape_files().items():
        canonical, mappable, mapped  = already.get(href, ('', '', ''))
        yield (canonical, mappable, mapped, " / ".join(sorted(names, key = lambda key: len(key))), description, href)

def merge_iter():
    yield u"\t".join(["Canonical","Mappable","Mapped","Name","Description","Link"])
    for row in merge_txt():
        yield u"\t".join([
            row.canonical,
            unicode("" if row.mappable is None else int(row.mappable)),
            unicode("" if row.mappable is None else int(row.mapped)),
            row.name,
            row.description,
            row.href,
        ])

def merge():
    print u"\n".join(merge_iter()).encode('utf-16')

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

