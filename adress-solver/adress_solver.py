from z3 import Solver, BitVec, BitVecSort, BitVecVal, Function, And, sat
import json
from dataclasses import dataclass, field
from typing import Optional

imms = json.load(open('./imms-generator/solutions-16bit.json'))
imms = {int(k): len(v) for k, v in imms.items()}

LONGEST_IMMEDIATE = max(imms.values())
SHORT_IMMEDIATE = min(imms.values())
MAX_JUMP_LENGHT = LONGEST_IMMEDIATE + 2
MIN_JUMP_LENGHT = SHORT_IMMEDIATE + 2

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
        solver.add(lengths_map(i) == (imms[i] + 2))

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

def solve_adresses(program, starting_adress, timeout=2000):
    solution = try_solve_adresses(program, starting_adress, buffer=1, timeout=timeout)
    if solution:
        return solution
    for i in range(1, 5):
        solution = try_solve_adresses(program, starting_adress, buffer=i, timeout=timeout)
        if solution:
            return solution
    else:
        return try_solve_adresses(program, starting_adress, buffer=14, timeout=None)


if __name__ == "__main__":
    # generate long program
    import random

    size = 20
    program = []
    for i in range(size):
        if random.random() < 0.5:
            program.append((20, ))
        else:
            program.append((20, random.randint(i-2, i+2)))
    
    jumps = sum(1 for instr in program if len(instr) == 2)
    print(jumps)

    starting_adress = 0
    solution = try_solve_adresses(program, starting_adress, buffer=1, timeout=None)

    if solution:
        print("Solution Found:")
        for section in solution:
            print(section)
    else:
        print("No solution found")