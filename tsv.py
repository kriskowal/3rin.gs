
from StringIO import StringIO
from itertools import chain, cycle

def cell(cell):
    if cell.startswith('"') and cell.endswith('"'):
        cell = cell[1:-1].replace('""', '"')
    return cell

def DictReader(text, encoding = 'utf-8'):
    if isinstance(text, basestring):
        text = StringIO(text)
    text = iter(text)
    headers = text.next().decode(encoding).rstrip(u"\r\n").split(u"\t")
    headers = map(cell, headers)
    for line in text:
        row = line.decode(encoding).rstrip(u"\n\r").split(u"\t")
        row = map(cell, row)
        yield dict(zip(headers, chain(row, cycle([""]))))

def format(table):
    return u"".join(
        u"%s\n" % line for line in (
            u"\t".join(
                u"%s" % cell.decode('utf-8')
                if isinstance(cell, str)
                else u"%s" % cell
                for cell in row
            )
            for row in table
        )
    ).encode("utf-8")

