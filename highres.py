from sys import argv
input = argv[1]
output = argv[2]
open(output, 'w').write(open(input).read().replace('/practice/', '/embedded/'))
