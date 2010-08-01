#!/usr/bin/env python

import Image

def fade(image, factor):
    backdrop = Image.new("RGBA", image.size, (255, 255, 255, 0))
    mask = Image.new("L", image.size, int(255 * factor))
    backdrop.paste(image, (0, 0), mask)
    return backdrop

def main():
    import sys
    image = Image.open(sys.argv[1])
    factor = float(sys.argv[2])
    fade(image, factor).save(sys.argv[3])

if __name__ == '__main__':
    main()

