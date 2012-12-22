# Copyright St Boniface Hospital
# @author Mark Jenkins <mark@parit.ca>
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.
# http://www.gnu.org/prep/maintain/html_node/License-Notices-for-Other-Files.html

from decimal import Decimal

def average(iterable):
    total = Decimal(0)
    count = Decimal(0)
    ONE = Decimal(1)
    for blah in iterable:
        total += blah
        count += ONE
    return total / count
