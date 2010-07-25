
from decimal import Decimal
import xml.dom.minidom as dom
import csv

def walk(node):
    if node.nodeType != 1:
        return

    if node.tagName == 'rect':
        x = float(node.getAttribute('x')) / 7200
        y = float(node.getAttribute('y')) / 7200
        width = float(node.getAttribute('width')) / 7200
        height = float(node.getAttribute('height')) / 7200
        id = node.getAttribute('id')
        if not id.startswith('rect'):
            yield (
                id,
                x,
                y,
                width,
                height,
                "http://3rin.gs/#" + ",".join(str(_) for _ in [height, width, y, x])
            )

    child = node.firstChild
    while child:
        for row in walk(child):
            yield row
        child = child.nextSibling

def get():
    regions_svg = dom.parse("regions.svg")
    return walk(regions_svg.documentElement)

def regions():
    return dict(
        (name, dict(
            name = name,
            x = x,
            y = y,
            width = width,
            height = height,
            url = url,
        ))
        for name, x, y, width, height, url in get()
    )

if __name__ == '__main__':
    regions_svg = dom.parse("regions.svg")
    regions_csv = csv.writer(open("regions.csv", "w"))
    for row in walk(regions_svg.documentElement, regions_csv):
        regions_csv.writerow(row)

