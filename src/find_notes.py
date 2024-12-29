import os
import subprocess

from .local_settings import LOGSEQ_FOLDER

def find_notes():

    os.chdir(LOGSEQ_FOLDER)
    command = 'find . -name "*.md"'
    files = subprocess.run(command, shell=True, capture_output=True, text=True)
    files = files.stdout.split('\n')
    files = [f for f in files if not (f.startswith('./@') or f.startswith('./hls') or len(f)<1)]
    return files

if __name__ == '__main__':
    files = find_notes()
    print(files)