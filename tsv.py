
from StringIO import StringIO
from itertools import chain, cycle
import codecs

def read_cell(i, text):
    r"""
        >>> read_cell(0, '''a''')
        (1, 'a')
        >>> read_cell(0, '''a\t''')
        (1, 'a')
        >>> read_cell(0, '''a\tb''')
        (1, 'a')
        >>> read_cell(0, '''a\n''')
        (1, 'a')
        >>> read_cell(0, '''a\nb\n''')
        (1, 'a')
        >>> read_cell(0, '''"a"''')
        (3, 'a')
        >>> read_cell(0, '''"a"\t''')
        (3, 'a')
        >>> read_cell(0, '''"a"\n''')
        (3, 'a')
        >>> read_cell(0, '''"("")"''')
        (6, '(")')
        >>> read_cell(0, '''"\n"''')
        (3, '\n')
        >>> read_cell(0, '''"(""-"")"''')
        (9, '("-")')
        >>> read_cell(0, '''"(\n""\n)"''')
        (8, '(\n"\n)')
        >>> read_cell(0, '''"9,10"''')
        (6, '9,10')
    """
    if len(text) <= i:
        return [i, ""]
    elif text[i] == '"':
        cell = ""
        j = i + 1
        while True:
            q = text[j:].find('"')
            next = j + q + 1
            if len(text) > next and text[next] == '"':
                cell = cell + text[j:next]
                j = next + 1
            else:
                cell = cell + text[j:j+q]
                j = j + q
                break
        return (j + 1, cell)
    else:
        n = text[i:].find('\n')
        t = text[i:].find('\t')
        if n == -1 and t == -1:
            end = len(text)
            return (end, text[i:end])
        elif n == -1 or t == -1:
            nt = max(n, t)
            return (i + nt, text[i:i+nt])
        elif n < t:
            return (i + n, text[i:i+n])
        else:
            return (i + t, text[i:i+t])

def read_row(i, text):
    r"""
        >>> read_row(0, "")
        (0, [''])
        >>> read_row(0, "a")
        (1, ['a'])
        >>> read_row(0, "a\tb")
        (3, ['a', 'b'])
        >>> read_row(0, '"\n"\t""\n')
        (7, ['\n', ''])
        >>> read_row(0, '\t"abc"')
        (6, ['', 'abc'])
        >>> read_row(0, '\t"9,10"')
        (7, ['', '9,10'])
    """
    row = []
    while True:
        i, cell = read_cell(i, text)
        row.append(cell)
        if i >= len(text):
            break
        elif text[i] == '\n':
            i += 1
            break
        elif text[i] == '\t':
            i += 1
        else:
            assert False, 'invalid cell separator %r' % text[i] 
    return (i, row)

def read_table(i, text):
    r"""
        >>> list(read_table(0, ""))
        [['']]
        >>> list(read_table(0, "\n"))
        [['']]
        >>> list(read_table(0, "a\nb"))
        [['a'], ['b']]
        >>> list(read_table(0, "a\nb\n"))
        [['a'], ['b']]
        >>> list(read_table(0, '"\n"\t"\n"\n'))
        [['\n', '\n']]
    """
    while True:
        i, row = read_row(i, text)
        yield row
        if i >= len(text):
            break

def reader(stream):
    if not isinstance(stream, basestring):
        stream = stream.read()
    return read_table(0, stream)

def DictReader(stream):
    r"""
        >>> list(DictReader('a\tb\n"1"\t"2"\n'))
        [{'a': '1', 'b': '2'}]
        >>> list(DictReader('a\tb\n"1"\t"2"\n3\t4\n'))
        [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
    """
    rows = reader(stream)
    headers = rows.next()
    for row in rows:
        yield dict(zip(headers, chain(row, cycle([""]))))

def format(table):
    return u"".join(
        u"%s\n" % line for line in (
            u"\t".join(
                u"%s" % cell.decode('utf-8')
                if isinstance(cell, str)
                else u"%s" % cell
                for cell in row
            )
            for row in table
        )
    )

if __name__ == '__main__':
    from doctest import testmod
    testmod()

