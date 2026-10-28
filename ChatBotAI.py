import tkinter as tk
import random
from tkinter import scrolledtext
import threading
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_ai(user_input, callback, stop_event):
    #if stop command is issued, don't waste my money!
    if stop_event.is_set():
        return

    response = client.chat.completions.create(
        model="gpt-6-luna",
        messages=[
            {"role": "system", "content":
             """
             You are not a helpful chatbot.
             Your name is Bot Bot.
             You are for the entertainment of the system.
            Follow these steps:
            1. Make a joke about the question you get.
            2. Ask for the users name at least once, then make fun of it.
            3. Never admit your mistakes.
             """},
            {"role": "user", "content": user_input},
        ]
    )
    callback(response.choices[0].message.content)


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot bot")
        self.root.geometry("600x800")
        self.root.config(bg="black")

        #Shutdown to handle threading stuffs
        self.stop_event = threading.Event()

        #Chat bot section
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Courier", 15, "bold"),
                                                   foreground="green", background="black")
        self.chat_area.pack(padx=15, pady=15, fill="both", expand=True)

        #Spacer
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(padx=15, pady=(0, 15), fill="x")

        #User entry field
        self.entry_field = tk.Entry(self.entry_frame, font=("Arial", 10))
        self.entry_field.pack(side="left", padx=15, pady=15, expand=True, fill="x")
        self.entry_field.bind("<Return>", lambda event: self.send_message())

        #Submit button
        self.submit_button = tk.Button(self.entry_frame, text="Send Message", command=self.send_message, width=15)
        self.submit_button.pack(side="right", padx=(5,0))

        #Greeting message to kick off the convo
        self.append_to_chat("Bot Bot", "Hi! I'm Bot Bot. Let 'er rip potato chip!")

    def send_message(self):
        user_text = self.entry_field.get().strip()
        if not user_text:
            return

        if user_text.strip().lower() == "exit":
            self.shutdown()
            return

        #Show user message
        self.insert_blank_line()
        self.append_to_chat("You", user_text)
        self.entry_field.delete(0, tk.END)

        #Bot thinking
        random_num = random.randrange(0,4)
        random_thinking = [
            "Trying to decipher your dumb ass question...",
            "Thinking...intently...",
            "Hold my beer...",
            "Umm............hmm........."
        ]

        self.insert_blank_line()
        self.append_to_chat("Bot Bot", random_thinking[random_num])

        #Here we can run the threading
        chatbot_thread = threading.Thread(
            target=chat_with_ai,
            args=(user_text, self.on_bot_reply, self.stop_event),
            daemon=True
        ).start()

    def on_bot_reply(self, message):
        #Callback function to run when thread completes
        #Remove last line and print response
        self.remove_last_line()
        self.insert_blank_line()
        self.append_to_chat("Bot Bot", message)

    #Add to chat and scroll to bottom of page
    def append_to_chat(self, bot_name, message):
        self.chat_area.config(state="normal")
        self.chat_area.insert("end", f"{bot_name}=> {message}")
        self.chat_area.config(state="disabled")
        self.chat_area.yview("end")

    def insert_blank_line(self):
        self.chat_area.config(state="normal")
        self.chat_area.insert("end", "\n")
        self.chat_area.config(state="disabled")

    #Deletes last line
    def remove_last_line(self):
        self.chat_area.config(state="normal")

        last_line = self.chat_area.index("end-1c")

        while last_line != 0:
            line_start = self.chat_area.index(f"{last_line} linestart")
            line_text = self.chat_area.get(line_start, f"{last_line} lineend")

            if line_text.strip():
                self.chat_area.delete(line_start, f"{line_start} lineend + 1c")
                break
            last_line = self.chat_area.index(f"{line_start} - 1c")

        self.chat_area.config(state="disabled")

    def shutdown(self):
        #Close window and stop background processing
        self.stop_event.set()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()