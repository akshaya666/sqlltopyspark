import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("File Upload and Chat Prompt UI")

        # Main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left menu frame
        self.menu_frame = tk.Frame(self.main_frame, width=200, bg='lightgray')
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right content frame
        self.content_frame = tk.Frame(self.main_frame, bg='white')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Menu buttons
        self.upload_button = tk.Button(self.menu_frame, text="Upload Files", command=self.show_upload_files)
        self.upload_button.pack(pady=10, padx=10, fill=tk.X)

        self.chat_button = tk.Button(self.menu_frame, text="Chat Prompt", command=self.show_chat_prompt)
        self.chat_button.pack(pady=10, padx=10, fill=tk.X)

    def show_upload_files(self):
        self.clear_content_frame()
        
        file_label = tk.Label(self.content_frame, text="Upload Files")
        file_label.pack(pady=10)

        upload_button = tk.Button(self.content_frame, text="Choose Files", command=self.choose_files)
        upload_button.pack(pady=10)

        self.file_listbox = tk.Listbox(self.content_frame, width=50, height=10)
        self.file_listbox.pack(pady=10)

    def choose_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.file_listbox.delete(0, tk.END)
            for file_path in file_paths:
                self.file_listbox.insert(tk.END, file_path)
                with open(file_path, 'r') as file:
                    content = file.read()
                    messagebox.showinfo("File Content", content)

    def show_chat_prompt(self):
        self.clear_content_frame()

        chat_label = tk.Label(self.content_frame, text="Chat Prompt")
        chat_label.pack(pady=10)

        self.chat_area = scrolledtext.ScrolledText(self.content_frame, width=50, height=20)
        self.chat_area.pack(pady=10)

        self.user_input = tk.Entry(self.content_frame, width=50)
        self.user_input.pack(pady=10)
        self.user_input.bind("<Return>", lambda event: self.send_message())

        send_button = tk.Button(self.content_frame, text="Send", command=self.send_message)
        send_button.pack(pady=10)

        self.responses = []

    def send_message(self):
        user_message = self.user_input.get()
        if user_message:
            self.chat_area.insert(tk.END, f"You: {user_message}\n")
            self.responses.append(user_message)
            self.user_input.delete(0, tk.END)

            # Echo the user input as the chatbot response (replace with actual chatbot logic)
            chatbot_response = f"ChatBot: {user_message}\n"
            self.chat_area.insert(tk.END, chatbot_response)
            self.responses.append(chatbot_response)
            self.chat_area.yview(tk.END)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.geometry("800x600")
    root.mainloop()
