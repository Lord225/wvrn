from core.context import Context
import core.parse.tokenize as tokenize
import core.error as error
import core.config as config

def find_closest_command(program, debug_command):
    distances = [(i, program_line.line_index_in_file-debug_command.line_index_in_file) for i, program_line in enumerate(program)]
    min_distance = min(abs(distance) for _, distance in distances)
    best = [item for item in distances if abs(item[1]) == min_distance]

    # if distance is positive, return closest with higher index
    # if distance is negative, return closest with lower index 
    if debug_command.line_index_in_file < program[best[0][0]].line_index_in_file:
        return best[0][0], best[0][1]
    else:
        return best[-1][0], best[-1][1]


def tokenize_debug_comman(debug):
    _, _, *args = tokenize.remove_meaningless_tokens_list(tokenize.tokienize_str(debug.line))
    return args


def add_debug_metadata(program, context: Context):
    debug = context.debug
    for line in program:
        line.debug = []

    for debug_command in debug:
        index, distance = find_closest_command(program, debug_command)
        best_command = program[index]
        if 'debug' not in best_command:
            best_command.debug = []
        if distance < 0:
            best_command.debug.append({'post': tokenize_debug_comman(debug_command)})
        else:
            best_command.debug.append({'pre': tokenize_debug_comman(debug_command)})
            
    return program, context

def generate_debug_command(line_obj):
    return ['log', line_obj.line]


def add_debug_command_logging(program, context: Context):
    if not config.logmode or config.use_disassembly_as_logs:
        return program, context

    for obj_line in program:
        if 'debug' not in obj_line:
            obj_line.debug = []
        obj_line.debug.append({'pre': generate_debug_command(obj_line)})
    
    return program, context