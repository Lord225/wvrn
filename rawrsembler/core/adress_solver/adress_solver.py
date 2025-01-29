from dataclasses import dataclass, field
import logging
from typing import Optional
from core.context import Context
import core.parse.tokenize as tokenize
import core.error as error
import core.config as config 
from z3 import Solver, BitVec, BitVecSort, BitVecVal, Function, And, sat
import json

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
        return [k for k, v in dictionary.items() if v == value]

    labels = context.labels
    label_segments = {}
    for i, line in enumerate(program):
        if i in labels.values():
            for label in find_key_by_value(i, labels):
                label_segments[label] = line.segment
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


imms = json.load(open('./rawrsembler/wvrn/solutions-16bit.json'))
imms = {int(k): len(v) for k, v in imms.items()}

LONGEST_IMMEDIATE = max(imms.values())
SHORT_IMMEDIATE = min(imms.values())
MAX_JUMP_LENGHT = LONGEST_IMMEDIATE + 1
MIN_JUMP_LENGHT = SHORT_IMMEDIATE + 1

def transform_program_into_instruction_sections(program):
    return [
        (1000,  ),
        (1000, 3),
        (1000, 0),
        (1000,  ),
    ]

@dataclass
class SolutionSection:
    address: int
    length: int
    buffer: int
    jump_to: Optional[int] = field(default=None)
    jump_lenght: Optional[int] = field(default=None)

def try_solve_adresses(problem, starting_adress, buffer, timeout) -> list[SolutionSection] | None:
    def calc_max_adress(layout):
        max_adress = 0
        for instr in layout:
            if len(instr) == 1:
                max_adress += instr[0]
            elif len(instr) == 2:
                max_adress += instr[0] + MAX_JUMP_LENGHT
        return max_adress + 1
    
    min_adress = starting_adress
    max_adress = starting_adress+calc_max_adress(problem)

    solver = Solver()
    solver.set("smt.phase_selection", 5)

    # this function maps jumps immediates to their respective lengths in bytecode
    lengths_map = Function('lengths_map', BitVecSort(16), BitVecSort(16))

    for i in range(min_adress, max_adress):
        solver.add(lengths_map(i) == (imms[i] + 1))

    num_sectors = len(problem)

    # adresses are the positions of the instructions in the program
    addresses  = [BitVec(f"address_{i}", 16) for i in range(num_sectors)]
    # lengths are the lengths of the instructions
    lengths    = [BitVec(f"length_{i}", 16) for i in range(num_sectors)]
    # bufferNops are the number of nops added to make all problems solveable
    bufferNops = [BitVec(f"bufferNo_{i}", 16) for i in range(num_sectors)]

    for i in range(num_sectors):
         solver.add(And(addresses[i] >= min_adress, addresses[i] < max_adress))

    # set lower up bound for adresses
    current_adress = starting_adress
    for i, instr in enumerate(problem):
        solver.add(addresses[i] <= current_adress)
        #print(f"Instruction {i} has adress atleast {current_adress}")  
        if len(instr) == 1:
            current_adress += instr[0]
        elif len(instr) == 2:
            current_adress += instr[0] + MAX_JUMP_LENGHT
    
    # set lower low bound for adresses
    current_adress = starting_adress
    for i, instr in enumerate(problem):
        solver.add(addresses[i] >= current_adress)
        #print(f"Instruction {i} has adress atmost {current_adress}")
        if len(instr) == 1:
            current_adress += instr[0]
        elif len(instr) == 2:
            current_adress += instr[0] + MIN_JUMP_LENGHT    

    for i in range(num_sectors):
        solver.add(And(bufferNops[i] >= 0, bufferNops[i] <= buffer))

    label_positions = {}

    for i, instr in enumerate(problem):
        match len(instr):
            case 1:  # instruction block
                length = instr[0]
                solver.add(lengths[i] == length)  # Fixed length
            case 2:  # instruction block with jump
                block_length, jump_label_idx = instr
                solver.add(lengths[i] == (lengths_map(addresses[jump_label_idx]) + block_length + bufferNops[i]))
                label_positions[i] = jump_label_idx  # Store the label index for the jump
            case 3:  # instruction block with prespecified jump adress
                block_length, _, jump_adress = instr
                solver.add(lengths[i] == (lengths_map(jump_adress) + block_length + bufferNops[i]))
            case _:
                raise ValueError(f"Unexpected instruction format at index {i}: {instr}")
            
    solver.add(addresses[0] == starting_adress)
    for i in range(num_sectors - 1):
        solver.add(addresses[i + 1] == addresses[i] + lengths[i])

    if timeout:
        solver.set(timeout=timeout) 
    if solver.check() == sat:
        model = solver.model()        
        solution = [] # type: list[SolutionSection]
        for i in range(num_sectors):
            addres = model[addresses[i]].as_long() # type: ignore
            length = model[lengths[i]].as_long() # type: ignore
            buffer = model[bufferNops[i]].as_long() # type: ignore
            if i in label_positions:
                jump_label_idx = label_positions[i]
                jump_addr = model[addresses[jump_label_idx]].as_long() # type: ignore
                jump_lenght = length-problem[i][0]

                section = SolutionSection(
                    address=addres,
                    length=length,
                    buffer=buffer,
                    jump_to=jump_addr,
                    jump_lenght=jump_lenght,
                )
            else:
                section = SolutionSection(
                    address=addres,
                    length=length,
                    buffer=buffer
                )
            
            solution.append(section)

        return solution
    else:
        return None

def find_adresses(problem, starting_adress, timeout=2000):
    logging.debug(f"Finding adresses for program with {len(problem)} instructions timeout: {timeout}, starting adress: {starting_adress}")
    solution = try_solve_adresses(problem, starting_adress, buffer=1, timeout=timeout)
    if solution:
        return solution
    for i in range(1, 5):
        logging.debug(f"Trying with buffer {i}, timeout: {timeout}")
        solution = try_solve_adresses(problem, starting_adress, buffer=i, timeout=timeout)
        if solution:
            return solution
    else:
        logging.debug(f"No solution found, retrying with buffer 14 and no timeout")
        return try_solve_adresses(problem, starting_adress, buffer=14, timeout=None)


def apply_phisical_adresses_to_program(program, solution: list[SolutionSection], context: Context):
    pass
        
def solve_adresses(program, context: Context):
    program, context = mark_code_segments(program, context)
    label_segments = calculate_label_segments(program, context)
    segment_lengths = calculate_segment_lengths(program)
    problem = create_problem_layout(program, segment_lengths, label_segments)
    translated_problem = translate_problem_layout(problem)

    logging.debug(f"segment_lengths: {segment_lengths}")
    logging.debug(f"label_segments: {label_segments}")
    logging.debug(f"problem: {problem}")
    logging.debug(f"translated problem: {translated_problem}")

    starting_adress = 1000
    solution = find_adresses(translated_problem, starting_adress)

    if solution:
        logging.debug(f"Solution found:")
        for i, section in enumerate(solution):
            logging.debug(f"Section {i}: {section}")
        context.solved_sections = solution
    else:
        logging.debug(f"No solution found")
        raise error.CompilerError(None, "No solution found - you can add nop instructions to make the problem solveable, You can increase the buffer size or increase the timeout or turn off adress optimization")
    
    return program, context

