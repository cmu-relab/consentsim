#!env/bin/python3

import time
from script_generator import *


def main(argv):
    
    for i in range(10):
        
        generate("steps")
        generate("nested_data")

        generate("access")
        generate("nested_data_and_access")

        generate("collect")
        generate("nested_data_and_collect")

        generate("realistic")
