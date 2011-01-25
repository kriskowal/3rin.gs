
from re import compile as re, IGNORECASE, escape

QUOTE_RE = re(r"""(['"])((?:'\S|[^'])*)\1""")

def gen_underbars():
    while True:
        yield '<em>'
        yield '</em>'

def replace_underbars(text, next):
    at = text.find('_')
    if at < 0:
        return text
    else:
        return text[:at] + next() + replace_underbars(text[at+1:], next)

def highlighter(text, terms):
    if not terms:
        return text
    def highlight(match):
        return '<span class="highlight">%s</span>' % match.groups(0)[0]
    return re(r'(%s)' % '|'.join(escape(term) for term in terms), IGNORECASE).sub(highlight, text)

def markup(text, highlight = None):
    if highlight is None: highlight = []
    next_underbar = gen_underbars().next
    processed = ""
    while QUOTE_RE.search(text):
        match = QUOTE_RE.search(text)
        quote, enquoted = match.groups()
        left, right = {
            "'": ('&#8216;', '&#8217;'),
            '"': ('&#147;', '&#148;'),
        }[quote]
        processed = "".join((
            processed,
            replace_underbars(text[0:match.start()].replace("'", "&#8217"), next_underbar),
            left,
            replace_underbars(enquoted.replace("'", "&#8217"), next_underbar),
            right,
        ))
        text = text[match.end():]
    return highlighter(processed + replace_underbars(text, next_underbar) + (
        '</em>' if next_underbar() == '</em>' else ''
    ), highlight)

def test():
    print markup("""'Glaurung's Bane'""")
    print markup("""'i'm in' 'i'm in' "i'm in" "'i'm in'" _'i'm in'_""")
    print markup("""'Glaurung's Bane'""", ['Glaurung'])

def main():
    import sys
    from pprint import pprint
    if len(sys.argv) < 2:
        command = 'build'
    else:
        command = sys.argv[1].replace('-', '_')
    result = globals()[command](*sys.argv[2:])
    if result is not None:
        pprint(result)

if __name__ == "__main__":
    main()

