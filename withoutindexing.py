def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def chunk_text(text, max_tokens=2048):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def ask_question_to_chunks(question, chunks, model="gpt-3.5-turbo", max_tokens=300):
    answers = []

    for chunk in chunks:
        prompt = f"{chunk}\n\nQuestion: {question}\nAnswer:"
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            answer = response.choices[0].message['content'].strip()
            answers.append(answer)
        except openai.error.OpenAIError as e:
            print(f"Error: {e}")
    
    return answers

def summarize_answers(answers, model="gpt-3.5-turbo", max_tokens=300):
    combined_answers = "\n\n".join(answers)
    prompt = f"Here are several answers to the same question from different parts of a document:\n\n{combined_answers}\n\nPlease provide a concise summary of the answer:"
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        summary = response.choices[0].message['content'].strip()
        return summary
    except openai.error.OpenAIError as e:
        print(f"Error: {e}")
        return None
file_path = "your_document.txt"  # Path to your .txt document
text = read_txt(file_path)

# Adjust max_tokens if needed, but ensure it's within the API limits
chunks = chunk_text(text, max_tokens=2048)

question = "What is the main topic of the document?"
answers = ask_question_to_chunks(question, chunks, model="gpt-3.5-turbo")

if answers:
    summary = summarize_answers(answers, model="gpt-3.5-turbo")
    print(summary)
else:
    print("No answers found for the question.")
