#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import argparse
import numpy
import sys
import fileinput

parser = argparse.ArgumentParser(description='Simple histogram generator to quickly check the distributions of dice rolls.')
parser.add_argument('number_source', \
	help='Source for numbers to draw the histogram from. Can be a file or stdin. Intended use is piping to this, ex.: ./roll_dice 4d6 -b 3 -c 1000 | ./draw_histogram', \
	nargs = "?", type = argparse.FileType('r'), default = sys.stdin)
args = parser.parse_args()

number_columns = []
for line in fileinput.input():
	numbers = []
	for number in line.split():
		numbers.append(int(number))

	number_columns.append(numbers)

numbers = numpy.asarray(number_columns)

if numbers.shape[0] < numbers.shape[1]:
	numbers = numpy.transpose(numbers)

x_bins = range(numpy.amin(numbers), numpy.amax(numbers) + 2)
x_bin_offsets = [x + 0.5 for x in x_bins]

fig, ax = plt.subplots()

ax.xaxis.set_major_formatter(ticker.NullFormatter())
ax.xaxis.set_minor_locator(ticker.FixedLocator(x_bin_offsets))
ax.xaxis.set_minor_formatter(ticker.FixedFormatter(x_bins))

alpha = 1.0
if numbers.shape[1] > 1:
	alpha = 0.5
n, bins, patches = plt.hist(numbers, bins = x_bins, normed = True, alpha = alpha, histtype = 'stepfilled')

#ax.xaxis.grid(True, linestyle = '-', which = 'major')
plt.xticks(x_bins)
ax.xaxis.grid(True, linestyle = '-', which = 'major')
ax.yaxis.grid(True, linestyle='--') 

plt.xlabel('Result')
plt.ylabel('Probability')
plt.title('Histograms of rolls')

legend_labels = []
for i in range(numbers.shape[1]):
	legend_labels.append('$avg = ' + str(numpy.mean(numbers[:, i])) + '$, $std = ' + str(numpy.std(numbers[:, i])) + '$')
plt.legend(legend_labels, loc='upper right', shadow = True)
plt.show()