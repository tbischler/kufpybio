#!/usr/bin/env python
"""
Copyright (c) 2013, Konrad Foerstner <konrad@foerstner.org>

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all
copies.

THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

"""
__description__ = ("Calculate the Pearson correlation coefficient "
                   "for the coverages of two wiggle files.")
__author__ = "Konrad Foerstner <konrad@foerstner.org>"
__copyright__ = "2013 by Konrad Foerstner <konrad@foerstner.org>"
__license__ = "ISC license"
__email__ = "konrad@foerstner.org"
__version__ = ""

import argparse

from wiggle import WiggleParser
import numpy as np
from scipy import stats
#import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("--wiggle_file_1a", type=argparse.FileType("r"), required=True)
    parser.add_argument("--wiggle_file_1b", type=argparse.FileType("r"), required=True)
    parser.add_argument("--wiggle_file_2a", type=argparse.FileType("r"), required=True)
    parser.add_argument("--wiggle_file_2b", type=argparse.FileType("r"), required=True)
    parser.add_argument('-m', '--method', choices=('pearson', 'spearman'), default="pearson")
    parser.add_argument('-r', '--rep_sizes', required=True)
    args = parser.parse_args()
    wiggle_correlator = WiggleCorrelator(args)
    wiggle_correlator.correlate(args.wiggle_file_1a, args.wiggle_file_2a, args.wiggle_file_1b, args.wiggle_file_2b)

class WiggleCorrelator(object):

    def __init__(self, args):
        self._wiggle_parser = WiggleParser()
        self._method = args.method
        self._rep_dict = dict([rep.split(':') for rep in args.rep_sizes.strip().split(',')])

    def correlate(self, wiggle_file_1a, wiggle_file_2a, wiggle_file_1b = None, wiggle_file_2b = None ):

        print("Replicon: %s correlation coefficient (p-value)" % self._method)
        for entry_1a, entry_2a, entry_1b, entry_2b in zip(
                self._wiggle_parser.entries(wiggle_file_1a),
                self._wiggle_parser.entries(wiggle_file_2a),
                self._wiggle_parser.entries(wiggle_file_1b),
                self._wiggle_parser.entries(wiggle_file_2b)):
                assert(entry_1a.chrom_name == entry_2a.chrom_name == entry_1b.chrom_name == entry_2b.chrom_name)
                pos_value_pairs_1a = dict(entry_1a.pos_value_pairs)
                pos_value_pairs_2a = dict(entry_2a.pos_value_pairs)
                pos_value_pairs_1b = dict(entry_1b.pos_value_pairs)
                pos_value_pairs_2b = dict(entry_2b.pos_value_pairs)
                if (len(pos_value_pairs_1a) == 0 and len(pos_value_pairs_1b) == 0) or (
                    len(pos_value_pairs_2a) == 0 and len(pos_value_pairs_2b) == 0):
                    print("%s: At least one replicon has no coverage for "
                          "this libs." % (entry_1a.chrom_name))
                    continue

                values_1 = np.array(
                    [pos_value_pairs_1a.get(pos, 0.0) for pos in range(1, int(self._rep_dict[entry_1a.chrom_name])+1)] +
                    [pos_value_pairs_1b.get(pos, 0.0) for pos in range(1, int(self._rep_dict[entry_1b.chrom_name])+1)])
                values_2 = np.array(
                    [pos_value_pairs_2a.get(pos, 0.0) for pos in range(1, int(self._rep_dict[entry_2a.chrom_name])+1)] +
                    [pos_value_pairs_2b.get(pos, 0.0) for pos in range(1, int(self._rep_dict[entry_2b.chrom_name])+1)])

                if self._method == "pearson":
                    corr, pvalue = stats.pearsonr(values_1, values_2)
                else:
                    corr, pvalue = stats.spearmanr(values_1, values_2)

                print("%s: %s (%s)" % (entry_1a.chrom_name, corr, pvalue))

if __name__ == "__main__":
   main()
