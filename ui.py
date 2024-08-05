from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong, unique key in production
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

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            session['chat_history'].append({'role': 'user', 'message': message})

            # Simulate a bot response
            bot_message = f"ChatBot: {message}"
            session['chat_history'].append({'role': 'bot', 'message': bot_message})

        # Return JSON for AJAX handling
        return jsonify({'chat_history': session.get('chat_history', [])})

    # Display the chat history and documents
    documents = session.get('documents', [])  # Example: replace with actual list
    selected_document = session.get('selected_document', None)
    
    return render_template('index.html', section='chat', chat_history=session.get('chat_history', []), documents=documents, selected_document=selected_document)

@app.route('/clear_chat')
def clear_chat():
    session.pop('chat_history', None)
    return redirect(url_for('chat'))

@app.route('/select_document', methods=['POST'])
def select_document():
    selected_document = request.form.get('document')
    session['selected_document'] = selected_document
    return jsonify({'selected_document': selected_document})

if __name__ == '__main__':
    app.run(debug=True)
