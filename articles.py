# -*- coding: UTF-8 -*-

from regions import regions as get_regions
from names import names as get_names
from labels import labels2_dict as get_labels
from utils import makedirs
from pprint import pprint
regions = get_regions()
names = get_names()
labels = get_labels()

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
    "N": "Ñoldorin",
}

def language_abbr_html(language):
    return """<em><abbr title="%s">%s.</abbr></em>""" % (
        LANGUAGE_ABBRS.get(language, language),
        language
    )

ARTICLE = '''\
%(labels)s
%(translations)s
'''

LABEL = '''<p><img src="%(image_url)s" title="&#8216;%(name)s&#8217; in %(language)s with %(letters)s letters"></p>'''

LANGUAGE = """<p class="translation"><em><strong>%s:</strong></em> %s%s %s</p> %s"""

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
            "<em>(%s)</em>" % language["Meaning"]
            if
                "Meaning" in language and
                not "Construction" in language and
                not any(
                    language["Meaning"].lower() == other["Name"].lower()
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
                        if "Constructed" in language
                        else ""
                    )
                )
            )
            if "Construction" in language
            else ""
        ),
    )

TEMPLATE = open('template.html').read().decode("utf-8")
EMBEDDED = u'''%s <p><a href="/articles/%s.html" target="_blank">comments</a></p>'''
makedirs("build/articles")
for canonical, region in regions.items():
    parts = []
    print canonical
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
    etym = names[canonical]
    for et in etym:
        parts.append(language_html(et))
    body = u"\n".join(parts)
    file = open("build/articles/%s.frag.html" % canonical, "w")
    file.write((EMBEDDED % (body, canonical)).encode("utf-8"))
    file = open("build/articles/%s.html" % canonical, "w")
    file.write((TEMPLATE % {
        "title": canonical,
        "id": canonical,
        "body": body
    }).encode("utf-8"))

