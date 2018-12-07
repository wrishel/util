import argparse
import os

def get_clargs(command_line):
    print '\nCommand line args="{}"'.format(command_line)

    argpars = argparse.ArgumentParser(description='descript',
                                      prog=os.path.basename(__file__))
    # argpars.add_argument('--arg_w_value', type=int, default=-1)
    # argpars.add_argument('--kwonly_arg', type=bool)
    # argpars.add_argument('indir', nargs='?')
    # argpars.add_argument('outdir', nargs='?')
    try:
        return argpars.parse_args(command_line)
    except Exception as e:
        return e

cl = os.path.basename(__file__)
print get_clargs(cl)

print get_clargs('tryargparse.py --arg_w_value 100 ')
print get_clargs('--arg_w_value 100 /abc /d/e/f')
print get_clargs('-h')
print get_clargs('/abc /d/e/f')
