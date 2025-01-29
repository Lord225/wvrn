try:
    import core
except ModuleNotFoundError as module:
    print(f"{module} You can install dependencies by running:\n\t pip install -r requirements.txt")
    exit()

import argparse
import logging
import pprint
from typing import Callable
from core import quick
import core.adress_solver
import core.error as error
import core.config as config
import core.context as contextlib
import sys

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter, 
    description=
"""It is Rawrsembler. It is a custom Assembly for most Nefarius CPUs.
    
You can start with: \t 'python compile.py'

It will compile "program.lor" and save it in "output" dir.
if emulation is avalible add --run to emulate compiled program and --logs to show instructions in console (if avalible)
""")

parser.add_argument("-i", "--input", type=str, default="./src/program.wvrn",
help="""Name of file to compile
Default: src/program.wvrn""")

parser.add_argument("-o", "--output", type=str, default="./out/compiled.txt", help="Name of file to save in")

parser.add_argument('--debug', dest='debug', action='store_true', help="Turn on debug mode")

args = parser.parse_args()

DEBUG_MODE = args.debug

config.override_from_dict(
    {
        'input': args.input,
        'output': args.output
    }
)

def override_debug():
    if DEBUG_MODE:
        config.override_from_dict(
            run = True,
            save = "bin",
            comments = True,
            onerror = 'None',
            debug = True,
            logmode = True,
            why_error=True
        )
        logging.basicConfig(
            level=logging.DEBUG
        )
        logging.debug("Logging is set to debug")


def compile():
    load_preproces_pipeline = core.pipeline.make_preproces_pipeline() # Load & Preprocess
    parse_pipeline = core.pipeline.make_parser_pipeline()             # Parse & Extract arguments
    save_pipeline = core.pipeline.make_save_pipeline()                # Format & Save
    format_pipeline = core.pipeline.make_format_pipeline()            # Format

    start_file = config.input
    
    override_debug()

    profile = core.profile.profile.load_profile_from_file('wvrn.jsonc', True)

    output, context = core.pipeline.exec_pipeline(load_preproces_pipeline, start_file, contextlib.Context(profile), progress_bar_name='Loading')

    if context.profile_name:
        config.override_from_dict(profile=context.profile_name)
    if config.init is not None:
        config.override_from_file(config.init)

    # Load profile and pass it to context
    override_debug()

    output, context = core.pipeline.exec_pipeline(parse_pipeline, output, context, progress_bar_name='Parsing')

    pprint.pprint(output)
    pprint.pprint(context.__dict__)

    solve_wvrn = \
    [
        ('solve adresses', core.adress_solver.adress_solver.solve_adresses),
    ]


    output, context = core.pipeline.exec_pipeline(solve_wvrn, output, context, progress_bar_name='Solving adresses')



def on_compilation_error(err: error.CompilerError):
    print("*"*50) 
    print(f"Error in line {err.line}:" if err.line is not None else f"Error in unknown line:")
    print(f"{err.info}")
    if err.line_object is not None:
        if 'is_macro_expanded' in err.line_object: # type: ignore
            print(f"This originates from macro expansion in line {err.line_object.line_index_in_file}:")
            for line in err.line_object.expanded_command:
                print(f"> {line}")
            print(f">: {err.line_object.line}")

def on_profile_error(err):
    print("*"*50)
    print('Error loading profile:')
    print(f'{err}')

def other_error(err):
    print("*"*50)
    print('Other compile error:')
    print(f'{err}')

def key_error(err):
    print("*"*50)
    print(f"Internal compiler error (missing key): Expected: {err}")


if __name__ == "__main__":
    if config.CPYTHON_PROFILING:
        import cProfile
        cProfile.run("main()", sort="cumtime")
    else:
        if config.onerror is None:
            compile()
        else:
            try:
                compile()
            except error.CompilerError as err:
                on_compilation_error(err)
            except error.ProfileLoadError as err:
                on_profile_error(err)
            except KeyError as err:
                key_error(err) 
            except Exception as err:
                other_error(err)
            finally:
                if config.onerror == "interupt":
                    input()
                elif config.onerror == "abort":
                    pass