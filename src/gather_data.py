from tqdm import tqdm
import re

from .database import create_tables, store_embedding
from .find_notes import find_notes
from .logseq_parser import extract_blocks
from .embeddings import get_embedding
from .local_settings import PAGE_IGNORE_EXPRESSIONS, BLOCK_IGNORE_EXPRESSIONS


def filter_pages(pagename):
    valid = True
    for be in PAGE_IGNORE_EXPRESSIONS:
        if re.match(be, pagename):
            valid = False
    return valid

def filter_blocks(block):
    valid = True
    for be in BLOCK_IGNORE_EXPRESSIONS:
        if re.match(be, block):
            valid = False
    return valid

def gather_data():
    create_tables()
    pagenames = find_notes()

    for pagename in tqdm(pagenames, desc="Processing pages", total=len(pagenames)):

        tqdm.write(f"Processing: {pagename}")

        if not filter_pages(pagename):
            continue

        blocks, down_pointers, up_pointers = extract_blocks(filename=pagename)

        for block, dp, up in zip(blocks, down_pointers, up_pointers):
            
            if not filter_blocks(block):
                continue

            embedding = get_embedding(content=block)

            store_embedding(
                filename=pagename,
                content=block,
                embedding=embedding,
                down_pointers=dp,
                up_pointers=up
            )

if __name__ == '__main__':
    gather_data()