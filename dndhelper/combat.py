#!/usr/bin/env python

import argparse
import dice_util as du

parser = argparse.ArgumentParser(
    description='Simple attack roller for D&D 5th edition.')
parser.add_argument('attack_roll', help='Code for the attack roll, ex: 1d20+5')
parser.add_argument('damage_roll', help='Code for the damage roll, ex: 3d6+2')
parser.add_argument('target_ac', help='Target AC to hit, ex: 18')
parser.add_argument(
    '-c',
    help='number of times to repeat the attack',
    type=int)

parser.add_argument('-a', help='roll width advantage', action='store_true')
parser.add_argument('-d', help='roll width disadvantage', action='store_true')

args = parser.parse_args()

repeats = 1
if args.c is not None:
    if args.c >= 1:
        repeats = args.c

try:
    for i in range(repeats):
        target_ac = int(args.target_ac)

        attack_dice, attack_bonus = du.parse_roll_line(args.attack_roll)
        attack_result = du.roll_batch(attack_dice[0])
        if args.a:
            attack_result = max(attack_result, du.roll_batch(attack_dice[0]))
        elif args.d:
            attack_result = max(attack_result, du.roll_batch(attack_dice[0]))

        attack_roll = attack_result + attack_bonus
        print("Attack roll:     {} vs AC {}".format(attack_roll, target_ac))

        damage_dice, damage_bonus = du.parse_roll_line(args.damage_roll)
        damage = du.roll_all(damage_dice) + damage_bonus
        if attack_result == 20:
            damage += du.roll_all(damage_dice)

        if attack_result == 20:
            print("CRITICAL HIT!")
            print("Damage roll:     {}".format(damage))
        elif attack_result + attack_bonus >= target_ac:
            print("HIT!")
            print("Damage roll:     {}".format(damage))
        else:
            print("MISS!")

        if i < repeats - 1:
            print("----------------------------")

except Exception as ex:
    print(ex.args[0])
