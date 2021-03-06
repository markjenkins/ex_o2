#!/usr/bin/env python3

# Copyright St Boniface Hospital
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
from o2_stat import  gen_o2_stats_from_file, gen_points_after_interval
from stats import average

def trapazoid_area(bottom, side1, side2):
    return bottom * ( average( (side1, side2) )  )

def baseline_integrate(iterable, baseline):
    number_of_traps = 0
    integrating = False
    sum_of_traps = Decimal(0)
    
    for value in iterable:
        if value == None:
            if integrating:
                # find last area and stop integrating
                sum_of_traps += trapazoid_area(1, last, baseline)
                number_of_traps += 1
                integrating = False
        elif value > baseline:
            if integrating:
                # find last area and stop integrating
                sum_of_traps += trapazoid_area(1, last, baseline)
                number_of_traps += 1
                integrating = False
            #else: # ignore ones above baseline when not integrating
    
        elif not integrating: # and i<=baseline 
            sum_of_traps += trapazoid_area(1, baseline, value)
            number_of_traps += 1
            integrating = True

        else: # i <=baseline and itegrating
            assert( integrating )
            # find trapazoidal area with current and last point
            sum_of_traps += trapazoid_area(1, last, value)
            number_of_traps += 1

        last = value

    return number_of_traps, sum_of_traps

def gen_avg_pair_stream(iterable):
    for pair in iterable:
        if (None, None) == pair:
            yield None
        else:
            yield pair[0] if pair[1] == None else (
                pair[1] if pair[0] == None else average(pair) )

def baseline_integrate_avg_of_chans_after_time(
    filename, baseline, start):
    return baseline_integrate(
        gen_avg_pair_stream(gen_points_after_interval(filename, start)),
        baseline )

def baseline_integrate_chan_after_time(
    filename, baseline, start, channel):
    # channel is assumed to be 1 or 2, adjust to 0 index
    return baseline_integrate( 
        ( points[channel-1]
          for points in gen_points_after_interval(filename, start) ),
        baseline ) # baseline_integrate




