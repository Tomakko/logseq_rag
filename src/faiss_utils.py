import json
import numpy as np
import faiss
from .database import get_all_embeddings

def build_faiss_index():
    records = get_all_embeddings()

    dim = len(json.loads(records[0][1])) # 1024, dimensionality of embeddings

    embedding_matrix = np.zeros((len(records), dim), dtype=np.float32)

    id_map = {} # to map index in matrix to original id
    for i, record in enumerate(records):
        idx, embedding_str = record
        embedding = np.array(json.loads(embedding_str), dtype=np.float32)
        embedding_matrix[i] = embedding
        id_map[i] = idx

    # build the faiss index
    index = faiss.IndexFlatL2(dim)
    index.add(embedding_matrix)

    return index, id_map

if __name__ == '__main__':
    faiss_index, id_map = build_faiss_index()
    print((f'FAISS index has {faiss_index.ntotal} items'))
    print(f'ID map: {id_map}')