#!/usr/bin/env python2

import random
import sys
from collections import OrderedDict
import argparse


class Generator(object):

    def __init__(self, name, content_map):
        self.name = name
        self.content_map = content_map

    def generate_sample(self):
        raise NotImplemented()


class UniformFileGenerator(Generator):

    def __init__(self, name, content_map, file_name):
        self.file_name = file_name

        super(UniformFileGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        gen_file = open(self.file_name, 'r')
        gen_list = []
        for line in gen_file.readlines():
            if len(line) >= 2:
                gen_list.append(line.strip())

        choice = random.choice(gen_list)
        # if isinstance(choice, str):
        #   choice = choice.decode('utf-8')
        return choice


class ValueGenerator(Generator):

    def __init__(self, name, content_map, value):
        self.value = value

        super(ValueGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        return self.value


class ProbabilityGenerator(Generator):

    def __init__(self, name, content_map, choices):
        self.choices = choices

        super(ProbabilityGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        return self.weighted_choice(self.choices).generate_sample()

    def weighted_choice(self, choices):
        total = sum(w for c, w in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w in choices:
            if upto + w > r:
                return c
            upto += w
        assert False, "Shouldn't get here"


class UniformProbabilityGenerator(Generator):

    def __init__(self, name, content_map, choices):
        self.choices = choices

        super(UniformProbabilityGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        return random.choice(self.choices).generate_sample()


class DependanceGenerator(Generator):

    def __init__(self, name, content_map, choices, dependancy_name):
        self.choices = choices
        self.dependancy_name = dependancy_name

        for i, choice in enumerate(self.choices):
            if choice[1] == "ANY":
                self.choices.append(self.choices.pop(i))

        super(DependanceGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        if self.dependancy_name not in self.content_map:
            return None

        for choice in self.choices:
            if choice[1] == self.content_map[
                    self.dependancy_name] or choice[1] == "ANY":
                return choice[0].generate_sample()

        return None


class MultipleWithoutReplacementGenerator(Generator):

    def __init__(self, name, content_map, gen_count, gen_provider):
        self.gen_count = gen_count
        self.gen_provider = gen_provider

        super(
            MultipleWithoutReplacementGenerator,
            self).__init__(
            name,
            content_map)

    def generate_sample(self):
        samples = []
        while len(samples) < self.gen_count:
            samples.append(self.gen_provider.generate_sample())
            samples = list(set(samples))

        return tuple(samples)


class InterfaceGenerator(Generator):

    def __init__(self, name, content_map, generator):
        self.generator = generator

        super(InterfaceGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        return self.generator.generate_sample()


class TemplateParser():

    def __init__(self):
        pass

    def parse_line(self, content_map, line):
        if len(line) > 4:
            var_name = line.split(':')[0]
            return self.parse_statement(
                var_name,
                content_map,
                line.split(':')[1])

        return None

    def parse_statement(self, var_name, content_map, statement):
        choice_generators = []
        conditional = ""
        l_statement = statement
        if statement.rfind('|') > statement.rfind(')'):
            conditional = statement[statement.rfind('|') + 1:].strip()
            l_statement = statement[:statement.rfind('|')].strip()

        choice_strings = []
        paren_accum = 0
        start_i = 0
        end_i = None

        for i in range(len(l_statement)):
            if l_statement[i] == '(':
                paren_accum += 1
            elif l_statement[i] == ')':
                paren_accum -= 1

            if paren_accum == 0 and l_statement[i] == ',':
                if start_i is None:
                    start_i = i
                else:
                    end_i = i
                    choice_strings.append(l_statement[start_i:end_i])

                    start_i = end_i + 1
                    end_i = None

        choice_strings.append(l_statement[start_i:].strip())
        for choice_string in choice_strings:
            choice_generators.append(
                self.parse_choice(
                    var_name,
                    content_map,
                    choice_string))

        if conditional == "":
            if isinstance(choice_generators[-1][1], float):
                return ProbabilityGenerator(
                    var_name,
                    content_map,
                    choice_generators)
            else:
                if len(choice_generators) == 1:
                    return InterfaceGenerator(
                        var_name, content_map, choice_generators[-1][0])
                else:
                    return UniformProbabilityGenerator(
                        var_name, content_map, [
                            x[0] for x in choice_generators])
        else:
            return DependanceGenerator(
                var_name,
                content_map,
                choice_generators,
                conditional)

        return None

    def parse_choice(self, var_name, content_map, choice_string):
        value = ""
        condition = ""
        if len(choice_string.split(')')) == 1:
            value = choice_string.split('-')[0].strip()
            if len(choice_string.split('-')) == 2:
                condition = choice_string.split('-')[1].strip()
        else:
            if choice_string.rfind('-') > choice_string.rfind(')'):
                value = choice_string[0:choice_string.rfind('-')].strip()
                condition = choice_string[
                    choice_string.rfind('-') +
                    1:].strip()
            else:
                value = choice_string.strip()

        if len(condition.split('.')) >= 2:
            condition = float(condition)

        multiplier = 1
        if value.find('*') != -1:
            try:
                multiplier = int(value[0:value.find('*')])
                value = value[value.find('*') + 1:].strip()
            except Exception:
                pass

        # return self.parse_literal(var_name, content_map, value), condition
        parsed_down_choice = None
        if value[0] == '(' and value[-1] == ')':
            parsed_down_choice = self.parse_statement(
                var_name,
                content_map,
                value[
                    1:-
                    1])
        else:
            parsed_down_choice = self.parse_literal(
                var_name,
                content_map,
                value)

        if multiplier == 1:
            return parsed_down_choice, condition
        else:
            return MultipleWithoutReplacementGenerator(
                var_name, content_map, multiplier,
                parsed_down_choice), condition

    def parse_literal(self, var_name, content_map, literal):
        if len(literal.split('.')) >= 2:
            return UniformFileGenerator(var_name, content_map, literal)
        else:
            return ValueGenerator(var_name, content_map, literal)


class AggregateGenerator(Generator):

    def __init__(self, name, content_map, template_file):
        template_parser = TemplateParser()
        self.generators = []
        self.name_sequence = []
        for line in template_file:
            self.generators.append(
                template_parser.parse_line(
                    content_map,
                    line))
            self.name_sequence.append(self.generators[-1].name)

        super(AggregateGenerator, self).__init__(name, content_map)

    def generate_sample(self):
        for generator in self.generators:
            content_map[generator.name] = generator.generate_sample()

        for generator in self.generators:
            if content_map[generator.name] is None:
                sample = generator.generate_sample()
                content_map[generator.name] = sample

        return self.name_sequence, self.content_map


def print_sample_aggregate(names, content_map):
    for i in range(len(names)):
        first_string_part = names[i] + str(":")
        first_string_part = first_string_part.decode('utf-8')
        while len(first_string_part) < 20:
            first_string_part = first_string_part + " "

        first_string_part = first_string_part.encode('utf-8')

        output_line = first_string_part

        if isinstance(
                content_map[
                    names[i]],
                str) or isinstance(
                content_map[
                    names[i]],
                unicode):
            output_line = output_line + content_map[names[i]]
        elif content_map[names[i]] is None:
            output_line = output_line + "NOT DEFINED"
        else:
            for item in content_map[names[i]][0:-1]:
                output_line = output_line + item + ", "

            output_line = output_line + content_map[names[i]][-1]
        print(output_line)


def save_sample_aggregate(log_file, names, content_map):
    for i in range(len(names)):
        first_string_part = names[i] + str(":")
        first_string_part = first_string_part.decode('utf-8')
        while len(first_string_part) < 20:
            first_string_part = first_string_part + " "

        first_string_part = first_string_part.encode('utf-8')
        output_line = first_string_part

        if isinstance(
                content_map[
                    names[i]],
                str) or isinstance(
                content_map[
                    names[i]],
                unicode):
            output_line = output_line + content_map[names[i]]
        elif content_map[names[i]] is None:
            output_line = output_line + "NOT DEFINED"
        else:
            for item in content_map[names[i]][0:-1]:
                output_line = output_line + item + ", "

            output_line = output_line + content_map[names[i]][-1]
        log_file.write(output_line + "\n")

parser = argparse.ArgumentParser(
    description='Generate object decsriptions by template.')
parser.add_argument('template_file')
parser.add_argument('-c', help='number of objects to generate', type=int)

args = parser.parse_args()

repeats = 1
if args.c is not None:
    if args.c >= 1:
        repeats = args.c

for i in range(repeats):
    template_file_name = args.template_file + ".txt"
    template_file = open(template_file_name, 'r')
    file_type = template_file.readline().strip()

    content_map = {}

    if file_type == "TEMPLATE":
        aggregate_generator = AggregateGenerator(
            "Generator",
            content_map,
            template_file)

        log_file = open(template_file_name + ".txt.log", 'a')
        name_sequence, content_map = aggregate_generator.generate_sample()
        print_sample_aggregate(name_sequence, content_map)
        save_sample_aggregate(log_file, name_sequence, content_map)

        log_file.write("\n")

        if i != repeats - 1:
            print("")
    else:
        template_file.close()
        ufg = UniformFileGenerator("UFG", content_map, template_file_name)
        print(ufg.generate_sample())
