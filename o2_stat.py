#!/usr/bin/env python3

# Copyright Ben Arenson
# @author Mark Jenkins <mark@parit.ca>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.
# http://www.gnu.org/prep/maintain/html_node/License-Notices-for-Other-Files.html

from csv import DictReader
from sys import argv

def gen_o2_stats_from_file(filename):
    with open(filename) as f:
        d = DictReader(f, )
        for line in d:
            yield ( int(line[' Ch1rSO2']),
                    int(line[' Ch2rSO2']) )


