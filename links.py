
from glob import glob
import codecs

class Link(object):
    def __init__(
        self,
        canonical = None,
        mappable = None,
        mapped = None,
        names = None,
        description = None,
        href = None,
        source = None
    ):
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
    links = list(
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
    for link in links:
        articles.setdefault(link.canonical, []).append(link)
    return articles

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

