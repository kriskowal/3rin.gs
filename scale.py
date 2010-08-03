#!/usr/bin/env python

import Image

def scale(image, factor):
    r, g, b, a = image.split()
    image = Image.merge("RGB", (r, g, b))
    mask = Image.merge("L", (a,))
    return image.resize(
        [int(axis * factor) for axis in image.size],
        mask
    )

def scale_command(source, target, factor):
    image = Image.open(source)
    factor = float(factor)
    scale(image, factor).save(target)

def main():
    import sys
    scale_command(sys.argv[1], sys.argv[3], sys.argv[2])

if __name__ == '__main__':
    main()

