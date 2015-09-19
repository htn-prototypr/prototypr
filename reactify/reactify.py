#!/usr/bin/python
import os
import subprocess
import sys

PWD = os.path.dirname(os.path.realpath(__file__))

# Read index file
def read_index_file():
    pass
    
# project_name should be all lowercase; the title of the React project will be project_name.capitalize()
def create(project_name='test'):
    directory = os.path.join(PWD, "output")
    if not os.path.exists(directory):
        os.mkdir(directory)
    # Hand off to bash script to continue work
    subprocess.call(['./reactify.sh', project_name, project_name.capitalize()])

def main():
    num_args = len(sys.argv)
    if num_args > 1:
        create(sys.argv[1])
    else:
        create()

if __name__ == "__main__":
    main()
