import unittest
from core.context import Context
import core.parse.tokenize as tokenize
import core.error as error
import core.config as config


BRC_COMMANDS = [
    "brc carry",
    "brc ncarry",
    "brc zero",
    "brc nzero",
    "brc odd",
    "brc nodd",
    "brc even",
    "brc neven",
    "brc sign",
    "brc nsign",
    "brc overflow",
    "brc noverflow",
    "brc true",
    "brc false",
]


def mark_code_segments(program, context):
    segment_id = 0

    labels = context.labels.values()  # dict of indexes of labels
    labels = [-len(program) + i for i in labels]

    for i in range(len(program)):
        line = program[-i - 1]

        line["segment"] = segment_id

        if line.mached_command[0] in BRC_COMMANDS or -i - 1 in labels:
            segment_id += 1

    return program, context


def calculate_label_segments(program, context):
    def find_key_by_value(value, dictionary):
        for k, v in dictionary.items():
            if v == value:
                return k

    labels = context.labels
    label_segments = {}
    for i, line in enumerate(program):
        if i in labels.values():
            label_segments[find_key_by_value(i, labels)] = line.segment
    return label_segments


def calculate_segment_lengths(program):
    segment_lengths = {}
    current_segment = 0
    current_length = 0
    for i, line in enumerate(program):
        if line.segment != current_segment:
            segment_lengths[current_segment] = current_length
            current_segment = line.segment
            current_length = 0
        current_length += 1
    segment_lengths[current_segment] = current_length
    return segment_lengths


def create_problem_layout(program, segment_lengths, label_segments):
    problem = []
    current_segment = max(segment_lengths.keys())
    for i, line in enumerate(program):
        if current_segment != line.segment:
            if line.mached_command[0] in BRC_COMMANDS:
                addr = line.mached_command[1]["addr"]
                problem.append(
                    (
                        segment_lengths[current_segment],
                        current_segment,
                        label_segments[addr],
                    )
                )
            else:
                problem.append(
                    (
                        segment_lengths[current_segment],
                        current_segment,
                    )
                )
            current_segment = line.segment
    # append last
    if line.mached_command[0] in BRC_COMMANDS:
        addr = line.mached_command[1]["addr"]
        problem.append(
            (segment_lengths[current_segment], current_segment, label_segments[addr])
        )
    else:
        problem.append(
            (
                segment_lengths[current_segment],
                current_segment,
            )
        )

    return problem


def translate_problem_layout(problem):
    def find_section_by_id(id):
        for i, p in enumerate(problem):
            if p[1] == id:
                return i

    translated_problem = []
    for i, instr in enumerate(problem):
        if len(instr) == 2:
            translated_problem.append((instr[0],))
        elif len(instr) == 3:
            translated_problem.append((instr[0], find_section_by_id(instr[2])))
    return translated_problem


def solve_adresses(program, context: Context):
    program, context = mark_code_segments(program, context)
    label_segments = calculate_label_segments(program, context)
    segment_lengths = calculate_segment_lengths(program)
    problem = create_problem_layout(program, segment_lengths, label_segments)
    translated_problem = translate_problem_layout(problem)

    print(label_segments)
    print(segment_lengths)
    print(problem)
    print(translated_problem)

    return program, context

