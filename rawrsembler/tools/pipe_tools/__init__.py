import argparse
import os
import sys

import path
sys.path.append(str(path.Path(__file__).parent.parent))
import core
import requests
import hashlib
import random
import clipboard
import json

def init():
    """
    Loads json from stdin and restores profile_name and parsed instructions
    """
    
    data = ''.join(list(sys.stdin))
    decoder = json.JSONDecoder()

    try:
        raw = decoder.decode(data)
        profile = core.profile.profile.load_profile_from_file(f"{raw['profile_name']}", False)
        
        data = list(raw['data'])
    
        return profile, data
    except json.JSONDecodeError as err:
        print("Cannot parse input. Check if you didn't add --save to compile.py")
        raise
    