import argparse
import os
import sys

import path
sys.path.append(str(path.Path(__file__).parent.parent))

if __name__ == "__main__":
    import pipe_tools

    profile, program = pipe_tools.init()
    
    if len(program) == 0:
        exit()

    # collect line[""]

    bytes = []
    for line in program:
        bytes.extend(line["value"])

    # convert to hex
    hex_bytes = []
    for byte in bytes:
        hex_bytes.append('0x'+hex(byte)[2:].zfill(2))
    
    print(' '.join(hex_bytes))

    