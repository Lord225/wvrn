import logging
from .base import *
from . import tokenize as tokenize
from . import match_commands as match_commands
from . import jumps as jumps
from . import debug_heades as debug_heades
from . import generate as generate
from . import solve_sections as solve_sections
from . import macros as macros

def parse_number(token):
    try:
        return get_value(token)
    except:
        return None

def parse_hex(token):
    try:
        if token[:2] == "0x":
            return int(token[2:],base=16)
        else:
            return int(token, base=16)
    except:
        return None
def parse_bin(token):
    try:
        if token[:2] == "0b":
            return int(token[2:], base=2)
        else:
            return int(token, base=2)
    except:
        return None
def parse_dec(token):
    try:
        return int(token[2:], base=10)
    except:
        return None
def parse_label(token, labels: dict):
    if token not in labels:
        return None
    return labels[token]

def parse_string(token):
    if token[0] == '"' and token[-1] == '"':
        return token[1:-1]
    return None

def parse_offset_label(token, labels: dict, line):
    if token not in labels:
        return None
    if line.has_key('physical_adress'):
        return labels[token]-line.physical_adress
    else:
        return 0