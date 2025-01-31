from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
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
        OP_LDA0  = 3
        OP_SEG = 4

        # Define an array to hold intermediate results
        intermediate = [z3.BitVec(f'intermediate_{i}', BIT_WIDTH) for i in range(num_operations + 1)]
        intermediate_seg = [z3.BitVec(f'intermediate_seg_{i}', BIT_WIDTH) for i in range(num_operations + 1)]

        # Introduce an "initialized" flag that tracks if intermediate[0] has been explicitly set
        initialized = [z3.Bool(f'initialized_{i}') for i in range(num_operations + 1)]
        initialized_seg = [z3.Bool(f'initialized_seg_{i}') for i in range(num_operations + 1)]

        # Initially, intermediate[0] is "uninitialized" and cannot be used
        s.add(initialized[0] == z3.BoolVal(False))
        s.add(initialized_seg[0] == z3.BoolVal(False))

        # Constraints for each operation
        for i in range(num_operations):
            op = z3.Select(operations, i)  # Get the operation at index i
            imm = z3.BitVec(f'imm_{i}', BIT_WIDTH)  # Immediate value for addition
            s.add(imm >= -8, imm <= 7)  # Immediate value constraint    

            acc_ininitialized = initialized[i]
            seg_initialized = initialized_seg[i]

            # Apply the operation based on its type
            cond_add = z3.And(op == OP_ADD, acc_ininitialized, intermediate[i + 1] == (intermediate[i] + imm) & 0xFF, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_shift = z3.And(op == OP_SHIFT, acc_ininitialized, intermediate[i + 1] == (intermediate[i] << 1) & 0xFF, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_neg = z3.And(op == OP_NEG, acc_ininitialized, intermediate[i + 1] == ~intermediate[i] & 0xFF, intermediate_seg[i + 1] == intermediate_seg[i])
            cond_lda0 = z3.And(op == OP_LDA0, intermediate[i + 1] == 0, intermediate_seg[i + 1] == intermediate_seg[i], initialized[i + 1] == z3.BoolVal(True))
            cond_seg = z3.And(op == OP_SEG, 
                              acc_ininitialized,
                              intermediate_seg[i + 1] == intermediate[i], 
                              intermediate[i + 1] == intermediate[i], 
                              initialized_seg[i + 1] == z3.BoolVal(True)
                              )

            # Ensure exactly one operation applies
            s.add(z3.Or(cond_add, cond_shift, cond_neg, cond_lda0, cond_seg))

            s.add(initialized[i + 1] == z3.Or(initialized[i], op == OP_LDA0))
            s.add(initialized_seg[i + 1] == z3.Or(initialized_seg[i], op == OP_SEG))

        # The last intermediate value must match the target
        s.add(intermediate[-1] == target_low)
        s.add(intermediate_seg[-1] == target_high)
        s.add(initialized[-1] == z3.BoolVal(True))
        s.add(initialized_seg[-1] == z3.BoolVal(True))

        # Solve the constraints
        if s.check() == z3.sat:
            model = s.model()

            buffer = []
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


def process_target(target):
    solution = find_number_shifts(target)
    return (str(target), solution) if solution else None

def main():
    solutions = dict()
    UPPER_BOUND = 2**16
    # Using ThreadPoolExecutor to parallelize
    with ProcessPoolExecutor() as executor:
        results = list(tqdm.tqdm(
            executor.map(process_target, range(0, UPPER_BOUND)),
            total=UPPER_BOUND,
            smoothing=0.05,
        ))

    # Collect non-None results into the solutions dictionary
    for result in results:
        if result:
            solutions[result[0]] = result[1]

    return solutions

if __name__ == "__main__":
    final_solutions = main()
    import json
    json.dump(final_solutions, open("solutions.json", "w"), indent=2)
