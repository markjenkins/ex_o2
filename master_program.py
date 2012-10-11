#!/usr/bin/env python3

# Copyright Ben Arenson
# @author Mark Jenkins <mark@parit.ca>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.
# http://www.gnu.org/prep/maintain/html_node/License-Notices-for-Other-Files.html

# python imports
from os.path import exists, join
from decimal import Decimal
from sys import argv
from csv import DictWriter

# imports from this project
from ave_of_points import ave_over_interval
from area_under_interval_with_threshold import \
    baseline_integrate_chan_after_time, \
    baseline_integrate_avg_of_chans_after_time, \
    gen_avg_pair_stream
from o2_stat import gen_o2_stats_from_file

FILE_PREFIX = 'CSVs'

SECONDS_PER_MINUTE = 60
SECONDS_PER_INTERVAL = 4
# convert to int because python3 converts to float on division now
INTERVALS_PER_MINUTE = int(SECONDS_PER_MINUTE / SECONDS_PER_INTERVAL)

ROOM_AIR_START = INTERVALS_PER_MINUTE * 1
ROOM_AIR_END = INTERVALS_PER_MINUTE*2 - 1

O2_START = INTERVALS_PER_MINUTE * 2
O2_END = INTERVALS_PER_MINUTE * 3 - 1

 # 4/60 = 0.0666.. minutes
INTERVAL_LENGTH = Decimal(SECONDS_PER_INTERVAL) / Decimal(SECONDS_PER_MINUTE)

DECIMAL_PLACES = 4

CSV_FIELDNAMES = [
        'subject_id',

        'data_point_count_OR',
        'data_point_count_ICU',
        'data_point_count_OR_useful',
        'data_point_count_ICU_useful',

        'o2_both_chan_baseline',
        'o2_chan1_baseline',
        'o2_chan2_baseline',
        'ra_both_chan_baseline',
        'ra_chan1_baseline',
        'ra_chan2_baseline',

        'chan-1_O2_ICU_AUB',
        'chan-1_O2_ICU_TUB',
        'chan-1_O2_OR_AUB',
        'chan-1_O2_OR_TUB',
        'chan-1_RA_ICU_AUB',
        'chan-1_RA_ICU_TUB',
        'chan-1_RA_OR_AUB',
        'chan-1_RA_OR_TUB',
        'chan-2_O2_ICU_AUB',
        'chan-2_O2_ICU_TUB',
        'chan-2_O2_OR_AUB',
        'chan-2_O2_OR_TUB',
        'chan-2_RA_ICU_AUB',
        'chan-2_RA_ICU_TUB',
        'chan-2_RA_OR_AUB',
        'chan-2_RA_OR_TUB',
        'chan-avg_O2_ICU_AUB',
        'chan-avg_O2_ICU_TUB',
        'chan-avg_O2_OR_AUB',
        'chan-avg_O2_OR_TUB',
        'chan-avg_RA_ICU_AUB',
        'chan-avg_RA_ICU_TUB',
        'chan-avg_RA_OR_AUB',
        'chan-avg_RA_OR_TUB',

        # adjusted averages
        'chan-avg_RA_OR_<10_AUB',
        'chan-avg_RA_OR_<10_TUB',
        'chan-avg_RA_OR_<15_AUB',
        'chan-avg_RA_OR_<15_TUB',
        'chan-avg_RA_OR_<20_AUB',
        'chan-avg_RA_OR_<20_TUB',

        'chan-avg_RA_ICU_<10_AUB',
        'chan-avg_RA_ICU_<10_TUB',
        'chan-avg_RA_ICU_<15_AUB',
        'chan-avg_RA_ICU_<15_TUB',
        'chan-avg_RA_ICU_<20_AUB',
        'chan-avg_RA_ICU_<20_TUB',

        # absolute
        'chan-avg_RA_OR_=60_AUB',
        'chan-avg_RA_OR_=60_TUB',
        'chan-avg_RA_OR_=55_AUB',
        'chan-avg_RA_OR_=55_TUB',
        'chan-avg_RA_OR_=50_AUB',
        'chan-avg_RA_OR_=50_TUB',

        'chan-avg_RA_ICU_=60_AUB',
        'chan-avg_RA_ICU_=60_TUB',
        'chan-avg_RA_ICU_=55_AUB',
        'chan-avg_RA_ICU_=55_TUB',
        'chan-avg_RA_ICU_=50_AUB',
        'chan-avg_RA_ICU_=50_TUB',
    ]

#CSV_FIELDNAMES.sort()
#for fieldname in CSV_FIELDNAMES:
#    print("        '%s'," % fieldname)
#exit(0)

FIRST_SUBJECT = 3
LAST_SUBJECT = 3

#FIRST_SUBJECT = 3
#LAST_SUBJECT = 100

def analyze_file_and_channel_after_start_with_baseline(
    filename, baseline, start, channel):
    if channel in (1, 2):
        number_of_traps, sum_of_traps = baseline_integrate_chan_after_time(
            filename, baseline, start, channel)
    else:
        number_of_traps, sum_of_traps = \
            baseline_integrate_avg_of_chans_after_time(
            filename, baseline, start)

    time_under_baseline = number_of_traps * INTERVAL_LENGTH

    baseline_rectangle = time_under_baseline * baseline 
    area_of_traps = sum_of_traps * INTERVAL_LENGTH 

    # the area under the baselime during the time
    # under the baseline, minus the area of the trapazoids
    area_under_baseline = baseline_rectangle - area_of_traps

    # here's another way of looking at it
    # this assert is true algebraicly
    assert( round(
            (number_of_traps * baseline - sum_of_traps)  * INTERVAL_LENGTH, 5)
            == round(area_under_baseline, 5) )

    return ( time_under_baseline, area_under_baseline )


FILE_AND_BASELINE_TYPE_TO_START_TABLE = {
    'OR': { 'RA': ROOM_AIR_END+1,
            'O2': O2_END+1},
    'ICU': { 'RA': 1,
             'O2': 1 },
    }

def analyse_combo(baseline, baseline_type, channel, filename,
                  special_baseline_suffix='', start=False):
    file_type = 'OR' if 'OR' in filename else 'ICU'
    assert( file_type in filename )
    if not start:
        start = FILE_AND_BASELINE_TYPE_TO_START_TABLE[file_type][baseline_type]

    time_under_baseline, area_under_baseline = (
        analyze_file_and_channel_after_start_with_baseline(
            filename, baseline, start, channel) )

    field_prefix = 'chan-%s_%s_%s%s' % (
        channel, baseline_type,
        file_type, special_baseline_suffix)

    return { field_prefix + '_TUB': time_under_baseline,
             field_prefix + '_AUB': area_under_baseline }

def not_nones(iteration):
    return ( value
             for value in iteration
             if value != None )

def generator_len(iteration):
    return sum( 1
                for value in iteration )

def analyse_subject(i, output_csv):
    or_file = join(FILE_PREFIX, '%s_OR.CSV' % i)
    if exists(or_file):
        icu_file = join(FILE_PREFIX, '%s_ICU.CSV' % i)
        assert( exists(icu_file) )
    else:
        return # exit early if there is no such subject

    ra_chan1_baseline, ra_chan2_baseline, ra_both_chan_baseline = \
        ave_over_interval(or_file, ROOM_AIR_START, ROOM_AIR_END)

    o2_chan1_baseline, o2_chan2_baseline, o2_both_chan_baseline = \
        ave_over_interval(or_file, O2_START, O2_END)
    
    results_dict = {
        'subject_id': i,
        'ra_chan1_baseline': ra_chan1_baseline,
        'ra_chan2_baseline': ra_chan2_baseline,
        'ra_both_chan_baseline': ra_both_chan_baseline,
        'o2_chan1_baseline': o2_chan1_baseline,
        'o2_chan2_baseline': o2_chan2_baseline,
        'o2_both_chan_baseline': o2_both_chan_baseline,
        'data_point_count_OR':
            generator_len(gen_o2_stats_from_file(or_file)),
        'data_point_count_ICU':
            generator_len(gen_o2_stats_from_file(icu_file)),
        'data_point_count_OR_useful':
            generator_len(not_nones(gen_avg_pair_stream(gen_o2_stats_from_file(
                        or_file)))),
        'data_point_count_ICU_useful':
            generator_len(not_nones(gen_avg_pair_stream(gen_o2_stats_from_file(
                        icu_file)))),
        }

    for filename in (or_file, icu_file):
        for baseline, baseline_type, channel, suffix in (
            (ra_chan1_baseline, 'RA', 1, ''),
            (ra_chan2_baseline, 'RA', 2, ''),
            (ra_both_chan_baseline, 'RA', 'avg', ''),
            (o2_chan1_baseline, 'O2', 1, ''),
            (o2_chan2_baseline, 'O2', 2, ''),
            (o2_both_chan_baseline, 'O2', 'avg', ''),

            # adjusted averages
            (ra_both_chan_baseline * Decimal('0.9'), 'RA', 'avg', '_<10'),
            (ra_both_chan_baseline * Decimal('0.85'), 'RA', 'avg', '_<15'),
            (ra_both_chan_baseline * Decimal('0.8'), 'RA', 'avg', '_<20'),

            # absolute baselines
            (Decimal('60'), 'RA', 'avg', '_=60'),
            (Decimal('55'), 'RA', 'avg', '_=55'),
            (Decimal('50'), 'RA', 'avg', '_=50'),            
            ):
            results_dict.update(
                analyse_combo(baseline, baseline_type,
                              channel, filename, suffix) )
            
    # round all results to 3 decimal places
    for key in results_dict:
        if key != 'subject_id':
            results_dict[key] = round( results_dict[key], DECIMAL_PLACES )

    output_csv.writerow(results_dict)

def main():
    output_file_path = 'output.csv' if len(argv) < 2 else argv[1]
    with open(output_file_path, 'w') as f:
        results_csv = DictWriter(f, CSV_FIELDNAMES)
        results_csv.writeheader()
        for i in range(FIRST_SUBJECT, LAST_SUBJECT+1):
            analyse_subject(i, results_csv)

if __name__ == "__main__":
    main()
        
