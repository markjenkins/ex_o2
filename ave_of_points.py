#!/usr/bin/env python3

# Copyright St Boniface Hospital
# @author Mark Jenkins <mark@parit.ca>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.
# http://www.gnu.org/prep/maintain/html_node/License-Notices-for-Other-Files.html

# python imports
from sys import argv

# imports from this project
from o2_stat import gen_points_over_interval
from stats import average

def ave_over_interval(filename, start_row, end_row):
    (chan1_ave, chan2_ave) = tuple(
        average( points[i]
                 for points in
                 gen_points_over_interval(filename, start_row, end_row)
                 if points[i] != None )
        for i in range(1+1) )
    return( chan1_ave, chan2_ave, average( (chan1_ave, chan2_ave) ) )


