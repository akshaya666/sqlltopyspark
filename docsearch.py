import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import openai

def determine_chunk_size(file_path, max_chunks=1000):
    # Calculate an appropriate chunk size based on file size
    file_size = os.path.getsize(file_path)
    return max(500, file_size // max_chunks)

def chunk_text_streaming(file_path, chunk_size):
    with open(file_path, 'r', encoding='utf-8') as file:
        buffer = []
        for line in file:
            words = line.split()
            buffer.extend(words)
            while len(buffer) >= chunk_size:
                yield ' '.join(buffer[:chunk_size])
                buffer = buffer[chunk_size:]
        if buffer:
            yield ' '.join(buffer)

def index_document_streaming(file_path):
    # Determine optimal chunk size
    chunk_size = determine_chunk_size(file_path)

    # Define the schema
    schema = Schema(content=TEXT(stored=True))

    # Create the index directory if it doesn't exist
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    # Create the index
    ix = create_in("indexdir", schema)

    # Add the chunks to the index
    writer = ix.writer()
    for chunk in chunk_text_streaming(file_path, chunk_size):
        writer.add_document(content=chunk)
    writer.commit()

def search_index(query_str, limit=10):
    ix = open_dir("indexdir")
    relevant_chunks = []
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query, limit=limit)
        for result in results:
            relevant_chunks.append(result['content'])
    return relevant_chunks

def generate_answer(question, relevant_chunks, model="gpt-3.5-turbo"):
    prompt = f"Question: {question}\n\nHere are some relevant parts of the document:\n\n"
    for chunk in relevant_chunks:
        prompt += f"- {chunk}\n\n"
    prompt += "Answer:"

    attempt = 0
    max_retries = 3
    while attempt < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,  # Adjust max tokens if needed
                temperature=0.7  # Adjust temperature for creativity vs. accuracy
            )
            return response.choices[0].message['content'].strip()
        except RateLimitError:
            attempt += 1
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    raise Exception("Rate limit exceeded. Please try again later.")

file_path = "your_document.txt"  # Path to your document
index_document_streaming(file_path)

question = "What is the main topic of the document?"
relevant_chunks = search_index(question, limit=10)
answer = generate_answer(question, relevant_chunks)
print(answer)
