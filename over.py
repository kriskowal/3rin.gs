#!/usr/bin/env python

import Image
import numpy
numpy.seterr(all='ignore')

numpy.seterr(all='ignore')

def over(front,back):
    # The formula comes from http://en.wikipedia.org/wiki/Alpha_compositing
    front = numpy.asarray(front.convert("RGBA"))
    back = numpy.asarray(back.convert("RGBA"))
    result=numpy.empty(front.shape,dtype='float')
    fa=front[:,:,3]/255.0
    ba=back[:,:,3]/255.0
    result[:,:,3]=(fa+ba*(1-fa))
    for i in range(3):
        f=front[:,:,i]
        b=back[:,:,i]        
        result[:,:,i]=((f*fa)+ b*ba*(1-fa))/result[:,:,3]
    result[:,:,3]*=255
    front_transparent=(fa<=0.001)&(ba>0.001)
    result[front_transparent]=back[front_transparent]
    back_transparent=(ba<=0.001)&(fa>0.001)
    result[back_transparent]=front[back_transparent]
    return Image.fromarray(result.astype('uint8'), "RGBA")

def command(a, b, target):
    try:
        a = Image.open(a)
        b = Image.open(b)
        over(b, a).save(target)
    except IOError:
        print 'ERROR', a, b, target

def main():
    import sys
    command(*sys.argv[1:])

if __name__ == '__main__':
    main()

