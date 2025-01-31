import logging
from typing import List
from core.context import Context
from .base import *

def load_raw(path: str, context: Context):
    program = list()
    logging.info(f"Loading file {path}")
    with open(path, "r") as file:
        program = [Line(line, line_index_in_file=i+1) for i, line in enumerate(file)]
    Program = [line for line in program if len(line) != 0]
    return Program

def load_from_string(string: str, context: Context):
    program = string.split("\n")
    program = [Line(line, line_index_in_file=i+1) for i, line in enumerate(program)]
    Program = [line for line in program if len(line) != 0]
    return Program

def load_lines(lines: list, context: Context):
    program = [Line(line, line_index_in_file=i+1) for i, line in enumerate(lines)]
    Program = [line for line in program if len(line) != 0]
    return Program

def strip(program: List[Line], context: Context):
    for data in program:
        data.line = data.line.replace("\t",' ').replace("\n",'').strip()
    return program

def remove_empty_lines(program: List[Line], context: Context):
    return [line for line in program if line.line.strip() != ""]
            