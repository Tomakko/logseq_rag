import ollama

def get_embedding(content=None, model='mxbai-embed-large '):

    embedding = ollama.embeddings(prompt=content, model="mxbai-embed-large")
    
    return embedding['embedding']


if __name__ == '__main__':
    content = "We have images, taken by Johannes in 3 different old aircrafts in teruel and frankfurt"
    embedding = get_embedding(content=content)
    print(embedding)
    print(len(embedding))

