import core.error as error
import re

def get_value(strage_format:str):
    """Returns value of strage_format"""
    strage_format = strage_format.strip()
    try:
        return int(strage_format, base=0)
    except:
        pass
    if len(strage_format[2:]) == 0:
        raise error.ParserError(-1, f"Value: '{strage_format}' cannot be parsed.")
    elif strage_format[:2] == "0x":
        return int(strage_format[2:],base=16)
    elif strage_format[:2] == "0b":
        return int(strage_format[2:],base=2)
    else:
        raise error.ParserError(-1, f"Value: '{strage_format}' cannot be parsed.")


def smart_replace(line: str, From: str, To: str):
    line = re.sub(r"(?<![a-zA-Z0-9\w])({})(?![a-zA-Z0-9\w])".format(From), To, line)
    return line


def smart_find(line: str, From: str):
    finded = re.search(r"(?<![a-zA-Z0-9\w])({})(?![a-zA-Z0-9\w])".format(From),line)
    return finded

