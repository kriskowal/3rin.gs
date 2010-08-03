#!/usr/bin/env python

import Image

def fade(image, factor):
    backdrop = Image.new("RGBA", image.size, (255, 255, 255, 0))
    mask = Image.new("L", image.size, int(255 * factor))
    backdrop.paste(image, (0, 0), mask)
    return backdrop

def command(source, target, factor):
    image = Image.open(source)
    factor = float(factor)
    fade(image, factor).save(target)

def main():
    import sys
    command(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()

