from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy data for documents
dummy_documents = ["Document 1", "Document 2", "Document 3", "Document 4", "Document 5"]
selected_documents = []
chat_history = []

@app.route('/')
def home():
    return render_template('index.html', section='home')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        uploaded_files = [file.filename for file in files]
        return render_template('index.html', section='upload', uploaded_files=uploaded_files)
    return render_template('index.html', section='upload')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    documents = ['Doc1.pdf', 'Doc2.docx', 'Doc3.pptx']  # Example documents
    if 'selected_documents' not in session:
        session['selected_documents'] = []

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            session['chat_history'].append({'role': 'user', 'message': message})
            bot_message = f"ChatBot: {message}"
            session['chat_history'].append({'role': 'bot', 'message': bot_message})

    return render_template('index.html', section='chat', chat_history=session.get('chat_history', []), documents=documents, selected_documents=session.get('selected_documents', []))
@app.route('/clear_chat')
def clear_chat():
    global chat_history
    chat_history = []
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)
