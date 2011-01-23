
from BeautifulSoup import BeautifulSoup
import urlparse
from itertools import chain
from time import sleep
from urllib2 import urlopen
from re import compile as re
from pprint import pprint
from os.path import isfile, isdir, join
from os import mkdir
import names as NAMES
import entities
import pickle as MARSHALL

url_base = "http://www.tuckborough.net/"

def known_canonical_names_to_names():
    pass

CACHE = join('build', 'tuckborough')
def tuckread(url):
    url = urlparse.urljoin(url_base, url)
    file_name = join(CACHE, urlparse.urlparse(url)[2][1:])
    if isdir(file_name):
        file_name = join(file_name, "index.html")
    if not isfile(file_name):
        if not isdir(CACHE):
            mkdir(CACHE)
        open(file_name, 'wb').write(urlopen(url, 'rb').read())
        sleep(1)
    return open(file_name).read()

SOUP_MEMO = {}
def tucksoup(url):
    url = urlparse.urljoin(url_base, url)
    file_name = join(CACHE, urlparse.urlparse(url)[2][1:])
    if file_name not in SOUP_MEMO:
        SOUP_MEMO[file_name] = BeautifulSoup(tuckread(url))
    return SOUP_MEMO[file_name]

def tuckname(url):
    url = urlparse.urljoin(url_base, url)
    name = urlparse.urlparse(url)[-1]
    soup = tucksoup(url)
    for tag in soup.findAll('a', {"name": name}):
        while tag.nextSibling:
            tag = tag.nextSibling
            contents = getattr(tag, 'contents', ())
            while not all(isinstance(content, basestring) for content in contents):
                contents = list(chain(*[
                    [content]
                    if isinstance(content, basestring)
                    else
                    content.contents
                    if hasattr(content, 'contents')
                    else
                    []
                    for content in contents
                ]))
            content = u' '.join(contents)
            if content:
                return entities.decode(content.replace("\n", " "))
    return None

def scrape():
    soup = tucksoup("http://tuckborough.net/abcindex.html")
    name_to_href = {}
    href_to_names = {}

    for tag in soup.findAll('a'):
        if tag and tag.contents and isinstance(tag.contents[0], basestring) and tag.parent and tag.parent.contents:
            href = tag['href'].replace(" ", "%20")
            name = entities.decode(tag.contents[0].replace("\n", " "))
            names = [name]
            if isinstance(tag.parent.contents[0], basestring):
                name = tag.parent.contents[0].split(" - ")[0].replace("\n", " ")
                names.insert(0, entities.decode(name))
            for name in names:
                href_to_names.setdefault(href, set()).add(name)
                name_to_href[name] = href

    # find the tuckborough article name for every link
    href_to_tuckname = {}
    for href, names in href_to_names.items():
        name = tuckname(href)
        print 'tuckname', href, name
        if name:
            href_to_tuckname[href] = name
            names.add(name)

    return name_to_href, href_to_names, href_to_tuckname

SCRAPE_MEMO = join('build', 'tuckborough.json')
def memo_scrape():
    if not isfile(SCRAPE_MEMO):
        MARSHALL.dump(scrape(), open(SCRAPE_MEMO, 'w'))
    return MARSHALL.load(open(SCRAPE_MEMO))

def analyze():
    name_to_href, href_to_names, href_to_tuckname = memo_scrape()
    # known names to cannonicals
    lookup = NAMES.names_to_canonicals()
    # discovered names to canonicals
    name_to_canonicals = {}
    href_to_canonicals = {}
    for href, names in href_to_names.items():
        # find correlations
        for name in names:
            if name in lookup:
                canonical = lookup[name]
                name_to_canonicals.setdefault(name, set()).update(names)
                href_to_canonicals.setdefault(href, set()).add(canonical)
    pprint(href_to_canonicals)

    hrefs = href_to_names.keys()
    for href, names in href_to_names.items():
        for canonical in href_to_canonicals.get(href, ()):
            name = href_to_tuckname.get(href,
                " / ".join(sorted(names, key = len))
            )
            yield canonical, '?', '?', '?', name, '', 'The Thains Book', urlparse.urljoin(url_base, href)

def dump():
    import tsv
    import codecs
    data = tsv.format(sorted(analyze()))
    codecs.open("tuckborough.tsv", "w", "utf-8").write(data)

dump()
