import openai

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key_here'

# Function to extract and combine text from the JSON structure
def extract_text_from_json(json_data):
    combined_text = []
    for page in json_data:
        for content in page['content']:
            if content['type'] == 'text':
                combined_text.append(content['text'])
            elif content['type'] == 'image':
                combined_text.extend(content['text'])  # Assuming text extracted from image is a list of strings
    return ' '.join(combined_text)

# Function to estimate the number of tokens in a text
def estimate_tokens(text):
    return len(text.split())

# Function to chunk the combined text into manageable parts
def chunk_text(text, max_chunk_size):
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        current_tokens += len(word)
        if current_tokens > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = len(word)
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# Function to ask questions using ChatGPT and retrieve answers
def ask_question(question, json_data, max_tokens_per_chunk):
    combined_text = extract_text_from_json(json_data)
    text_length = estimate_tokens(combined_text)

    # Set max tokens for each chunk
    max_chunk_size = min(max_tokens_per_chunk, text_length)

    text_chunks = chunk_text(combined_text, max_chunk_size)

    answers = []
    for chunk in text_chunks:
        prompt = f"{chunk}\n\nQuestion: {question}\nAnswer:"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        answer = response.choices[0].message['content'].strip()
        answers.append(answer)

    return answers

# Function to refine and get a precise answer
def get_precise_answer(question, json_data):
    initial_answers = ask_question(question, json_data, max_tokens_per_chunk=2048)
    aggregated_answer = "\n\n".join(initial_answers)
    
    # Secondary query to refine the answer
    refinement_prompt = f"The following are multiple answers to the question '{question}':\n\n{aggregated_answer}\n\nPlease provide a concise and precise answer based on the above information."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": refinement_prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    precise_answer = response.choices[0].message['content'].strip()

    return precise_answer

# Example usage
question = "What does the document say about the sales figures?"
json_data = [
    {
        "page_num": 1,
        "content": [
            {
                "type": "text",
                "text": "This is some text from the PDF."
            },
            {
                "type": "image",
                "text": ["Text extracted from image."]
            }
        ]
    },
    {
        "page_num": 2,
        "content": [
            {
                "type": "text",
                "text": "More text from another page."
            }
        ]
    }
]

precise_answer = get_precise_answer(question, json_data)
print(precise_answer)
