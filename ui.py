from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

chat_history = []

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', section='home')

@app.route('/upload_files', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        uploaded_files = [file.filename for file in files if file]
        return render_template('index.html', section='upload', uploaded_files=uploaded_files)
    return render_template('index.html', section='upload')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global chat_history
    if request.method == 'POST':
        user_message = request.form['message']
        chat_history.append({'role': 'user', 'message': user_message})
        # Here you can add code to get the response from the bot and append it to chat_history
        # For now, we'll just echo the message back
        chat_history.append({'role': 'bot', 'message': user_message})
        return redirect(url_for('chat'))
    return render_template('index.html', section='chat', chat_history=chat_history)

@app.route('/clear_chat')
def clear_chat():
    global chat_history
    chat_history = []
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)
