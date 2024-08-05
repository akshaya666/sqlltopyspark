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
    global selected_documents, chat_history
    if request.method == 'POST':
        message = request.form['message']
        chat_history.append({'role': 'user', 'message': message})
        chat_history.append({'role': 'bot', 'message': f"Echo: {message}"})
        selected_documents = request.form.getlist('selected_documents[]')
    return render_template('index.html', section='chat', dummy_documents=dummy_documents, selected_documents=selected_documents, chat_history=chat_history)

@app.route('/clear_chat')
def clear_chat():
    global chat_history
    chat_history = []
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)
