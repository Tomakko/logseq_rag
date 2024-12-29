SQLITE_DB_PATH = "/home/martin/logseq_assistant/embedding_db.sqlite"
LOGSEQ_FOLDER = "/home/martin/logseq_assistant/logseq_copy"

PAGE_IGNORE_EXPRESSIONS = [
]

BLOCK_IGNORE_EXPRESSIONS = [
    r"^!", # starts with ! -> image
    r"^\[\[.*\]\]$" # [[link]]
]