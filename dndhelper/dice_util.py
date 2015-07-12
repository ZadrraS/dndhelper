import random
import sys
import argparse
import re


def roll_batch(die_params, sumup=True):
    op_type, die_count, die_type = die_params

    roll_results = [random.randint(1, die_type) for i in range(die_count)]
    for i in range(len(roll_results)):
        if op_type == '-':
            roll_results[i] = -roll_results[i]

    if sumup:
        return sum(roll_results)
    else:
        return roll_results


def roll_all(die_param_list, sumup=True):
    roll_results = [roll_batch(die_params, sumup=True)
                    for die_params in die_param_list]
    if sumup:
        return sum(roll_results)
    else:
        return roll_results


def parse_dice_code(die_code):
    die_count = die_code.split('d')[0]
    if die_count == '':
        die_count = 1
    else:
        die_count = int(die_count)

    die_type = int(die_code.split('d')[1])

    return die_count, die_type


def parse_roll_line(roll_line):
    bonus = 0
    dice = []

    roll_chunks = re.split('([\+\-])', roll_line)

    op_type = '+'
    for chunk in roll_chunks:
        if chunk == '+':
            op_type = '+'
        elif chunk == '-':
            op_type = '-'
        else:
            if 'd' not in chunk:  # This is a regular number
                if op_type == '-':
                    bonus -= int(chunk)
                else:
                    bonus += int(chunk)
            else:  # This is a dice roll
                die_count, die_type = parse_dice_code(chunk)
                dice.append((op_type, die_count, die_type))

    return dice, bonus
