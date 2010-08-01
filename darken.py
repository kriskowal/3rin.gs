
import Image
import numpy

def darken(image, factor):
    image = numpy.asarray(image.convert("RGBA")).copy()
    x, y, c = image.shape
    image[numpy.ix_(range(x),range(y),(0, 1, 2))] *= factor
    return Image.fromarray(image.astype('uint8'), "RGBA")

def darken_command(source, target, factor):
    image = Image.open(source)
    factor = float(factor)
    darken(image, factor).save(target)

def main():
    import sys
    darken_command(sys.argv[1], sys.argv[3], sys.argv[2])

if __name__ == '__main__':
    main()

