
from itertools import chain
from tiles import TILE_WIDTH, TILE_HEIGHT

levels = (1, 2, 3, 4, 5, 6, 7, 8)
small_sizes = [1024 * n for n in (1, 2, 4, 8, 16)]
large_sizes = (32 * 1024,)
alphabets = ('tengwar', 'latin')
layers = ('geography',) + alphabets

@task('all')
def _(make, output):
    make('build/data.json')
    for size in large_sizes:
        make('build/tiles-%d' % size)
    for size in small_sizes:
        for alphabet in ('latin', 'tengwar'):
            make('build/map-%s-%d.png' % (alphabet, size))

@task('dev')
def _(make, output):
    make('build/geography-4096.png')
    make('build/labels')
    for alphabet in alphabets:
        make('build/map-%s-4096.png' % alphabet)

@file('build/data.json')
def _(make, output):
    make.command('''python data.py''')

# small maps
for size in small_sizes:
    @enclosure(size)
    def _(size):

        for alphabet in alphabets:
            @enclosure(alphabet)
            def _(alphabet):

                @file('build/map-%s-%s.png' % (alphabet, size))
                def _(make, output):
                    geography = 'build/geography-%s.png' % (size)
                    labels = 'build/labels-%s-%d.png' % (alphabet, size)
                    make(geography)
                    make(labels)
                    make.command(['python', 'over.py', geography, labels, output])

                @file('build/labels-%s-%s.png' % (alphabet, size))
                def _(make, output):
                    make.depends('labels-%s.svg' % alphabet)
                    make.command([
                        'inkscape', '-z',
                        '-e', output,
                        '-w', size, '-h', size,
                        'labels-%s.svg' % alphabet
                    ])

        @file('build/geography-%d.png' % size)
        def _(make, output):
            input = 'build/geography-combined-%d.png' % size
            make(input)
            make.command(['python', 'darken.py', input, output, .5])

        @file('build/geography-combined-%d.png' % size)
        def _(make, output):
            coast = 'build/coast-translucent-%d.png' % size
            geography = 'build/geography-translucent-%d.png' % size
            make(coast)
            make(geography)
            make.command(['python', 'over.py', coast, geography, output])

        for layer in ('coast', 'geography'):
            @enclosure(layer)
            def _(layer):

                @file('build/%s-translucent-%d.png' % (layer, size))
                def _(make, output):
                    input = 'build/%s-export-%d.png' % (layer, size)
                    make(input)
                    make.command('''(echo %s; echo %s) | bash c2a.bash''' % (
                        input,
                        output
                    ))

                @file('build/%s-export-%d.png' % (layer, size))
                def _(make, output):
                    make.command([
                        'inkscape', '-z',
                        '-e', 'build/%s-export-%d.png' % (layer, size),
                        '-w', size, '-h', size,
                        '%s.svg' % layer
                    ])

for size in large_sizes:
    @enclosure(size)
    def _(size):

        @file('build/tiles-%d' % size)
        def _(make, output):
            for layer in layers:
                make('build/tiles-%d/%s' % (size, layer[0]))

        """
        dark-> geography (tiles/g)
         ^-- over-> geography-combined
              ^-- c2a -> geography-translucent
              |    ^-- choose-> geography-chosen
              |         ^-- 0 1 2 3 4 scales
              |         |   geography-export
              |         ^-- 5 6 7 scales
              |             over -> geography-detailed
              |              ^-- geography-detail
              |              ^-- geography-export
              ^-- c2a -> coast-translucent
                   ^-- coast-export
        """

        @file('build/tiles-%d/g' % size)
        def _(make, output):
            input = 'build/geography-combined-%d/t' % size
            make(input)
            make.directory('build/tiles-%d' % size)
            make.command(['python', 'tiles_darken.py', input, output, .5])

        @file('build/geography-combined-%d/t' % size)
        def _(make, output):
            inputs = [
                'build/%s-translucent-%d/t' % (component, size)
                for component in ('coast', 'geography')
            ]
            for input in inputs:
                make(input)
            make.directory('build/geography-combined-%d' % size)
            make.command(list(chain(
                ['python', 'tiles_over.py'],
                inputs,
                [output],
            )))

        for source, target in (
            ('geography-chosen', 'geography-translucent'),
            ('coast-export', 'coast-translucent'),
        ):
            @enclosure(source, target)
            def _(source, target):
                @file('build/%s-%d/t' % (target, size))
                def _(make, output):
                    make.directory('build/%s-%d' % (target, size))
                    input = 'build/%s-%d/t' % (source, size)
                    make(input)
                    make.command(['bash', 'tiles_c2a.bash', input, output]) 

        @file('build/geography-chosen-%d/t' % size)
        def _(make, output):
            make.directory('build/geography-chosen-%d' % size)
            base = 'build/geography-export-%d/t' % size
            detailed = 'build/geography-detailed-%d/t' % size
            make(base)
            make(detailed)
            make.command([
                'python',
                'tiles_choose.py',
                output,
                '0,1,2,3,4:' + base,
                '5,6,7:' + detailed,
            ])

        @file('build/geography-detailed-%d/t' % size)
        def _(make, output):
            make.directory('build/geography-detailed-%d' % size)
            base = 'build/geography-export-%d/t' % size
            details = 'build/geography-detail-export-%d/t' % size
            make(base)
            make(details)
            make.command([
                'python',
                'tiles_over.py',
                base,
                details,
                output
            ])

        for component in ('coast', 'geography', 'geography-detail'):
            @enclosure(component)
            def _(component):

                @file('build/%s-export-%d/t' % (component, size))
                def _(make, output):
                    for quadrant in range(4):
                        make.directory('build/%s-export-%d' % (component, size))
                        input = 'build/%s-export-%d/q%d.png' % (component, size / 2, quadrant)
                        make(input)
                        make.command([
                            'python', 'tiles.py', input,
                            '%s%d' % (output, quadrant),
                        ])
                    make.directory('build/%s-export-%d' % (component, size))
                    make.command([
                        'inkscape', '-z',
                        '-e', '%s.png' % output,
                        '-w', TILE_WIDTH, '-h', TILE_HEIGHT,
                        '%s.svg' % component,
                    ])

                for quadrant, area in zip(
                    range(4),
                    (
                        '0000:3600:3600:7200',
                        '3600:3600:7200:7200',
                        '0000:0000:3600:3600',
                        '3600:0000:7200:3600',
                    ),
                ):
                    @enclosure(quadrant, area)
                    def _(quadrant, area):
                        @file('build/%s-export-%d/q%d.png' % (component, size / 2, quadrant))
                        def _(make, output):
                            make.directory('build/%s-export-%d' % (component, size / 2))
                            make.command([
                                'inkscape', '-z',
                                '-e', output,
                                '-a', area,
                                '-w', size / 2,
                                '-h', size / 2,
                                '%s.svg' % component,
                            ])

    @file('build/labels')
    def _(make, output):
        make.depends('locations.tsv')
        make.command(['python', 'labels.py'])

    for alphabet in alphabets:

        @enclosure(alphabet)
        def _(alphabet):
            @file('build/labels-%s-opaque.svg' % alphabet)
            def _(make, output):
                make.command([
                    'python', 
                    'opaque_svg.py',
                    'labels-%s.svg' % alphabet,
                    output
                ])

        for size in large_sizes:
            @enclosure(size, alphabet)
            def _(size, alphabet):

                @file('build/tiles-%s/%s' % (size, alphabet[0]))
                def _(make, output):
                    input = 'build/labels-%s-export-%d' % (alphabet, size)
                    make(input)
                    make.directory('build/tiles-%d' % size)
                    make.command(['python', 'tiles_labels.py', input, output])

                @file('build/labels-%s-export-%d' % (alphabet, size))
                def _(make, output):
                    for level in levels:
                        make('build/labels-%s-export-%d/%d' % (alphabet, size, level))

                for level in levels:
                    @enclosure(level)
                    def _(level):

                        @file('build/labels-%s-export-%d/%d' % (alphabet, size, level))
                        def _(make, output):
                            make('build/labels')
                            make('build/labels-%s-opaque.svg' % (alphabet))
                            for quadrant in range(4):
                                make.directory('build/labels-%s-export-quads-%d' % (alphabet, size / 2))
                                make('build/labels-%s-export-quads-%d/%d-%d.png' % (
                                    alphabet,
                                    size / 2,
                                    level,
                                    quadrant
                                ))
                                make('build/labels-%s-export-quads-%d/%d-%d.png' % (
                                    alphabet, size / 2, level, quadrant,
                                ))
                                make.directory('build/labels-%s-export-%d' % (alphabet, size))
                                make.command([
                                    'inkscape', '-z',
                                    '-e', '%s-.png' % output,
                                    '-w', 256, '-h', 256,
                                    '-i', 'layer%d' % level, '-j',
                                    'build/labels-%s-opaque.svg' % alphabet
                                ])
                                make.command([
                                    'python', 'tiles.py',
                                    'build/labels-%s-export-quads-%d/%d-%d.png' % (alphabet, size / 2, level, quadrant),
                                    'build/labels-%s-export-%d/%d-%d' % (alphabet, size, level, quadrant),
                                ])

                        for quadrant, area in zip(
                            range(4),
                            (
                                '0000:3600:3600:7200',
                                '3600:3600:7200:7200',
                                '0000:0000:3600:3600',
                                '3600:0000:7200:3600',
                            ),
                        ):

                            @enclosure(quadrant, area)
                            def _(quadrant, area):
                                @file('build/labels-%s-export-quads-%d/%d-%d.png' % (
                                    alphabet,
                                    size / 2,
                                    level,
                                    quadrant
                                ))
                                def _(make, output):
                                    make('build/labels')
                                    make.directory('build/labels-%s-export-%d' % (alphabet, size / 2))
                                    make.command([
                                        'inkscape', '-z',
                                        '-e', output,
                                        '-a', area,
                                        '-w', size / 2,
                                        '-h', size / 2,
                                        '-i', 'layer%s' % level, '-j',
                                        'build/labels-%s-opaque.svg' % alphabet,
                                    ])

encarda_file_names = (
    'land', 'citi', 'fiel', 'fore', 'hill',
    'isla', 'rive', 'seas', 'othe'
)

@task('build/encarda')
def _(make, output):
    for file_name in encarda_file_names:
        make('build/encarda/plac%s.html' % file_name)

for file_name in encarda_file_names:
    @enclosure(file_name)
    def _(file_name):
        @file('build/encarda/plac%s.html' % file_name)
        def _(make, output):
            make.directory('build/encarda')
            make.command([
                'curl',
                'http://www.glyphweb.com/ARDA/plac%s.html' % file_name
            ], output = output)

