from flask import Flask, render_template, request, jsonify, redirect, url_for
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

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message', '').strip()
    selected_document = request.form.get('selected_document', '')

    # Here you can process the message and selected document
    # For now, we'll just simulate a response
    response = {
        'chat_history': [
            {'role': 'user', 'message': message},
            {'role': 'bot', 'message': f"ChatBot response to: {message} with document {selected_document}"}
        ],
        'selected_document': selected_document
    }

    return jsonify(response)

@app.route('/clear_chat')
def clear_chat():
    # Clear chat history and redirect
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)

