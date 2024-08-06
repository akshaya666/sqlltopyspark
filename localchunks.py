import json
import boto3

class TextProcessor:
    def __init__(self, json_data=None, bucket_name=None, s3_client=None, input_file=None):
        if json_data:
            self.json_data = json_data
        elif bucket_name and input_file and s3_client:
            self.json_data = self.load_json_from_s3(bucket_name, input_file, s3_client)
        else:
            raise ValueError("Either json_data or both bucket_name and input_file must be provided.")
        self.chunks = []
        self.bucket_name = bucket_name
        self.s3_client = s3_client

    def load_json_from_s3(self, bucket_name, input_file, s3_client):
        response = s3_client.get_object(Bucket=bucket_name, Key=input_file)
        json_data = json.loads(response['Body'].read().decode('utf-8'))
        return json_data

    def load_json_from_local(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)

    def extract_text_from_json(self):
        combined_text = []
        for page in self.json_data:
            for content in page['content']:
                if content['type'] == 'text':
                    combined_text.append(content['text'])
                elif content['type'] == 'image':
                    combined_text.extend(content['text'])  # Assuming text extracted from image is a list of strings
        return ' '.join(combined_text)

    def estimate_tokens(self, text):
        return len(text.split())

    def chunk_text(self, text, max_tokens=2048):
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0

        for word in words:
            current_tokens += len(word)
            if current_tokens > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_tokens = len(word)
            else:
                current_chunk.append(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        self.chunks = chunks
        return chunks

    def process_text(self, max_chunks=10):
        combined_text = self.extract_text_from_json()
        total_tokens = self.estimate_tokens(combined_text)
        max_tokens_per_chunk = min(8192, total_tokens // max_chunks)  # Adjust chunk size based on total tokens
        self.chunk_text(combined_text, max_tokens_per_chunk)

    def save_chunks_to_s3(self, output_file):
        chunks_data = json.dumps(self.chunks, indent=2)
        self.s3_client.put_object(Bucket=self.bucket_name, Key=output_file, Body=chunks_data)

    def save_chunks_to_local(self, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2)

import json
import boto3
from text_processor import TextProcessor
from chatgpt_handler import ChatGPTHandler

# Local setup
input_file_local = 'input_data.json'
output_file_local = 'output_chunks.json'

# Load JSON data from local file and process it
text_processor = TextProcessor()
text_processor.load_json_from_local(input_file_local)
text_processor.process_text(max_chunks=10)  # Adjust max_chunks as needed
text_processor.save_chunks_to_local(output_file_local)

# Read chunks from the local file
with open(output_file_local, 'r', encoding='utf-8') as f:
    text_chunks = json.load(f)

# Ask questions using ChatGPT
api_key = 'your_openai_api_key_here'
chatgpt_handler = ChatGPTHandler(api_key)

question = "What does the document say about the sales figures?"
precise_answer = chatgpt_handler.get_precise_answer(question, text_chunks)
print(precise_answer)
