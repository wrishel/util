#!/user/bin/python
"""Visit the image outputs of TEVS and report on all image files, missing or present.

Written by Wes Rishel as part of the Trachtenberg Election Verification System.

Intended for open source use via the same license used by TEVS.
"""

import os
import glob
import datetime


def name_time(p):
    """Return a string representing the mtime for the file identifed by integer p."""

    try:
        modtime = os.path.getmtime(p)
    except Exception as e:
        print e.__repr__()
        exit(-1)
    modtimes = datetime.datetime.fromtimestamp(modtime)
    filename = os.path.basename(p)
    return modtimes

def item_block_fmt(start, end):
    """Given integers start and end, print the file names (no times("""

    return '{:06d}.jpg - {:06d}.jpg  ({:,d} files)'\
        .format(start, end, end - start + 1)

PATHSPEC = '/Users/Wes/NotForTheCloud/2018_Nov/unproc/*/*.jpg'
MAXNUM = 299999
jpglist = []
paths = glob.glob(PATHSPEC)

for p in paths:
    _, f = os.path.split(p)
    jpglist.append(f)

img_cnt = 0
jpglist = sorted(jpglist)
first_good = jpglist[0][0]
lastnum = -1 + int((first_good.split('.')[0]))
if lastnum != -1:
    raise Exception('What if 000000.jpg is missing?')

previous_last_bad = -1
print
print '             files present                               gap between files'
print '-----------------------------------------    ---------------------------------------'

for f in jpglist:
    thisnum = int((f.split('.')[0]))
    if thisnum > MAXNUM:
        break

    if thisnum > lastnum + 1:

        # there is a gap running from lastnum +1 to thisnum - 1
        #
        s = item_block_fmt(previous_last_bad + 1, lastnum)
        s += (' ' * (45 - len(s)) + item_block_fmt(lastnum + 1, thisnum - 1))
        print s

        previous_last_bad = thisnum - 1
        lastnum = thisnum
        img_cnt += 1

    else:
        lastnum += 1
        img_cnt += 1
        last_file = f

print item_block_fmt(previous_last_bad + 1, lastnum)
print
print 'Images counted:           {:8,d} files'.format(img_cnt)
print
print "Last file scanned = ", last_file
