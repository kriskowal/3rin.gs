from BeautifulSoup import BeautifulSoup, NavigableString

def scrape():
    soup = BeautifulSoup(open('tolkiengateway.frag.html').read())
    name_to_link = {}
    for li in soup.findAll('li'):
        link = li.find('a')
        if link and link['href']:
            href = link['href']
            if href.startswith('/wiki/'):

                tg_name = href[len('/wiki/'):]
                name = link.contents[0]
                names = [name]

                other_name = u" ".join(
                    part
                    for part in li.contents
                    if isinstance(part, NavigableString)
                ).strip()

                if other_name.endswith(')'):
                    parenthetical = other_name[other_name.index('(') + 1:other_name.index(')')]
                    other_name = other_name[:other_name.index('(')].strip()
                if other_name.startswith(', '):
                    other_name = other_name[2:].strip() + " " + name
                    names.append(other_name)
                else:
                    names.append(other_name)

                reference = u"http://www.tolkiengateway.net/wiki/%s" % tg_name
                names = [name]
                assert not any('&' in name for name in names)

                for name in names:
                    name_to_link[name] = reference

    return name_to_link

def inverse_reference(x_to_y):
    y_to_xs = {}
    for x, y in x_to_y.items():
        y_to_xs.setdefault(y, []).append(x)
    return y_to_xs

def cross_reference():
    from names import names as get_names
    from itertools import chain
    names = chain(*get_names().values())
    name_to_canonical = dict(
        (name['Name'], name['Canonical'])
        for name in names
    )
    scrapings = scrape()
    table = sorted(
        (
            canonical,
            ('1' if canonical else ''), # mapped
            ('1' if canonical else ''), # mapable
            " / ".join(names),
            '', # description
            'Tolkien Gateway', # source
            link
        )
        for link, names in inverse_reference(scrapings).items()
        for canonical in set(
            name_to_canonical[name]
            for name in names
            if name in name_to_canonical
        ) or ['']
    )
    return table

def cross_reference_txt():
    from tsv import format
    open('temp.tsv', 'w').write(format(cross_reference()))


def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

