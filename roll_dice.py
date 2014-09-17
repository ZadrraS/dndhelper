#!/usr/bin/env python

import argparse
import dice_util as du

class DiceArgumentException(Exception):
    pass

parser = argparse.ArgumentParser(description='Simple dice roller for D&D 5th edition.')
parser.add_argument('die_code', help='Code for the dice roll, ex.: 3d6+4-1d4-1', nargs='+')



formatting_group = parser.add_mutually_exclusive_group()
formatting_group.add_argument('-l', '--line_print', help='print repeated rolls in a line instead of a column', action = 'store_true')
formatting_group.add_argument('-v', '--verbose', help='print extra info when rolling multiple dice', action = 'store_true')

parser.add_argument('-c', '--count', help='number of times to repeat the roll', type = int)
parser.add_argument('-t', '--transpose', help='print all rolls of each die in a line instead of a column', action = 'store_true')



group = parser.add_mutually_exclusive_group()
group.add_argument('-a', '--advantage', help='roll width advantage (die_code has to be of the form 1d20{+-x})', action = 'store_true')
group.add_argument('-d', '--disadvantage', help='roll width disadvantage (die_code has to be of the form 1d20{+-x})', action = 'store_true')

group.add_argument('-crit', '--critical', help='roll critical hit damage', action = 'store_true')

group.add_argument('-b', '--best', help='only sum specified number of best rolls (can only include one die type in a roll)', type = int)
group.add_argument('-w', '--worst', help='only sum specified number of worst rolls (can only include one die type in a roll)', type = int)

args = parser.parse_args()

repeats = 1
if args.count is not None:
	if args.count >= 1:
		repeats = args.count

try:
	parsed_dice = []
	for die_code in args.die_code:
		die, bonus = du.parse_roll_line(die_code)
		parsed_dice.append((die, bonus))

	rolls = []
	for i in range(repeats):
		rolls.append([])
		for dice, bonus in parsed_dice:
			if len(dice) == 0:
				rolls[i].append(bonus)
			elif args.advantage:
				if dice[0][1] > 1 or dice[0][2] != 20:
					raise DiceArgumentException("Can only do a 1d20+x type of roll with advantage.")

				rolls[i].append(max(du.roll_batch(dice[0]), du.roll_batch(dice[0])) + bonus)
			elif args.disadvantage:
				if dice[0][1] > 1 or dice[0][2] != 20:
					raise DiceArgumentException("Can only do a 1d20+x type of roll with disadvantage.")

				rolls[i].append(max(du.roll_batch(dice[0]), du.roll_batch(dice[0])) + bonus)
			elif args.best is not None:
				if len(dice) > 1:
					raise DiceArgumentException("You can use only one type of die.")
				elif dice[0][1] < int(args.best):
					raise DiceArgumentException("You can't pick out more dice than you roll.")

				rolls[i].append(sum(sorted(du.roll_batch(dice[0], sumup = False), reverse = True)[:int(args.best)]) + bonus)
			elif args.worst is not None:
				if len(dice) > 1:
					raise DiceArgumentException("You can use only one type of die.")
				elif dice[0][1] < int(args.worst):
					raise DiceArgumentException("You can't pick out more dice than you roll.")

				rolls[i].append(sum(sorted(du.roll_batch(dice[0], sumup = False))[:int(args.worst)]) + bonus)
			elif args.critical is True:
				rolls[i].append(du.roll_all(dice) + du.roll_all(dice) + bonus)
			else:
				rolls[i].append(du.roll_all(dice) + bonus)

	if args.transpose:
		rolls = map(list, zip(*rolls))

	if args.verbose:
		dice_strings = []
		for dice, bonus in parsed_dice:
			output_string = ""
			if len(dice) > 0:
				output_string = output_string + str(dice[0][1]) + 'd' + str(dice[0][2])
				if len(dice) > 1:
					for die in dice[1:]:
						output_string = output_string + die[0] + str(die[1]) + 'd' + str(die[2])

				if bonus > 0:
					output_string = output_string + "+" + str(bonus)
				elif bonus < 0:
					output_string = output_string + "-" + str(bonus)
			else:
				output_string = output_string + str(bonus)

			dice_strings.append(output_string)

		number_strings = [str(num) for num in range(repeats)]

		if args.transpose:
			number_strings, dice_strings = dice_strings, number_strings

		max_die_line_len = 10
		for die_string in dice_strings:
			max_die_line_len = max(max_die_line_len, len(die_string) + 2)

		front_pad_length = 2
		for number_string in number_strings:
			front_pad_length = max(front_pad_length, len(number_string) + 1)

		output_line = " " * front_pad_length
		for die_string in dice_strings:
			output_string = "| " + die_string
			output_string = output_string + " " * (max_die_line_len - len(output_string))
			output_line = output_line + output_string

		output_line = output_line + "|"
		print output_line
		output_line = "-" * len(output_line)
		print output_line

		output_line = ""
		for i, roll in enumerate(rolls):
			output_line = str(number_strings[i])
			output_line = output_line + " " * (front_pad_length - len(str(number_strings[i])))

			for result in roll:
				output_string = "| " + str(result)
				output_string = output_string + " " * (max_die_line_len - len(output_string))
				output_line = output_line + output_string

			print output_line + "|"
	else:
		for roll in rolls:
			for result in roll:
				print result,
			if not args.line_print:
				print ""

except DiceArgumentException as ex:
	print ex.args[0]