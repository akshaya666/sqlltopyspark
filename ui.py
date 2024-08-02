from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('files[]')
    for file in files:
        if file:
            file.save(os.path.join('uploads/', file.filename))
    return redirect(url_for('index'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.form['message']
        chatbot_response = f"ChatBot: {user_message}"  # Simulate chatbot response
        return render_template('chat.html', user_message=user_message, chatbot_response=chatbot_response)
    return render_template('chat.html', user_message=None, chatbot_response=None)

if __name__ == '__main__':
    app.run(debug=True)
