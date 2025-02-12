import z3

# Define operation codes.
OP_ADDI = 0
OP_NAND = 1

def simulate_expr(instructions, init_state):
    """
    Returns a Z3 expression representing the final accumulator
    after running the given instructions starting from init_state.
    """
    acc = init_state
    for instr in instructions:
        if instr.startswith("addi"):
            imm = int(instr.split()[1])
            acc = (acc + imm) & 0xFF
        elif instr.startswith("nand"):
            acc = (~acc) & 0xFF
        else:
            raise ValueError(f"Unknown instruction: {instr}")
    return acc

def simulate_optimized_expr(ops, args, init_state, target_length):
    """
    Returns a Z3 expression representing the final accumulator
    after running the optimized program (represented by ops and args)
    starting from init_state.
    """
    acc = init_state
    for i in range(target_length):
        # For an addi, we add the argument; for nand, we perform bitwise NOT.
        acc = z3.If(ops[i] == OP_ADDI,
                    (acc + args[i]) & 0xFF,
                    z3.If(ops[i] == OP_NAND,
                          (~acc) & 0xFF,
                          acc))
    return acc

def optimize(instructions, target_length):
    BIT_WIDTH = 8

    s = z3.Solver()

    # Create a fresh quantified variable for initial state.
    x = z3.BitVec('x', BIT_WIDTH)

    # Build the original program's effect as an expression in x.
    original_expr = simulate_expr(instructions, x)

    # Create symbolic parameters for the optimized program.
    ops = [z3.Int(f'op_{i}') for i in range(target_length)]
    args = [z3.BitVec(f'arg_{i}', BIT_WIDTH) for i in range(target_length)]

    # For each operation, add the constraint that op must be either OP_ADDI or OP_NAND.
    # And if it is an addi, the immediate must be in the range [-8, 7].
    for i in range(target_length):
        s.add(z3.Or(ops[i] == OP_ADDI, ops[i] == OP_NAND))
        s.add(z3.Implies(ops[i] == OP_ADDI, z3.And(args[i] >= -8, args[i] <= 7)))
    
    # Build the optimized program's final state expression.
    optimized_expr = simulate_optimized_expr(ops, args, x, target_length)

    # Ensure that for all possible initial states x, the optimized program produces the same result as the original.
    s.add(z3.ForAll([x], optimized_expr == original_expr))

    # (Optional) Debug: print all constraints.
    print("\n=== Constraints ===")
    for c in s.assertions():
        print(c)

    # Check for a solution.
    if s.check() == z3.sat:
        model = s.model()
        optimized_instructions = []
        for i in range(target_length):
            op_val = model[ops[i]].as_long()
            if op_val == OP_ADDI:
                imm_val = model[args[i]].as_long()
                optimized_instructions.append(f"addi {imm_val}")
            elif op_val == OP_NAND:
                optimized_instructions.append("nand")
            else:
                raise ValueError(f"Unknown op: {op_val}")
        return optimized_instructions
    else:
        return None  # No valid sequence found.

if __name__ == "__main__":
    # Example 1: a sequence that should be optimizable (e.g., three addi 1's to one addi 3)
    instructions = ["addi 1", "addi 1", "addi 1"]
    target_length = 1
    optimized = optimize(instructions, target_length)
    print("\nOptimized Instructions:", optimized)

    # Example 2: a sequence that is not optimizable in 1 instruction.
    instructions = ["addi 2", "addi 2", "addi 5"]
    target_length = 1
    optimized = optimize(instructions, target_length)
    print("\nOptimized Instructions:", optimized)