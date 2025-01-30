from dataclasses import dataclass, field
import logging
import pprint
from typing import Optional
from core.context import Context
import core.parse.tokenize as tokenize
import core.error as error
import core.config as config 
from z3 import Solver, BitVec, BitVecSort, BitVecVal, Function, And, sat
import json

from core.load.base import Line

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
    if len(program) > 0:
        for label in labels:
            if label not in label_segments:
                next_index = max(label_segments.values()) + 1
                label_segments[label] = next_index
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

@dataclass
class ProblemSegmentLabels:
    length: int
    segment_id: int
    jump_label: Optional[int] = None

@dataclass
class ProblemSegmentIndexes:
    length: int
    segment_id: int
    jump_index: Optional[int] = None


def create_problem_layout(program, segment_lengths, label_segments) -> list[ProblemSegmentLabels]:
    problem = []
    current_segment = max(segment_lengths.keys())
    for i, line in enumerate(program):
        if current_segment != line.segment:
            if line.mached_command[0] in BRC_COMMANDS:
                addr = line.mached_command[1]["addr"]
                problem.append(
                    ProblemSegmentLabels(
                        length=segment_lengths[current_segment],
                        segment_id=current_segment,
                        jump_label=label_segments[addr],
                    )
                )
            else:
                problem.append(
                    ProblemSegmentLabels(
                        length=segment_lengths[current_segment],
                        segment_id=current_segment,
                    )
                )
            current_segment = line.segment

    if line.mached_command[0] in BRC_COMMANDS:
        addr = line.mached_command[1]["addr"]
        problem.append(
            ProblemSegmentLabels(
                length=segment_lengths[current_segment],
                segment_id=current_segment,
                jump_label=label_segments[addr],
            )
        )
    else:
        problem.append(
            ProblemSegmentLabels(
                length=segment_lengths[current_segment],
                segment_id=current_segment,
            )
        )

    return problem


def translate_problem_layout(problem: list[ProblemSegmentLabels]) -> list[ProblemSegmentIndexes]:
    translated_problem = []
    for instr in problem:
        if instr.jump_label is None:
            translated_problem.append(
                ProblemSegmentIndexes(
                    length=instr.length,
                    segment_id=instr.segment_id
                )
            )
        else:
            translated_problem.append(
                ProblemSegmentIndexes(
                    length=instr.length,
                    segment_id=instr.segment_id,
                    jump_index=next(
                        i for i, p in enumerate(problem) if p.segment_id == instr.jump_label
                    )
                )
            )
    return translated_problem


imms = json.load(open('./rawrsembler/wvrn/solutions-16bit.json'))
imms =  {int(k): v for k, v in imms.items()}
imms_lens = {int(k): len(v) for k, v in imms.items()}

LONGEST_IMMEDIATE = max(imms_lens.values())
SHORT_IMMEDIATE = min(imms_lens.values())
MAX_JUMP_LENGHT = LONGEST_IMMEDIATE + 1
MIN_JUMP_LENGHT = SHORT_IMMEDIATE + 1

@dataclass
class SolutionSection:
    # starting adress of this section
    address: int
    # lenght of this section in bytes (including jumps and buffer)
    length: int
    # padding nops to make problem solvable
    buffer: int
    # physical adress of the jump target
    jump_to: Optional[int] = field(default=None)
    # lenght of the jump instruction alone (without buffer and other instructions)
    # basically lenght of 16 bit imm + 1 
    jump_lenght: Optional[int] = field(default=None)

def try_solve_adresses(problem: list[ProblemSegmentIndexes], starting_adress, buffer, timeout) -> list[SolutionSection] | None:
    def calc_max_adress(layout: list[ProblemSegmentIndexes]):
        max_adress = 0
        for instr in layout:
            if instr.jump_index is None:
                max_adress += instr.length
            else:
                max_adress += instr.length + MAX_JUMP_LENGHT
        return max_adress + 1
    
    min_adress = starting_adress
    max_adress = starting_adress+calc_max_adress(problem)

    solver = Solver()
    solver.set("smt.phase_selection", 5)

    # this function maps jumps immediates to their respective lengths in bytecode
    lengths_map = Function('lengths_map', BitVecSort(16), BitVecSort(16))

    for i in range(min_adress, max_adress):
        solver.add(lengths_map(i) == (imms_lens[i] + 1))

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
        if instr.jump_index is None:
            current_adress += instr.length
        else:
            current_adress += instr.length + MAX_JUMP_LENGHT
    
    # set lower low bound for adresses
    current_adress = starting_adress
    for i, instr in enumerate(problem):
        solver.add(addresses[i] >= current_adress)
        #print(f"Instruction {i} has adress atmost {current_adress}")
        if instr.jump_index is None:
            current_adress += instr.length
        else:
            current_adress += instr.length + MIN_JUMP_LENGHT    

    for i in range(num_sectors):
        solver.add(And(bufferNops[i] >= 0, bufferNops[i] <= buffer))

    label_positions = {}

    for i, instr in enumerate(problem):
        if instr.jump_index is None:  # instruction block
            solver.add(lengths[i] == instr.length)  # Fixed length
        else:  # instruction block with jump
            solver.add(lengths[i] == (lengths_map(addresses[instr.jump_index]) + instr.length + bufferNops[i])) # type: ignore
            label_positions[i] = instr.jump_index  # Store the label index for the jump
            
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
                jump_lenght = length-problem[i].length - buffer

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
    logging.debug(f"Resolving adresses for program with {len(problem)} sections, timeout: {timeout}, starting adress: {starting_adress}")
    solution = try_solve_adresses(problem, starting_adress, buffer=1, timeout=timeout)
    if solution:
        return solution
    for i in range(2, 5):
        logging.debug(f"Trying with buffer {i}, timeout: {timeout}")
        solution = try_solve_adresses(problem, starting_adress, buffer=i, timeout=timeout)
        if solution:
            return solution
    else:
        logging.debug(f"No solution found, retrying with buffer 14 and no timeout")
        return try_solve_adresses(problem, starting_adress, buffer=14, timeout=None)



def get_jump_sequence(target, brc_instruction: Line):
    if target < 0 or target >= 2**16:
        raise error.CompilerError(None, f"Invalid jump target: {target}")
    
    if brc_instruction.mached_command[0] not in BRC_COMMANDS:
        raise error.CompilerError(None, "Logic error: Jumps solution is in par with problem")
    
    cond = brc_instruction.tokenized[1]

    jump_command = f"bt {cond}"
    
    imm_load = imms[target]

    return imm_load + [jump_command]
    

def find_physical_adresses(program, solution: list[SolutionSection], context: Context):
    program_index = 0
    new_program = []
    fill = str(context.get_profile().fill)
    for section in solution:
        start_adress = section.address
        current_adress = start_adress 
        lenght = section.length
        buffer = section.buffer
        jump_len = section.jump_lenght if section.jump_lenght else 0

        for _ in range(start_adress, start_adress+lenght-jump_len-buffer):
            line = program[program_index]
            line["physical_adress"] = current_adress
            program_index += 1
            current_adress += 1
            new_program.append(line)

        if jump_len:
            jump_instruction = program[program_index]
            
            if jump_instruction.mached_command[0] not in BRC_COMMANDS:
                raise error.CompilerError(None, "Logic error: Jumps solution is in par with problem")
            
            jump_seq = get_jump_sequence(section.jump_to, jump_instruction)

            if len(jump_seq) != jump_len:
                raise error.CompilerError(None, "Logic error: Jump sequence lenght does not match jump lenght")

            for instr in jump_seq:
                new_program.append(Line(line_index_in_file=jump_instruction.line_index_in_file, line=instr, physical_adress=current_adress))
                current_adress += 1

        for _ in range(buffer):
            new_program.append(Line(line_index_in_file=None, line=fill, physical_adress=current_adress))
            current_adress += 1

    return new_program, context

def get_used_adresses(program):
    used_adresses = {}
    for line in program:
        used_adresses[line.physical_adress] = line
    return used_adresses

def find_label_physical_adresses(program, solution, label_segments):
    # crate dict of labels that has its physical adress in it
    label_adresses = dict()

    def find_key_by_value(value, dictionary):
        return [k for k, v in dictionary.items() if v == value]
    # todo
    return label_adresses
    

        
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

    starting_adress = 0
    solution = find_adresses(translated_problem, starting_adress)

    if solution:
        logging.debug(f"Solution found:")
        for i, section in enumerate(solution):
            logging.debug(f"Section {i}: {section}")
        context.solved_sections = solution
        program, context = find_physical_adresses(program, solution, context)

        context.used_addresses = get_used_adresses(program)
        context.physical_adresses = find_label_physical_adresses(program, solution, label_segments)

        return program, context
    else:
        logging.debug(f"No solution found")
        raise error.CompilerError(None, "No solution found - you can add nop instructions to make the problem solveable, You can increase the buffer size or increase the timeout or turn off adress optimization")
    

