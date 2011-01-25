import htmlentitydefs
import re
def decode(s):
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
                name = hit[2:-1]
                try:
                        entnum = int(name)
                        s = s.replace(hit, unichr(entnum))
                except ValueError:
                        pass

    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&amp;"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if htmlentitydefs.name2codepoint.has_key(name):
                s = s.replace(hit, unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s

if __name__ == '__main__':
    print repr(decode(u"&amp;&#8247;"))

