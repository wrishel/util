

"""Copy some files from indir tree to outdir tree,
   creating subdirs of outdir as needed.


usage: copy_unmatched.py [-h] [--progress PROGRESS] [--report_only]
                         [--safe_overwrite]
                         [indir] [outdir]

Copies file excluding those that begin with "." or end with "~".

positional arguments:
  indir                The directory files are copied from
  outdir               The directory files are copied to

optional arguments:
  -h, --help           show this help message and exit
  --progress PROGRESS  Report progress every N files
  --report_only        Don't actually scan files but report as if we did
  --safe_overwrite     Don't overwrite unsave files that are " "already
                       present in the output

If a file already exists in the output it is considered 'safe' to copy if it
the new file is younger or smaller than the file beinc copied.
"""

import argparse
import datetime
import os
import signal
import shutil
import sys
import time


#  -------- SAFE EXIT ON SIGTERM, SIGINT  --------

global interruption     # if true, the code should exit
interruption = False    # at the next safe place

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    global interruption
    interruption = True

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

#  -------------------  UTILITIES  ----------------

def tot_secs(start):
    """Return the integer total seconds between now and the datetime start. """

    now = datetime.datetime.now()
    return int((now - start).total_seconds())

def seconds_since(last_time):
    """Return the integer total seconds between now and the integer last_time."""

    now = int(datetime.datetime.now().total_seconds())
    return  now - last_time

def pathminus(path, basepath):
    """returh the path left-stripped of base path or None if the basepath doesn't match"""

    pathparts = path.split('/')
    baseparts = basepath.split('/')
    outparts = list()
    pathsize = len(pathparts)
    basesize = len(baseparts)
    if basesize > pathsize:
        return None

    for i in range(basesize):
        if pathparts[i] == baseparts[i]:
            continue
        return None

    retpath = '/'.join(pathparts[i + 1:])
    return retpath

def progress_report(in_cnt, out_cnt, identical_cnt, head='', last_from=None):
    fmtn = '{:12} {:20} = {:10,}'
    fmts = '{:12} {:20} = {}'
    print
    print fmts.format(head,'time:', str(datetime.datetime.now()))
    print fmtn.format(head,'files checked', in_cnt)
    print fmtn.format(head,'files copied', out_cnt)
    print fmtn.format(head,'identical files', identical_cnt)

    if last_from:
        print fmts.format(head, 'Last file examined', last_from)


#  -----------------  MAIN FILE COPY  --------------

def copyfilenstat(frompath, to_path, report_only, safe_overwrite):
    """Copy file and metadata from frompath to the to_path creating any directories
       needed to fulfill to_path. Don't recopy seemingly identical files.


       Returns:
             1:  file copied
             0:  file not copied but would have, if report_only were false
            -1:  file not copied because it already exists and appears to be
                 identical
            -2:  file not copied because it already exists, is different
                 from the source and safe_overwrite is true

        Will throw exceptions if:
           - any needed directories to fulfill to_path can not be created
           - to_path already exists and is not a file.
           - permissions interfere with copy or metadata copy."""

    from_stat = os.stat(from_path)
    try:
        to_stat  = os.stat(to_path)
    except OSError as e:
        to_stat = None

    if to_stat:         # already a file in the destination

        # do not overwrite if the files appear the same (length and date)
        #
        if int(to_stat.st_mtime) - int(from_stat.st_mtime) == 0 \
                and to_stat.st_size <= from_stat.st_size:
            return -1

        if safe_overwrite:
            # various safety filters for overwriting to an existing file
            #
            if int(to_stat.st_mtime) - int(from_stat.st_mtime) >= 0 \
                    or to_stat.st_size >= from_stat.st_size:

                # this is an unsafe copy and save_overwrite is true
                #
                return -2

    # fall through here if file should be written and is safe or safe_copy is false

    to_dirtree, to_basename = os.path.split(to_path)
    if not report_only:
        if not os.path.exists(to_dirtree):
            os.makedirs(to_dirtree)
        shutil.copy2(frompath, to_path) # copy file and metadata
        return 1
    return 0

#  -----------------  PROCESS COMMAND LINE  --------------

def get_clargs():
    description = """Copies file excluding those that begin with '.'
           or end with '~' and '.marker'."""
    epilog = """If a file already exists in the output it is considered 'safe'
    to copy if it the new file is younger or smaller than the file beinc copied."""

    argpars = argparse.ArgumentParser(description=description,
                                      epilog=epilog)
    argpars.add_argument('--progress', type=int, default=None,
                         help='Report progress every N seconds')
    argpars.add_argument('--report_only', action='store_const',
                         const=True, help="Don't actually scan files but report as if we did")
    argpars.add_argument('--safe_overwrite', action='store_const',
                         const=True, help="""Don't overwrite unsave files that are "
                                          "already present in the output""")
    argpars.add_argument('indir',  nargs='?', help='The directory files are copied from')
    argpars.add_argument('outdir', nargs='?', help='The directory files are copied to')
    return argpars.parse_args()

# ---------------------------------------- MAIN ---------------------------------------- #

clargs = get_clargs()
print clargs
stderr = sys.stderr

uncopied = list()
from_dir = clargs.indir
to_dir = clargs.outdir
in_cnt = 0
out_cnt = 0
progress_interval = clargs.progress

file_list = []

start_time = datetime.datetime.now()

# make a sorted list of all valid files in from_dir tree
#
for root, subdirs, files in os.walk(from_dir):
    for filename in files:
        from_path = os.path.join(root, filename)
        if not ('/.' in from_path or from_path.endswith('%')
                or from_path.endswith('.marker')):
            in_cnt += 1
            file_list.append(from_path)

        if in_cnt % (progress_interval * 10) == 0:
            print('{:8} {}'.format(in_cnt, str(datetime.datetime.now())))

        if interruption:
            print "Process Terminated"
            exit(0)

print ('NUMBER OF SOURCE FILES: {}'.format(len(file_list)))

file_list = sorted(file_list)

print  len(file_list), "files to be examined and maybe copied"
last_report = datetime.datetime.now()
in_cnt = 0
identical_cnt = 0


for from_path in file_list:
    time_since_last = tot_secs(last_report)
    if time_since_last > clargs.progress:
        last_report = datetime.datetime.now()
        progress_report(in_cnt, out_cnt, identical_cnt, 'Progress', from_path)

    relpath = pathminus(from_path, from_dir)
    to_path = os.path.join(to_dir, relpath)
    in_cnt += 1
    # time.sleep(0.005)  $ only got testing progress report timing
    try:
        r = copyfilenstat(from_path, to_path, clargs.report_only, clargs.safe_overwrite)
    except ValueError as e:
        print('\nskipped file due to outfile larger or earlier date:\n{}'\
              .format(from_path))
        uncopied.append(from_path)

    if r in [1, 0]:
        out_cnt += 1

    if r == -1:
        identical_cnt += 1

    if r == -2:
        uncopied.append(from_path)

    if interruption:
        progress_report(in_cnt, out_cnt, 'Interruption', from_path)
        print 'Process terminated by user'
        exit(0)

if clargs.report_only:
    print """The fileds shown 'copied' would have been copied without the """ +\
    """report_only parameter"""
progress_report(in_cnt, out_cnt, identical_cnt, 'Final', from_path)

print 'Files not copied due to size or modified date (if any)'
for p in uncopied:
    print '\t', p




