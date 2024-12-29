import sys
import numpy as np
import ollama
import tiktoken
import ast

# import libraries for fast API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from .database import get_rows_by_id, get_rows_by_filename
from .embeddings import get_embedding
from .faiss_utils import build_faiss_index

NUM_NEIGHBORS=10
COSINE_SIMILARITY=230


PROMPT = """
"You are an AI assistant of a LogSeq plugin that will be used by Martin. Please answer Martin's question as truthfully as possible based on relevant context below. Martin documents his experiences, thoughts and projects in logseq. Those will be provided to you as a context. Any "I" or "me" in the context refers to Martin.
 Each part of the context starts with `SOURCE: ...` and ends with a blank line. Please format your answer using markdown syntax.
Don't mention anything about LogSeq plugin, your output will be directly displayed to the users of this plugin.
"

QUESTION:
{question}

CONTEXT:
{context}
"""


def ask_llama(query=None):
    faiss_index, id_map = build_faiss_index()

    query_vector = get_embedding(content=query)
    query_vector = np.array(query_vector, dtype=np.float32)
    query_vector = query_vector.reshape(1, -1)

    # get 
    dists, indices = faiss_index.search(query_vector, NUM_NEIGHBORS)
    print(dists)
    # only consider neighbors that are less than 1.5 cosine distance
    similar_items = [id_map[idx] for idx, sim in zip(indices[0], dists[0]) if idx >=0 and sim < COSINE_SIMILARITY]

    relevant_db_entries = get_rows_by_id(similar_items)
    
    # assemble context for each line
    for row in relevant_db_entries:
        #print("Dealing with row")
        #print(row)
        context_chain = []

        origin_file = row[1]
        origin_file_content = get_rows_by_filename(origin_file)
        #print("full file")
        #print(origin_file_content)

        down_pointers = ast.literal_eval(row[3])
        up_pointers = ast.literal_eval(row[4])

        #print("abab")
        #print(up_pointers[0])
        higher_level_content = [origin_file_content[int(i)] for i in up_pointers] 
        higher_level_content = [t[0] for t in higher_level_content] 
        lower_level_content = [origin_file_content[int(i)] for i in down_pointers] 
        lower_level_content = [t[0] for t in lower_level_content] 

        #print("h: ", higher_level_content)
        #print("l: ", lower_level_content)
        full_context = higher_level_content + [row[2]] + lower_level_content
        #print("full context")
        #print(full_context)
        #exit()

    prompt_contex = ''
    sources = {}
    for row in relevant_db_entries:
        source = f'Source: {row[1]}'

        if source not in sources:
            sources[source] = []

        sources[source].append(row[2])

    for source in sources:
        context = f'{source}\n'
        for note in sources[source]:
            context += f'{note}\n'
        context += '\n'
        #tmp_context = prompt_contex + context
        prompt_contex += context

    question = query
    prompt = PROMPT.format(context=prompt_contex, question=question)

    print('FULL PROMPT:')
    print(prompt)

    response = ollama.generate(model='llama3.2', prompt=prompt)

    print(response['response'])

    return response['response']

# Define the request body schema using Pydantic
class QueryRequest(BaseModel):
    query: str

# Initialize FastAPI app
app = FastAPI()

# REST API endpoint to accept a text string and call ask_llama
@app.post("/api/ask")
async def ask(request: QueryRequest):
    try:
        # Extract the query from the request body
        query = request.query

        print("the query", query)
        #print("the hisotry", request.history)
        
        # Call the ask_llama function with the query
        answer = ask_llama(query=query)

        print("the anwer", answer)
        
        # Return the answer as JSON response
        return {"query": query, "answer": answer}
    except Exception as e:
        # Handle exceptions and return an error response
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Existing CLI functionality
        query = sys.argv[1]
        answer = ask_llama(query=query)
        print(answer)
    else:
        # Start the FastAPI app using uvicorn
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=5000)