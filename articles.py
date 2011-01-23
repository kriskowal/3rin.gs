# -*- coding: UTF-8 -*-

from regions import regions2 as get_regions
from names import names as get_names
from labels import labels_dict as get_labels
from links import links as get_links
from locations import locations as get_locations
from utils import makedirs
from pprint import pprint
regions = get_regions()
names = get_names()
labels = get_labels()
links = get_links()
locations = dict(get_locations())

# sindarin normalizations (X/* references)
# http://www.jrrvf.com/cgi-bin/hisweloke/sindnorm.cgi

# &#8275; - swung dash
# "; " terms
# " > ", " < ", " - " parts
# definition ", " notes
# " / "
# " "

def linguistic_details_html(details):
    return "".join(
        "<li>%s</li>" % definition_html(detail)
        for detail in details.split("; ")
    )

def definition_html(definition):
    return ", ".join(term_html(term) for term in definition.split(", "))

def term_html(term):
    return " &#47; ".join(
        " &ndash; ".join(
            " &ndash; ".join(
                " &rarr; ".join(
                    " &larr; ".join(
                        "&#8275;".join(
                            words_html(words)
                            for words in tilde.split("~")
                        ) for tilde in rarr.split(" < ")
                    ) for rarr in ndash.split(" > ")
                ) for ndash in mdash.split(" - ")
            ) for mdash in solidus.split(" -- ")
        ) for solidus in term.split(" / ")
    )

def words_html(words):
    return " ".join(
        word_html(word)
        for word in
        words.split(" ")
    )

def word_html(word):
    if word.startswith("http://"):
        return '<a href="%s" target="_blank">&dagger;</a>' % word
    if word in LANGUAGE_ABBRS:
        return language_abbr_html(word)
    return word

LANGUAGE_ABBRS = {
    "E": "English",
    "S": "Sindarin",
    "Q": "Quenya",
    "Ñ": "Ñoldorin",
    "W": "Westron",
    "R": "Rohirric",
}
LANGUAGE_ABBRS_NORMAL = {
    "N": "Ñ",
}

def language_abbr_html(language):
    language = LANGUAGE_ABBRS_NORMAL.get(language, language)
    return """<em><abbr title="%s">%s</abbr></em>""" % (
        LANGUAGE_ABBRS.get(language, language),
        language
    )

LABEL = '''<p><img src="%(image_url)s" title="&#8216;%(name)s&#8217; in %(language)s with %(letters)s letters"></p>'''

LANGUAGE = """<p><em><strong>%s:</strong></em> %s%s %s</p> %s"""

def language_html(language):
    return LANGUAGE % (
        language["Language"],
        (
            """<abbr tilte="not attested, constructed by %s.">*</abbr>"""
                % language["Constructed"]
            if "Constructed" in language else ""
        ),
        language["Name"],
        (
            "<em>(%s)</em>" % language["English Meaning"]
            if
                language["English Meaning"] and
                not language["Construction"] and
                not any(
                    language["English Meaning"].lower() == other["Name"].lower()
                    for other in names[language["Canonical"]]
                )
            else ""
        ),
        (
            (
                "<ul>%s%s</ul>" % (
                    linguistic_details_html(language["Construction"]),
                    (
                        "<ul><small><em>&mdash; %s</em></small></ul>" %
                        language["Constructed"]
                        if language["Constructed"]
                        else ""
                    )
                )
            )
            if language["Construction"]
            else ""
        ),
    )

SOURCE = u'''<p><strong><a href="%(href)s" target="_blank">%(name)s</a></strong>%(description)s <nobr>&ndash; <em>%(source)s</em></nobr></p>'''
TEMPLATE = open('template.html').read().decode("utf-8")
EMBEDDED = u'''%s <p><a href="/articles/%s.html" target="_blank">comments</a></p>'''
makedirs("build/articles")
index = []
for canonical, region in regions.items():
    parts = []
    print canonical

    location = locations[canonical]
    if 'Notes' in location and location['Notes']:
        parts.append('<p>%s</p>' % location['Notes'])

    for letters in 'Tengwar',:
        for language in 'Sindarin', 'English', 'Quenya', 'Khuzdul':
            mode = 'General Use'
            label_key = canonical, language, letters, mode
            if label_key in labels:
                parts.append(LABEL % {
                    "image_url": "http://3rin.gs/labels/%s-%s.png" % labels[label_key].parts,
                    "name": canonical.replace("-", " "),
                    "language": language,
                    "letters": letters
                })

    map_href = "http://3rin.gs/#%s" % ",".join("%s" % val for val in [
        region.height,
        region.width,
        region.y,
        region.x,
        'l',
        canonical,
    ])
    etym = names[canonical]
    for et in etym:
        parts.append(language_html(et))
        index.append({
            "name": et['Name'],
            "article": "%s.html" % canonical,
            "map": map_href,
        })

    articles = links.get(canonical, [])
    for article in articles:
        parts.append(SOURCE % {
            'name': article.name,
            'href': article.href,
            'description': ", %s" % article.description if article.description else '',
            'source': article.source,
        })

    body = u"\n".join(parts)
    file = open("build/articles/%s.frag.html" % canonical, "w")
    file.write((EMBEDDED % (body, canonical)).encode("utf-8"))
    file = open("build/articles/%s.html" % canonical, "w")
    file.write((TEMPLATE % {
        "title": canonical,
        "id": canonical,
        "body": """
            <p style="float: right"><a href="%(map_href)s">MAP</a></p>
            %(body)s
        """ % {
            "body": body,
            "map_href": map_href,
        }
    }).encode("utf-8"))

open("build/articles/index.html", "w").write((TEMPLATE % {
    "title": "Locations of Middle-earth",
    "id": "index",
    "body": """
        <h1>Locations of Middle-earth</h1>
        <ol>%s</ol>
    """ % "".join(
        """<li>%(name)s <a href="%(map)s">map</a> <a href="%(article)s">info</a></li>\n""" % entry
        for entry in sorted(index, key=lambda entry: entry['name'])
    ),
}).encode("utf-8"))


