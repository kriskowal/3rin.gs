
import tsv
import codecs

languages = [
    'Sindarin',
    'Quenya',
    'Khuzdul',
    'English',
    'German',
    'French',
    'Polish',
]

def language_index(language):
    try:
        return languages.index(language)
    except ValueError:
        return len(languages)

# canonical -> sorted list of all name dicts
def names():
    entries = {}
    file = codecs.open("names.tsv", "r", "utf-8")
    for name in tsv.DictReader(file):
        entry = entries.setdefault(name[u"Canonical"], [])
        entry.append(dict(name))
    return dict(
        (canonical, list(sorted(names, key=language_index)))
        for canonical, names in entries.items()
    )

# canonical -> language -> name as known in language
def language_names(debug = False):
    entries = {}
    for canonical, _names in names().items():
        subentries = entries.setdefault(canonical, {})
        for name in _names:
            for language in languages:
                if language in name and name[language]:
                    if debug and language in subentries:
                        print 'duplicate', language, 'name for', canonical, repr(subentries[language]["Name"]), repr(name["Name"])
                    subentries[language] = name
    return entries

def language_names_debug():
    # but do not return
    language_names(debug = True)

def names_to_canonicals():
    return dict(names_to_canonicals_iter())

def names_to_canonicals_iter():
    for canonical, _names in names().items():
        for name in _names:
            yield name["Name"], canonical

def main():
    import sys
    from pprint import pprint
    command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

