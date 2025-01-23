from z3 import Solver, BitVec, BitVecSort, Function, And, sat
import json

# Load the immediate length mapping (16-bit immediate values with lengths)
# Assume imms.json has a structure like {"0": [2, 3, ...], "1": [4, 5, ...]}.
imms = json.load(open('./imms-generator/solutions.json'))

# Convert the immediate mapping to handle 16-bit values
imms = {int(k): len(v) for k, v in imms.items()}

LONGEST_IMMEDIATE = max(imms.values())

# Z3 solver
solver = Solver()

# Function to compute instruction lengths based on immediates (16-bit values)
lengths_map = Function('lengths_map', BitVecSort(16), BitVecSort(16))

start_adress = 0x0000
# layout:
# single value: contigous block of instructions with label at the end
# double value: contigous block of instructions with jump at the end to index of label
problem_layout = [
    (1000,),
    (1000, 3),
    (1000, 0),
    (1000,),
]

max_imm_length = max(imms.values())
max_jump_length = 2*max_imm_length + 2

min_adress = start_adress
def calc_max_adress(layout):
    max_adress = 0
    for instr in layout:
        if len(instr) == 1:
            max_adress += instr[0]
        elif len(instr) == 2:
            max_adress += instr[0] + max_jump_length + 1
    return max_adress + 1

max_adress = start_adress+calc_max_adress(problem_layout) 

# Handle 16-bit immediates by combining the 8-bit high and low parts
for i in range(min_adress, max_adress):
    high = i >> 8
    low = i & 0xFF
    solver.add(lengths_map(i) == (imms[low] + imms[high] + 2))


# Number of instructions
num_instructions = len(problem_layout)
# Variables for instruction addresses and lengths
# adresses are the positions of the instructions in the program
addresses = [BitVec(f"address_{i}", 16) for i in range(num_instructions)]
# lengths are the lengths of the instructions
lengths = [BitVec(f"length_{i}", 16) for i in range(num_instructions)]
bufferNops = [BitVec(f"bufferNo_{i}", 16) for i in range(num_instructions)]


for i in range(num_instructions):
    solver.add(And(addresses[i] >= min_adress, addresses[i] < max_adress))

for i in range(num_instructions):
    solver.add(And(bufferNops[i] >= 0, bufferNops[i] <= 1))

label_positions = {}

# Iterate over the problem layout and set up constraints
for i, instr in enumerate(problem_layout):
    if len(instr) == 1: # instruction block
        length = instr[0]
        solver.add(lengths[i] == length)  # Fixed length
    elif len(instr) == 2: # instruction block with jump
        block_length, jump_label_idx = instr
        # lenght depends on lengths_map. we take the length depending on the adress of the jump

        solver.add(lengths[i] == (lengths_map(addresses[jump_label_idx]) + block_length + bufferNops[i]))
        label_positions[i] = jump_label_idx  # Store the label index for the jump
    else:
        raise ValueError(f"Unexpected instruction format at index {i}: {instr}")

# Set up constraints for sequential addresses
solver.add(addresses[0] == start_adress)  # Starting address at 0
for i in range(num_instructions - 1):
    # Ensure addresses are sequential based on instruction lengths
    solver.add(addresses[i + 1] == addresses[i] + lengths[i])

# Solve the constraints
if solver.check() == sat:
    model = solver.model()
    print("Solution Found:")

    for i in range(num_instructions):
        addr = model[addresses[i]]
        length = model[lengths[i]]
        buf = model[bufferNops[i]]
        if i in label_positions:
            jump_label_idx = label_positions[i]
            jump_addr = model[addresses[jump_label_idx]]
            print(f"Instruction {i}: Jump to address = {jump_addr}, Jump Len = {length.as_long()-problem_layout[i][0]}, buf={buf}, Length = {problem_layout[i][0]}, Len = {length}")
        else:
            print(f"Instruction {i}: Address = {addr}, Len = {length}")


else:
    print("No solution found")
