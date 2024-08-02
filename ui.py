from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('index.html', section='home')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return redirect(url_for('home'))
    
    files = request.files.getlist('files[]')
    for file in files:
        if file and file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
    
    return redirect(url_for('home'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        user_message = request.form['message']
        chatbot_response = f"ChatBot: {user_message}"  # Simulate chatbot response
        
        # Append new messages to chat history
        session['chat_history'].append({'role': 'user', 'message': user_message})
        session['chat_history'].append({'role': 'bot', 'message': chatbot_response})

    return render_template('index.html', section='chat', chat_history=session.get('chat_history'))

@app.route('/clear_chat')
def clear_chat():
    session.pop('chat_history', None)
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)

