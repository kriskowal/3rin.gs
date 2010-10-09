
from BeautifulSoup import BeautifulSoup
import csv
import urlparse
from re import compile as re

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

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

