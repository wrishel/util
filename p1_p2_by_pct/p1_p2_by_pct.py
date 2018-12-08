#! python2.7

import csv
import os
import sys


details = '/Users/Wes/Dropbox/Programming/ElectionTransparency/vops/vops/details_except_114847_thru_114912.csv'

class Detail_line(object):
    '''A single line created from details.csv and updated before update.'''

    def __init__(self, line):
        parts = line.split(',')
        parts[-1] = parts[-1].strip()
        if len(parts) < 5:
            sys.stderr.write('{}: skipping short line {}\n'.format(self.linecnt, line))
            return

        self.columns = ('file|barcode|contest|choice|was_voted|' +
                        'x6|x7|x8|x9|x10|x11|x12|x13|' +
                        'fuz_contest|fuz_choice').split('|')
        self.file = parts[0]
        self.barcode = parts[1]
        self.contest = parts[2]
        self.choice = parts[3]
        self.was_voted = parts[4]
        self.x6 = parts[5]
        self.x7 = parts[6]
        self.x8 = parts[7]
        self.x9 = parts[8]
        self.x10 = parts[8]
        self.x11 = parts[10]
        self.x12 = parts[11]
        self.x13 = parts[12]
        self.fuz_contest = None
        self.fuz_choice = None

    def __str__(self):
        s = '<dl '
        items = []
        for col in self.columns:
            ss = col
            ss += ': '
            ss += str(getattr(self, col))
            items.append(ss)

        s += ('; ').join(items)
        s += '>'
        return s

class Detail_lines(list):
    def __init__(self):
        pass


class Report_line(object):
    def __init__(self, precinct, barcode):
        self.precinct = precinct
        self.barcode = barcode
        self.count_p1 = 0
        self.count_p2 = 0


class HARTS_barcode(object):
    """A barcde according to the HARTS format used in Eureka County, CA

        #
        # 10000010100013
        # +------------- page number
        #  +++++++------ precinct number
        #         +----- side e,g, 1,2,3 or 4
        #          ????? unknown purpose, some digits are probably redundcany codes
    """

    def __init__(self, codestring):
        self.codestring = codestring
        self.pagenum = int(codestring[0])
        self.pctnum = codestring[1:8]
        self.side = int(codestring[8:9])

    def __str__(self):
        return self.codestring


class Report_lines(dict):
    def accept(self, dl, pctids):
        """Integrate a detail line by adding or updating entries in this dict"""
        hbc = HARTS_barcode(dl.barcode)  # extract the digit string that IDs the precinct
        try:
            pctid = pctids[hbc.pctnum]              # get the corresponding ID
        except Exception as e:
            sys.stderr.write(('Detail line = {}\n'.format(dl)))
            sys.stderr.write(('could not file precinct ID of: {} in {}\n'.format(hbc.pctnum, str(hbc))))
            raise
        rl = self.get(pctid, Report_line(pctid, hbc.pctnum))
        if hbc.pagenum == 1:
            rl.count_p1 += 1
        else:
            rl.count_p2 += 1
        self[pctid] = rl

# ---------------------------------------------------   main   ---------------------------------------------------
#
if __name__ == '__main__':

    # misc parameters
    #
    SHORT_RUN = None

    # files
    #
    path_to_data = os.getcwd() + '/../vops/'
    pth_elections_static = path_to_data + 'static_2018_nov/'
    INF_DETAILS = path_to_data + 'vops/' + 'details_except_114847_thru_114912.csv'
    INF_HARTS_PRECINCTS = pth_elections_static + 'precincts_massaged.txt'  # 'precincts.tsv'

    # load precinct IDs
    #
    precinctids = dict()
    with open(INF_HARTS_PRECINCTS) as precidf:
        rd = csv.reader(precidf, delimiter="\t", quotechar='"')
        for row in rd:
            precinctids[row[0]] = row[1]


    # load the detail lines and merge then into report lines
    #
    detail_lines = Detail_lines()
    report_lines = Report_lines()
    with  open(INF_DETAILS) as detailsfile:
        lastfilename = None
        lcnt = 0
        for line in detailsfile:
            if SHORT_RUN and lcnt > SHORT_RUN:
                break
            lcnt += 1
            detlin = Detail_line(line)
            if lastfilename == detlin.file: # only once per file
                continue
            lastfilename = detlin.file
            report_lines.accept(detlin, precinctids)

    print('PRECINCT    PAGE 1')
    print('--------    ------')
    # print('PRECINCT    PAGE 1   PAGE-2')
    # print('--------    ------   ------')
    for k in sorted(report_lines.keys()):
        r = report_lines[k]
        print('{:6}      {:6,}'.format(r.precinct, r.count_p1 / 2.0))
        # print('{:6}      {:6,}   {:6,}'.format(r.precinct, r.count_p1 / 2.0, r.count_p2 / 2.0))

