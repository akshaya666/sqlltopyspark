import json

class TextProcessor:
    def __init__(self, json_data):
        self.json_data = json_data
        self.chunks = []

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

    def save_chunks_to_json(self, output_file):
        with open(output_file, 'w') as f:
            json.dump(self.chunks, f, indent=2)
