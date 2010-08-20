
import Image
import numpy

def w2aa(array):
    xl, yl, cl = array.shape
    flat = array.reshape((xl * yl, cl))
    opaque = numpy.empty((xl * yl, 3), dtype='float')
    a = numpy.empty((xl * yl, 1), dtype='float')
    rgb_ix = numpy.ix_(range(xl * yl), range(3))
    a_ix = numpy.ix_(range(xl * yl), (3,))
    a[:] = flat[a_ix] / 255.
    opaque[:] = flat[rgb_ix] / 255.
    whiteness = opaque.min(axis=1)
    removal = numpy.vstack((whiteness, whiteness, whiteness)).T
    color = (opaque - removal) / (1 - removal)
    flat[rgb_ix] = color * 255
    flat[a_ix] = whiteness.reshape(a.shape) * a * 255
    return flat.reshape(array.shape)

def w2a(image):
    image = numpy.asarray(image.convert("RGBA")).copy()
    image = w2aa(image)
    return Image.fromarray(image.astype("uint8"), "RGBA")

def command(source, target):
    image = Image.open(source)
    w2a(image).save(target)

def main():
    import sys
    command(sys.argv[1], sys.argv[2])

def test():
    before = numpy.array([
        [
            (255, 128, 128, 255),
            (255, 128, 128, 255),
        ],
        [
            (255, 128, 63, 255),
            (255, 128, 63, 255),
        ],
        [
            (255, 128, 0, 255),
            (255, 128, 0, 255),
        ],
    ])
    print before
    print '-'
    print w2aa(before)

if __name__ == '__main__':
    main()

