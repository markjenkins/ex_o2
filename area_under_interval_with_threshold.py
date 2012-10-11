#!/usr/bin/env python3

# Copyright Ben Arenson
# @author Mark Jenkins <mark@parit.ca>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.
# http://www.gnu.org/prep/maintain/html_node/License-Notices-for-Other-Files.html

# decimal imports
from decimal import Decimal

# imports from this project
from o2_stat import  gen_o2_stats_from_file

def trapazoid_area(bottom, side1, side2):
    return bottom * ( (side1 + side2) / 2 )

def baseline_integrate(iterable, baseline):
    data_points = 0
    integrating = False
    sum_of_traps = Decimal(0)

    for value in iterable:
        if value > baseline:
            if integrating:
                # find last area and stop integrating
                sum_of_traps += trapazoid_area(1, last, baseline)
                data_points += 1
                integrating = False
            #else: # ignore ones above baseline when not integrating
    
        elif not integrating: # and i<=baseline 
            sum_of_traps += trapazoid_area(1, baseline, value)
            data_points += 1
            integrating = True

        else: # i <=baseline and itegrating
            assert( integrating )
            # find trapazoidal area with current and last point
            sum_of_traps += trapazoid_area(1, last, value)
            data_points += 1

        last = value

    return data_points, sum_of_traps


print( 
    baseline_integrate(
        (points[0]
         for points in gen_o2_stats_from_file('test.csv') ),
         5) # baseline_integrate
    ) # print
