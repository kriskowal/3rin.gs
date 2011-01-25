# -*- coding: UTF-8 -*-

from django.template import loader, Context
from os import environ as env
env["DJANGO_SETTINGS_MODULE"] = "settings"

from itertools import chain
from utils import makedirs
from pprint import pprint
import codecs
from os.path import join
from markup import markup
from re import compile as re, escape

import regions, names, labels, links, locations, books
REGIONS = regions.regions2()
NAMES = names.names()
LANGUAGES = names.languages
LANGUAGE_NAMES = names.language_names()
LINKS = links.links()
LOCATIONS = locations.locations()
BOOKS_LIST = books.books_iter()
BOOK_ABBRS = list(zip(*BOOKS_LIST)[0])
BOOKS = dict(BOOKS_LIST)

DIR = join('build', 'articles')

parts_re = re(r'[^\w\d]')


def parse_citation(citation):
    if citation.startswith("http://"):
        return {
            "link": '<a href="%s">&dagger;</a>' % (
                citation,
            )
        }
    parts = parts_re.split(citation)
    part = parts.pop(0)
    if part in BOOKS:
        trailer = citation[len(part):]
        parts = trailer.split("#")
        if len(parts) == 2:
            trailer = '%s(<abbr title="occurrences">%s</abbr>)' % tuple(parts)
        book = BOOKS[part]
        link = book["HTML"]
        book_html = part
        if book["Title"]:
            book_html = '<abbr title="%s">%s</abbr>' % (
                book["Title"],
                book_html
            )
        part_html = part.replace("&", "&amp;")
        return {
            "link": link
                .replace("<a ", '<a target="_blank" ')
                .replace(part_html, book_html) + trailer,
            "book": part
        }
    else:
        return {
            "label": citation,
        }

def citation_index(citation):
    try:
        return BOOK_ABBRS.index(citation["book"])
    except (ValueError, KeyError):
        return len(BOOK_ABBRS)

def build_region(canonical, region):

    location = LOCATIONS[canonical]
    source_names = list(NAMES[canonical])
    language_names = LANGUAGE_NAMES[canonical]
    links = LINKS.get(canonical, [])

    names = []
    def add_name(name):
        if name in source_names:
            names.append({
                "name": name["Name"],
                "credit": ", ".join(name["Constructed"].split(" / ")),
                "language": name["Language"],
                "languages": [
                    language
                    for language in ("Sindarin", "English", "German")
                    if name[language] == "*" and
                    language != name["Language"]
                ],
                "meaning": name["English Meaning"],
                "citations": sorted([
                    parse_citation(citation)
                    for citation in name["Citations"].split(", ")
                    if citation
                ], key=citation_index),
                "construction": [
                    definition_html(construct)
                    for construct in name["Construction"].split("; ")
                    if construct
                ],
                "notes": markup(name["Notes"])
            })
            source_names.pop(source_names.index(name))

    for language in LANGUAGES:
        if language in language_names:
            add_name(language_names[language])
    while source_names:
        add_name(source_names[0])

    article_href = "%s.html" % canonical

    map_href = "http://3rin.gs/#%s" % ",".join("%s" % val for val in [
        region.height,
        region.width,
        region.y,
        region.x,
        'l',
        canonical,
    ])

    name = language_names["English"]["Name"]

    location = {
        "name": name,
        "names": names,
        "links": links,
        "map_href": map_href,
        "article_href": article_href
    }

    context = Context({
        "location": location,
        "disqus": {
            "id": canonical
        }
    })

    for extension in ('frag.html', 'html'):
        template = loader.get_template('article.' + extension)
        content = template.render(context)
        file = codecs.open(
            join(DIR, "%s.%s" % (canonical, extension)),
            "w",
            "utf-8"
        )
        file.write(content)
        file.close()

    return location

def build_index(locations):
    template = loader.get_template("articles.html")
    content = template.render(Context({
        "locations": locations,
        "disqus": {
            "id": "articles"
        }
    }))
    file = codecs.open(join(DIR, "index.html"), "w", "utf-8")
    file.write(content)
    file.close()

def build():
    makedirs(DIR)
    locations = []
    for canonical, region in REGIONS.items():
        location = build_region(canonical, region)
        locations.append(location)
    build_index(sorted(
        locations,
        key = lambda location: location['name']
    ))

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

build()

