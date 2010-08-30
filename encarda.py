from BeautifulSoup import BeautifulSoup
import csv, sys, urlparse
from glob import glob
from re import compile as re
from pprint import pprint

class Encarda(object):
    def __init__(self, **kws):
        for key, value in kws.items():
            setattr(self, key, value)
    def __repr__(self):
        return 'Encarda(%s)' % ", ".join(
            "%s=%r" % (key, value)
            for key, value in vars(self).items()
        )
    @property
    def name(self):
        return u" / ".join(self.names)

def encarda():
    reader = csv.reader(open('encarda.csv'))
    headers = reader.next()
    articles = {}
    encardas = list(
        Encarda(
            canonical = entry['Canonical'],
            mappable = entry['Mappable'] == '1',
            mapped = entry['Mapped'] == '1',
            names = entry['Names'].decode('utf-8').split(u" / "),
            description = entry['Description'].decode('utf-8'),
            href = entry['Link'],
        ) for entry in csv.DictReader(open("encarda.csv"))
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

def merge_iter():
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

def merge():
    print "Canonical,Mappable,Mapped,Name,Description,Link"
    for row in sorted(
        merge_iter(),
        key = lambda (canonical, mappable, mapped, name, description, href):
            (mappable == "", mapped == "", canonical)
    ):
        print csv_row(row).encode('utf-8')

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

