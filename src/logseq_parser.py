import sys
import re

from .local_settings import LOGSEQ_FOLDER

def extract_blocks(filename=None):
    file_path = f'{LOGSEQ_FOLDER}/{filename}'

    with open(file_path, 'r') as f:
        lines = f.readlines()

    notes = []
    hirarchy_level = [] # for tracking hirarchy level of every note

    #page name
    notes.append(filename.replace('.md','').replace('./',''))
    hirarchy_level.append(0)

    for line in lines:
        if not line.strip():
            continue

        indent = len(re.findall(r"(    |\t)", line))

        #remove markdown formatting symbols
        line = line.strip().replace("- ","").strip()
        line = line.replace("# ","")
        line = line.replace("#","")

        # remove short lines
        if len(line) < 2:
            continue

        # remove lines which contain ::, i.e. tags 
        if '::' in line:
            continue


        notes.append(line)
        hirarchy_level.append(indent+1)

    down_pointers = get_downwards_hirarchy_pointers(hirarchy_level)
    up_pointers = get_upwards_hirarchy_pointers(hirarchy_level)
    return notes, down_pointers, up_pointers


# calculcates for every note, the indices of all notes which are below it in the hirarchy
def get_downwards_hirarchy_pointers(hirarchy_levels):
    all_pointers = [] # array of arrays
    for i in range(len(hirarchy_levels)):
        h = hirarchy_levels[i]
        pointers = [] # pointers for curent element
        for j in range(i+1, len(hirarchy_levels)):
            # as long as hirarchy level is larger append indices
            if hirarchy_levels[j] > h: 
                pointers.append(j)
            else:
                break
        all_pointers.append(pointers)
    
    return all_pointers 

# calculcates for every note, the indices of all notes which are above it in the hirarchy
def get_upwards_hirarchy_pointers(hirarchy_levels):
    all_pointers = [] # array of arrays
    # iterate backwards
    for i in range(len(hirarchy_levels) - 1, -1, -1):
        h = hirarchy_levels[i]
        pointers = [] # pointers for curent element
        for j in range(i, -1, -1):
            # as long as hirarchy level gets smaller append indices
            if hirarchy_levels[j] < h: 
                pointers.append(j)
                h = hirarchy_levels[j]
        all_pointers.append(list(reversed(pointers)))
    
    return list(reversed(all_pointers))

if __name__ == '__main__':
    filename = sys.argv[1]
    notes = extract_blocks(filename=filename)
    print(notes)
