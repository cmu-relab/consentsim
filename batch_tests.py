#!env/bin/python3

import os

def generate(fn_name):
    
        os.system("python script_generator.py " + fn_name + " " + str(500) )

def main():
    
    for i in range(5):
        
        # re start
        generate("steps")
        generate("data")
        generate("data_and_recipient")
    
    for i in range(5):

        generate("access")
        generate("data_and_access")

        generate("collect")
        generate("data_and_collect")

        generate("realistic")


if __name__ == "__main__":
    main()