import streamlit as st
from io import StringIO

# Function to handle file uploads
def show_upload_files():
    st.header("Upload Files")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Assuming text files, adjust handling for other file types as needed
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            st.write(f"Uploaded file: {uploaded_file.name}")
            st.text_area("File content", stringio.read(), height=200)

# Function to handle chat prompt
def show_chat_prompt():
    st.header("Chat Prompt")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    def add_message(sender, message):
        st.session_state.chat_history.append({"sender": sender, "message": message})

    user_input = st.text_input("You:", key="user_input")
    if st.button("Send"):
        if user_input:
            add_message("You", user_input)
            # Simulate chatbot response
            response = f"ChatBot: {user_input}"
            add_message("ChatBot", response)
            st.session_state.user_input = ""  # Clear input box

    # Display chat history
    for chat in st.session_state.chat_history:
        st.write(f"**{chat['sender']}**: {chat['message']}")

# Sidebar menu
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ("Upload Files", "Chat Prompt"))

# Main content based on sidebar selection
if menu == "Upload Files":
    show_upload_files()
elif menu == "Chat Prompt":
    show_chat_prompt()
