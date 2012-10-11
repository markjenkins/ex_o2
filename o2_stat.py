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
from decimal import Decimal

def gen_o2_stats_from_file(filename):
    with open(filename) as f:
        d = DictReader(f, )
        for line in d:
            try:
                one = Decimal( int(line[' Ch1rSO2']) )
            except ValueError:
                one = None

            try:
                two = Decimal( int(line[' Ch2rSO2']) )
            except ValueError:
                two = None

            yield (one, two)

def gen_points_after_interval(filename, start):
    return ( points
             for i, points in enumerate(gen_o2_stats_from_file(filename), 1)
             if i>=start )

def gen_points_over_interval(filename, start, end):
    return ( points
             for i, points in enumerate(gen_o2_stats_from_file(filename), 1)
             if i>=start and i<=end )




