try:
    import core
except ModuleNotFoundError as module:
    print(f"{module} You can install dependencies by running:\n\t pip install -r requirements.txt")
    exit()

import argparse
import logging
import sys
import core.adress_solver
import core.error as error
import core.config as config
import core.context as contextlib

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

parser.add_argument("-s", "--save", choices=["txt", "pip", "hex", "pad", "schem", "bin"], type=str, default = 'pip',
help="""> pad - Build source and save as binary with padding to bytes
> txt - Build source and save as binary with padding to arguments
> pip - Build source and dump json to stdout (for pipelining), (standard output will be redirected to stderr)
> hex - Build source and save as hexadecimal representation of bytes
> schem - Build source and save as schematic
> bin - Build source and save as plain text
Default: pip (will not save)""")

parser.add_argument('-c','--comments', dest='comments', action='store_true', help="Add debug information on the end of every line in output files")
parser.set_defaults(feature=False)

parser.add_argument('--debug', dest='debug', action='store_true', help="Turn on debug mode")

args = parser.parse_args()

DEBUG_MODE = args.debug

config.override_from_dict(vars(args))

def override_debug():
    if DEBUG_MODE:
        config.override_from_dict(
            run = True,
            # save = "pip",
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

override_debug()

if config.save == "pip":
    # redirect output
    sys.stdout = sys.stderr

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

    # set profile_name
    context.profile_name = 'wvrn.jsonc'

    # Load profile and pass it to context
    override_debug()

    output, context = core.pipeline.exec_pipeline(parse_pipeline, output, context, progress_bar_name='Parsing')

    solve_wvrn = \
    [
        ('solve adresses', core.adress_solver.adress_solver.solve_adresses),
    ]


    output, context = core.pipeline.exec_pipeline(solve_wvrn, output, context, progress_bar_name='Solving adresses')

    output, context = core.pipeline.exec_pipeline(parse_pipeline, output, context, progress_bar_name='Parsing')
 
    output, context = core.pipeline.exec_pipeline(format_pipeline, output, context, progress_bar_name='Formatting')

    output, context = core.pipeline.exec_pipeline(save_pipeline, output, context, progress_bar_name='Saving')

    

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