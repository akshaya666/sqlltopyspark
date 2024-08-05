from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('index.html', section='home')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            return redirect(url_for('home'))

        files = request.files.getlist('files[]')
        uploaded_files = []
        for file in files:
            if file and file.filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                uploaded_files.append(file.filename)

        return render_template('index.html', section='upload', uploaded_files=uploaded_files)
    return render_template('index.html', section='upload')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    if 'selected_documents' not in session:
        session['selected_documents'] = []

    if request.method == 'POST':
        if 'message' in request.form:
            message = request.form.get('message', '').strip()
            if message:
                session['chat_history'].append({'role': 'user', 'message': message})

                # Simulate a bot response
                bot_message = f"ChatBot: {message}"
                session['chat_history'].append({'role': 'bot', 'message': bot_message})
        elif 'document' in request.form:
            document = request.form.get('document', '').strip()
            if document and document not in session['selected_documents']:
                session['selected_documents'].append(document)

    dummy_documents = [f"Document {i}" for i in range(1, 11)]  # List of dummy documents

    return render_template('index.html', section='chat', chat_history=session.get('chat_history', []), selected_documents=session.get('selected_documents', []), dummy_documents=dummy_documents)

@app.route('/clear_chat')
def clear_chat():
    session.pop('chat_history', None)
    session.pop('selected_documents', None)
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)
