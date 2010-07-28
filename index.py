
# -*- coding: UTF-8 -*-

from regions import regions as get_regions
from names import names as get_names
from labels import labels as get_labels
regions = get_regions()
names = get_names()
labels = get_labels()

HTML = """\
<html>
    <head>
        <title>Ennorath</title>
        <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
        <style>

            body, p, td, th, li, a {
                /* http://www.awayback.com/revised-font-stack/ */
                font-family: Garamond,Baskerville,"Baskerville Old Face","Hoefler Text","Times New Roman",serif;
                font-size: 24px;
            }

            small {
                font-size: 70%%;
            }

            td {
                padding: 1em;
            }

            a {
                color: #0000aa;
            }
            a:visited {
                color: #7777aa;
            }

            img.thumbnail {
                border: solid 1px #cccccc;
                height: 200px;
                width: 200px;
            }

            img.label {
                height: 100px;
                vertical-align: middle;
            }

        </style>
    </head>
    <body>
        <table>
            %s
        </table>
    </body>
</html>
"""

REGION = """\
<tr>
    <td>
        <a href="%(href)s"><img class="thumbnail" src="%(thumbnail)s"></a></p>
    </td>
    <td valign="top">
        %(languages)s
    </td>
</tr>
"""

LANGUAGE = """\
<p><em><strong>%s:</strong></em> %s%s %s %s</p> %s
"""

def language_abbr(language):
    return """<em><abbr title="%s">%s</abbr>.</em>""" % (
        {
            "E": "English",
            "S": "Sindarin",
            "Q": "Quenya",
            "N": "Ñoldorin",
        }.get(language, language),
        language
    )

def label_html(language):
    key = language["Canonical"], language["Language"], "Tengwar", "General Use"
    if key not in labels:
        return ""
    label = labels[key]
    return """
        <img class="label" src="http://3rin.gs/labels/%s-%st-thumbnail.png" title="%s in the Tengwar">
    """ % (
        label["Canonical"],
        label["Language"][0].lower(),
        label["Canonical"]
    )

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
        label_html(language),
        (
            (
                "<ul>%s%s</ul>" % (
                    (
                        "<br>".join(
                            " &rarr; ".join(
                                " ".join(
                                    language_abbr(word)
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

def region_html(name, region):
    return REGION % {
        "href": region["url"],
        "thumbnail": "http://3rin.gs/regions/%s.png" % name,
        "languages": "".join(
            language_html(language)
            for language in names.get(name, [])
        )
    }

html = HTML % "".join(
    region_html(name, region)
    for name, region in sorted(regions.items())
)

open('index.html', 'w').write(html.encode("UTF-8"))

