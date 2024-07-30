import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF
import openai

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key_here'

def extract_text_from_image(img_bytes):
    """Extract text from image bytes using Tesseract OCR."""
    img = Image.open(io.BytesIO(img_bytes))
    text = pytesseract.image_to_string(img)
    return text

def extract_images_from_pdf(file_path):
    """Extract images from a PDF and use OCR to get text from images."""
    descriptions = []
    pdf_document = fitz.open(file_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            img_bytes = base_image["image"]
            text_from_image = extract_text_from_image(img_bytes)
            descriptions.append(f"Image {img_index + 1} on page {page_num + 1} contains: {text_from_image}")
    
    return descriptions

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    pdf_document = fitz.open(file_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    
    return text


def chunk_text(text, max_tokens=2048):
    """Chunk the text into parts that fit within the token limit."""
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

def ask_question_to_chunks(question, chunks, model="gpt-4", max_tokens=300):
    """Send each chunk along with the question to the OpenAI API and collect the answers."""
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

def summarize_answers(answers, model="gpt-4", max_tokens=300):
    """Combine the answers and generate a summary."""
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


file_path = "your_document.pdf"  # Path to your PDF document
text = extract_text_from_pdf(file_path)
image_descriptions = extract_images_from_pdf(file_path)

combined_text = text + "\n\n" + "\n".join(image_descriptions)
chunks = chunk_text(combined_text, max_tokens=2048)

question = "What does the document say about the images?"
answers = ask_question_to_chunks(question, chunks, model="gpt-4")

if answers:
    summary = summarize_answers(answers, model="gpt-4")
    print(summary)
else:
    print("No answers found for the question.")
