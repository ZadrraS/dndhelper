#!/usr/bin/env python

import argparse
import dice_util as du

parser = argparse.ArgumentParser(description='Simple dice roller for D&D 5th edition.')
parser.add_argument('die_code', help='Code for the dice roll, ex.: 3d6+4-1d4-1', nargs='+')
parser.add_argument('-c', help='number of times to repeat the roll', type = int)

parser.add_argument('-a', help='roll width advantage (die_code has to be of the form 1d20{+-x}', action = 'store_true')
parser.add_argument('-d', help='roll width disadvantage (die_code has to be of the form 1d20{+-x}', action = 'store_true')

parser.add_argument('-crit', help='roll critical hit damage', action = 'store_true')

parser.add_argument('-b', help='only sum specified number of best rolls (can only include one die type in a roll)', type = int)
parser.add_argument('-w', help='only sum specified number of worst rolls (can only include one die type in a roll)', type = int)

args = parser.parse_args()

repeats = 1
if args.c is not None:
	if args.c >= 1:
		repeats = args.c

try:
	true_arguments = int(args.a) + int(args.d) or int(args.b is not None) + int(args.w is not None) + int(args.crit)
	if true_arguments >= 2:
		raise Exception("You used more than one of these arguments: -a, -d, -b, -w or -crit.")

	for i in range(repeats):
		rolls = []
		for die_code in args.die_code:
			dice, bonus = du.parse_roll_line(die_code)

			if args.a:
				if len(dice) > 1 or dice[0][2] != 20:
					raise Exception("Can only do a 1d20+x type of roll with advantage.")

				rolls.append(max(du.roll_batch(dice[0]), du.roll_batch(dice[0])) + bonus)
			elif args.d:
				if len(dice) > 1 or dice[0][2] != 20:
					raise Exception("Can only do a 1d20+x type of roll with disadvantage.")

				rolls.append(max(du.roll_batch(dice[0]), du.roll_batch(dice[0])) + bonus)
			elif args.b is not None:
				if len(dice) > 1:
					raise Exception("You can use only one type of die.")
				elif dice[0][1] < int(args.b):
					raise Exception("You can't pick out more dice than you roll.")

				rolls.append(sum(sorted(du.roll_batch(dice[0], sumup = False), reverse = True)[:int(args.b)]) + bonus)
			elif args.w is not None:
				if len(dice) > 1:
					raise Exception("You can use only one type of die.")
				elif dice[0][1] < int(args.w):
					raise Exception("You can't pick out more dice than you roll.")

				rolls.append(sum(sorted(du.roll_batch(dice[0], sumup = False))[:int(args.w)]) + bonus)
			elif args.crit is True:
				rolls.append(du.roll_all(dice) + du.roll_all(dice) + bonus)
			else:
				rolls.append(du.roll_all(dice) + bonus)

		for roll in rolls:
			print roll,
		print ""

except Exception as ex:
	print ex.args[0]