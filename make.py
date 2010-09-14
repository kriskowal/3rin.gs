
from subprocess import Popen, PIPE
from utils import makedirs
import sys

INDENT = ""

class CommandException(Exception):
    pass

def build():
    tasks = {}

    try:
        made = set(line.strip() for line in open('made'))
    except IOError:
        made = set()

    def make(name, depth = 0, made = made):
        if made is None:
            made = set()
        def _make(name):

            make(name, depth + 1, made = made)

        def _directory(path):
            print '%smkdir -p %s' % (
                INDENT * (depth + 1),
                path,
            )
            makedirs(path)

        _make.directory = _directory
        def _command(args, output = None):
            if isinstance(args, basestring):
                args = 'bash', '-c', args
            args = ["%s" % arg for arg in args]
            print '%s%s' % (
                INDENT * (depth + 1),
                " ".join(args),
            )
            if output is not None:
                output = open(output, 'w')
            process = Popen(args, stdout = output)
            process.communicate()
            if process.returncode != 0:
                raise CommandException("Process exited with %d returncode" % process.returncode)
        _make.command = _command
        def _depends(path):
            print '%s# depends: %s' % (
                INDENT * (depth + 1),
                path,
            )

        _make.depends = _depends
        print "%s# %s:" % (
            INDENT * (depth),
            name,
        )

        if name in made:
            print "%s# already made %s" % (
                INDENT * (depth + 1),
                name,
            )
            return

        tasks[name](_make, name)

        made.add(name)
        made_file = open('made', 'a')
        made_file.write("%s\n" % name)
        made_file.flush()
        made_file.close()

    def task(name):
        def wrapper(f):
            tasks[name] = f
        return wrapper
    file = task

    def enclosure(*args, **kws):
        def enclosure(f):
            return f(*args, **kws)
        return enclosure

    exec open('makefile.py') in locals()

    try:
        import sys
        for arg in sys.argv[1:]:
            make(arg)
    except CommandException, error:
        print error

if __name__ == '__main__':
    build()

