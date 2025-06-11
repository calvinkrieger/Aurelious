import tkinter as tk
import threading
import speech_recognition as sr

# Function to run speech recognition
def recognize_speech(text_widget):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        text_widget.insert(tk.END, "Listening...\n")
        audio = recognizer.listen(source)

    try:
        text_widget.insert(tk.END, "Recognizing...\n")
        text = recognizer.recognize_google(audio)
        text_widget.insert(tk.END, f"You said: {text}\n")
    except sr.UnknownValueError:
        text_widget.insert(tk.END, "Sorry, I couldn't understand that.\n")
    except sr.RequestError as e:
        text_widget.insert(tk.END, f"Request error: {e}\n")

# Button click triggers speech recognition in separate thread
def start_listening(text_widget):
    thread = threading.Thread(target=recognize_speech, args=(text_widget,))
    thread.start()

# GUI setup
root = tk.Tk()
root.title("Retail AI Assistant")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

text_output = tk.Text(frame, height=15, width=60)
text_output.pack()

listen_button = tk.Button(frame, text="Speak", command=lambda: start_listening(text_output))
listen_button.pack(pady=10)

root.mainloop()
