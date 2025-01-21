import z3

def find_number_shifts(target: int):
    target_low = target & 0xFF
    target_high = target >> 8
    for i in range(1, 16):
        # Define the bit-width for 8-bit numbers
        BIT_WIDTH = 8
        
        # Define the array of operations
        num_operations = i  # Maximum number of operations
        operations = z3.Array('operations', z3.IntSort(), z3.IntSort())
        
        # Solver instance
        s = z3.Solver()

        # Define operation constants
        OP_ADD = 0
        OP_SHIFT = 1
        OP_NEG = 2
        OP_LDA0 = 3
        OP_SEG = 4

        # Define an array to hold intermediate results
        intermediate = [z3.BitVec(f'intermediate_{i}', BIT_WIDTH) for i in range(num_operations + 1)]
        intermediate_seg = [z3.BitVec(f'intermediate_seg_{i}', BIT_WIDTH) for i in range(num_operations + 1)]

        # The first intermediate value is the initial accumulator
        s.add(intermediate[0] == 0)
        s.add(intermediate_seg[0] == 0)

        # Constraints for each operation
        for i in range(num_operations):
            op = z3.Select(operations, i)  # Get the operation at index i
            imm = z3.BitVec(f'imm_{i}', BIT_WIDTH)  # Immediate value for addition
            s.add(imm >= -8, imm <= 7)  # Immediate value constraint
            
            # Apply the operation based on its type
            cond_add = z3.And(op == OP_ADD, intermediate[i + 1] == (intermediate[i] + imm) & 0xFF, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_shift = z3.And(op == OP_SHIFT, intermediate[i + 1] == (intermediate[i] << 1) & 0xFF, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_neg = z3.And(op == OP_NEG, intermediate[i + 1] == ~intermediate[i] & 0xFF, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_lda0 = z3.And(op == OP_LDA0, intermediate[i + 1] == 0, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_seg = z3.And(op == OP_SEG, intermediate_seg[i + 1] == intermediate[i], intermediate[i + 1] == intermediate[i])

            # Ensure exactly one operation applies
            s.add(z3.Or(cond_add, cond_shift, cond_neg, cond_lda0, cond_seg))

        # The last intermediate value must match the target
        s.add(intermediate[-1] == target_low)
        s.add(intermediate_seg[-1] == target_high)

        # Solve the constraints
        if s.check() == z3.sat:
            model = s.model()

            buffer = ['lda 0']
            for i in range(num_operations):
                op = model.eval(z3.Select(operations, i)).as_long()
                if op == OP_ADD:
                    imm = model.eval(z3.BitVec(f'imm_{i}', BIT_WIDTH)).as_long()
                    if imm >= 8:
                        buffer.append(f"addi {imm-256}")
                    else:
                        buffer.append(f"addi {imm}")
                elif op == OP_SHIFT:
                    buffer.append("add acc")
                elif op == OP_NEG:
                    buffer.append("nand acc")
                elif op == OP_LDA0:
                    buffer.append("lda 0")
                elif op == OP_SEG:
                    buffer.append("sta seg")
            return buffer
    else:
        print(f"Target {target} not reachable with {num_operations} operations")
import tqdm 


z3.set_param('parallel.enable', True)

solutions = dict()

for target in tqdm.tqdm(range(0, 2**16)):
    solution = find_number_shifts(target)
    if solution:
        solutions[str(target)] = solution

import json
json.dump(solutions, open("solutions.json", "w"), indent=2)
