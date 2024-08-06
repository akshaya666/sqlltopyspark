from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from datetime import timedelta
import boto3
from search_handler import SearchHandler
from text_processor import TextProcessor
import json

app = Flask(__name__)
app.secret_key = 'sdf34987tymns037ut3n0tu30jrgj3klfgu430g98q90gro'
app.config['UPLOAD_FOLDER'] = 'uploads/'

DOCUMENTS = ['Sample', 'Document 2', 'Document 3']
s3_client = boto3.client('s3')
bucket_name = "app-id-25591-dep-id-111615-uu-id-x80cfnuken7o"
uploads_folder_path = "document search/raw_data/"
processed_folder_path= "document search/processed_data/"
chunks_folder_path = "document search/chunks/"

@app.route('/')
def home():
    session['dummy'] = '1'
    session['chat_history'] = []
    session['selected_document'] = DOCUMENTS[0]  # Set default selected document
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
                file_path = os.path.join(uploads_folder_path, file.filename)
                s3_client.upload_fileobj(file, bucket_name, file_path)
                uploaded_files.append(file.filename)

        return render_template('index.html', section='upload', uploaded_files=uploaded_files, documents=DOCUMENTS)
    return render_template('index.html', section='upload', documents=DOCUMENTS)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            session['chat_history'].append({'role': 'user', 'message': message})
            chunk_file = chunks_folder_path + session.get('selected_document') + '.json'
            read_chunk_file = s3_client.get_object(Bucket=bucket_name, Key=chunk_file)
            text_chunks = json.loads(read_chunk_file['Body'].read().decode('utf-8'))
            search_handler_instance = SearchHandler(message, text_chunks)
            search_answer = search_handler_instance.get_precise_answer()
            bot_message = f"{search_answer}"
            session['chat_history'].append({'role': 'bot', 'message': bot_message})
            return jsonify({'message': bot_message})

    return render_template('index.html', section='chat', chat_history=session['chat_history'], documents=DOCUMENTS, selected_document=session.get('selected_document'))

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
