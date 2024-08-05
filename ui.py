from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'sdf34987tymns037ut3n0tu30jrgj3klfgu430g98q90gro'  # random set of characters
app.config['UPLOAD_FOLDER'] = 'uploads/'

app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=5)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Dummy list of documents
DOCUMENTS = ['Document 1', 'Document 2', 'Document 3']

@app.route('/')
def home():
    session['dummy'] = '1'
    session['chat_history'] = []
    session['selected_document'] = None  # Initialize selected document
    return render_template('index.html', section='home', documents=DOCUMENTS)

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

        return render_template('index.html', section='upload', uploaded_files=uploaded_files, documents=DOCUMENTS)
    return render_template('index.html', section='upload', documents=DOCUMENTS)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        if 'message' in request.form:
            message = request.form.get('message', '').strip()
            if message:
                session['dummy'] = '2'
                session['chat_history'].append({'role': 'user', 'message': message})

                # Simulate a bot response
                bot_message = f"ChatBot: {message}"
                session['chat_history'].append({'role': 'bot', 'message': bot_message})

    return render_template('index.html', section='chat', chat_history=session.get('chat_history', []), selected_document=session.get('selected_document'))

@app.route('/clear_chat')
def clear_chat():
    session['chat_history'] = []
    return redirect(url_for('chat'))

@app.route('/update_document', methods=['POST'])
def update_document():
    selected_document = request.form.get('selected_document')
    session['selected_document'] = selected_document
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=False)
