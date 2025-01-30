from typing import List
from core.context import Context
from .base import *
import core.error as error
import core.config as config

def remove_comments(lines: List[Line], context: Context):
    for line in lines:
        if "//" in line.line or ";" in line.line:
            # Check if it's inside a string
            if line.line.find('"') < line.line.find("//") and line.line.find('"') > 0:
                continue
            # check for ;
            if line.line.find('"') < line.line.find(";") and line.line.find('"') > 0:
                continue

            if config.save_comments_after_lines:
                pos = line.line.find("//%")
                if pos > 0:
                    line.comment = line.line[pos+3:].strip()
                else:
                    line.comment = None
            else:
                line.comment = None
                
            line.line = line.line[:line.line.find("//")]
            line.line = line.line[:line.line.find(";")] 
    return lines