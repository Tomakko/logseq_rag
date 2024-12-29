import sqlite3
import json

from.local_settings import SQLITE_DB_PATH
from .embeddings import get_embedding

def get_rows_by_id(row_ids):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, filename, content, down_pointers, up_pointers
        FROM embeddings
        WHERE id in ({seq})
        """.format(seq=','.join(['?']*len(row_ids))),
        row_ids
    )
    records = cursor.fetchall()
    return records

def get_rows_by_filename(filename):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM embeddings WHERE filename = ? ORDER BY id ASC",
        (filename,))
    records = cursor.fetchall()
    return records

def get_all_embeddings():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, embedding FROM embeddings")
    records = cursor.fetchall()
    return records

def get_number_of_entries_in_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # Execute a query to count the rows
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    row_count = cursor.fetchone()[0]

    return row_count

def create_tables():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY,
        filename TEXT,
        content TEXT,
        embedding TEXT,
        down_pointers TEXT,
        up_pointers TEXT
    )
    ''')
    conn.commit()

def store_embedding(
        filename=None,
        content=None,
        embedding=None,
        down_pointers=None,
        up_pointers=None):
    embedding_str = json.dumps(embedding)
    down_pointers_str = json.dumps(down_pointers)
    up_pointers_str = json.dumps(up_pointers)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor =conn.cursor()

    cursor.execute(
            "INSERT INTO embeddings (filename, content, embedding, down_pointers, up_pointers) VALUES (?, ?, ?, ?, ?)",
            (filename or '', content or '', embedding_str, down_pointers_str, up_pointers_str)
        )

    conn.commit()

if __name__ == '__main__':
    create_tables()

    embedding = get_embedding(content="This is a test")

    store_embedding(
        filename='test.txt',
        content='This is a test',
        embedding=embedding,
        down_pointers=[0,1],
        up_pointers=[2,3]
    )

    all_embeddings = get_all_embeddings()
    embeddings_count = len(all_embeddings)
    print(f'Found {embeddings_count} embeddings')

    rows = get_rows_by_id([1])
    print(rows)

    filename_qery_result = get_rows_by_filename("./ECCV Workshop on  Vision-based  InduStrial  InspectiON.md")
    print(filename_qery_result)

    


