import argparse
import os

# example parser
exmp_parser = argparse.ArgumentParser(description='Process some stuff.')
exmp_parser.add_argument('integers', metavar='N', type=int, nargs='+',
                    help='an integer')
exmp_parser.add_argument('--summit', action='store_const',
                    const=True, default=max,
                    help='tells what "sumit" does')


# my parser -> argpars

argpars = argparse.ArgumentParser(description='Backup TEVS JPEGS to another drive')
argpars.add_argument('--progress', type=int, default=None,
                     help='Report progress every N files')
argpars.add_argument('--report_only', action='store_const',
                    const=True)
argpars.add_argument('indir', nargs='?')
argpars.add_argument('outdir', nargs='?')


def parse_cl(parser, line):
    '''Accept a parser and line, spliting the line into an argv-like list,
       execute the parser, and print the in keyword-value pairs.'''

    print line
    argvlist = line.split()
    args = parser.parse_args(argvlist)
    argsdict = vars(args)
    for k in vars(args).keys():
        print k, argsdict[k]
    print
    return args

# cl = '1 2 3 4 --sum'
# args = parse_cl(exmp_parser, cl)
#
# cl = '-h'
# parse_cl(argpars, cl)
#
cl = '--progress 5000 /Users/Wes/Dropbox/Personal /private/var/tmp/Personal'
parse_cl(argpars, cl)

cl = '--progress 5000 --report_only /Users/Wes/Dropbox/Personal /private/var/tmp/Personal'
parse_cl(argpars, cl)

