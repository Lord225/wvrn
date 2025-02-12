import z3

# Define operation codes.
OP_ADDI = 0
OP_NAND = 1
BIT_WIDTH = 8

def simulate_cpu_array(instructions, init_state, s, prefix):
    n = len(instructions)
    states = [z3.BitVec(f'{prefix}_{i}', BIT_WIDTH) for i in range(n + 1)]
    # The initial state is set from the given parameter.
    s.add(states[0] == init_state)
    
    # Add constraints that simulate each instruction.
    for i, instr in enumerate(instructions):
        if instr.startswith("addi"):
            imm = int(instr.split()[1])
            s.add(states[i + 1] == (states[i] + imm) & 0xFF)
        elif instr.startswith("nand"):
            s.add(states[i + 1] == (~states[i]) & 0xFF)
        else:
            raise ValueError(f"Unknown instruction: {instr}")
    
    return states

def simulate_optimized_cpu(ops, args, init_state, s, target_length):
    states = [z3.BitVec(f'opt_state_{i}', BIT_WIDTH) for i in range(target_length + 1)]
    s.add(states[0] == init_state)
    
    for i in range(target_length):
        # Transition from state[i] to state[i+1]
        s.add(states[i+1] == 
              z3.If(ops[i] == OP_ADDI,
                    (states[i] + args[i]) & 0xFF,
                    z3.If(ops[i] == OP_NAND,
                          (~states[i]) & 0xFF,
                          states[i])))
    return states

def optimize(instructions, target_length):
    s = z3.Solver()

    # Create a fresh quantified variable for the initial state.
    # This 'x' will serve as the (arbitrary) starting value for the CPU.
    x = z3.BitVec('x', BIT_WIDTH)

    # Build the original program's state array.
    original_states = simulate_cpu_array(instructions, x, s, prefix="orig")
    # Build symbolic parameters for the optimized program.
    ops = [z3.Int(f'op_{i}') for i in range(target_length)]
    args = [z3.BitVec(f'arg_{i}', BIT_WIDTH) for i in range(target_length)]
    
    # For each optimized instruction, constrain the operation code and (if addi) the immediate.
    for i in range(target_length):
        # The op must be either ADDI or NAND.
        s.add(z3.Or(ops[i] == OP_ADDI, ops[i] == OP_NAND))
        # If it's an addi, the immediate must be between -8 and 7.
        s.add(z3.Implies(ops[i] == OP_ADDI, z3.And(args[i] >= -8, args[i] <= 7)))
    
    # Build the optimized program's state array.
    optimized_states = simulate_optimized_cpu(ops, args, x, s, target_length)
    
    # Enforce that for all possible initial states x, the final states agree.
    s.add(z3.ForAll([x], optimized_states[-1] == original_states[-1]))
    
    
    # (Optional) Print all constraints (for debugging)
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
    # Example 1: a sequence that should be optimizable (three addi 1's -> addi 3)
    instructions = ["addi 1", "addi 1", "addi 1"]
    target_length = 1
    optimized = optimize(instructions, target_length)
    print("\nOptimized Instructions for example 1:", optimized)

    # Example 2: a sequence that is not optimizable in 1 instruction.
    instructions = ["addi 2", "addi 2", "addi 5"]
    target_length = 1
    optimized = optimize(instructions, target_length)
    print("\nOptimized Instructions for example 2:", optimized)
