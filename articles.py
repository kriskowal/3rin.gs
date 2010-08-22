# -*- coding: UTF-8 -*-

from regions import regions as get_regions
from names import names as get_names
from labels import labels2_dict as get_labels
from utils import makedirs
from pprint import pprint
regions = get_regions()
names = get_names()
labels = get_labels()

def language_abbr_html(language):
    return """<em><abbr title="%s">%s.</abbr></em>""" % (
        {
            "E": "English",
            "S": "Sindarin",
            "Q": "Quenya",
            "N": "Ñoldorin",
        }.get(language, language),
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
        ("*" if "Constructed" in language else ""),
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
                    (
                        "<br>".join(
                            " &rarr; ".join(
                                " ".join(
                                    language_abbr_html(word)
                                    if
                                        len(word) == 1 and
                                        word.upper() == word and
                                        word.isalpha()
                                    else word
                                    for word in part.split(" ")
                                )
                                for part in term.split(" > ")
                            )
                            for term in language["Construction"].split("; ")
                        )
                    ),
                    (
                        "<ul><small><em>&mdash; %s</em></small></ul>" %
                        language["Constructed"]
                        if "Consructed" in language
                        else ""
                    )
                )
            )
            if "Construction" in language
            else ""
        ),
    )


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
    file = open("build/articles/%s.frag.html" % canonical, "w")
    file.write(u"\n".join(parts).encode("utf-8"))
    

