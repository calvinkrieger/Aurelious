import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import shutil
import os

# === Basic UI Setup ===
window = tk.Tk()
window.title("AI Retail Assistant")
window.geometry("600x400")

# === UI State ===
selected_audio = None
selected_catalog = None

# === File Selection ===
def choose_audio():
    global selected_audio
    filepath = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.m4a")])
    if filepath:
        selected_audio = filepath
        audio_label.config(text=os.path.basename(filepath))

def choose_catalog():
    global selected_catalog
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        selected_catalog = filepath
        catalog_label.config(text=os.path.basename(filepath))

# === Safe File Copy ===
def safe_copy_audio(selected_audio, target_prefix="input_audio"):
    ext = os.path.splitext(selected_audio)[-1]
    dst = target_prefix + ext
    try:
        if not os.path.samefile(selected_audio, dst):
            shutil.copyfile(selected_audio, dst)
            print(f"Audio file copied from {selected_audio} to {dst}")
        else:
            print(f"Audio file already in place: {dst}")
    except FileNotFoundError:
        shutil.copyfile(selected_audio, dst)
    except Exception as e:
        print(f"Error in safe_copy_audio: {e}")

def safe_copy_catalog(selected_catalog, target_filename="TrialCSVcatalog.csv"):
    try:
        if not os.path.samefile(selected_catalog, target_filename):
            shutil.copyfile(selected_catalog, target_filename)
            print(f"Catalog file copied from {selected_catalog} to {target_filename}")
        else:
            print(f"Catalog file already in place: {target_filename}")
    except FileNotFoundError:
        shutil.copyfile(selected_catalog, target_filename)
    except Exception as e:
        print(f"Error in safe_copy_catalog: {e}")

# === Run Main Assistant ===
def run_assistant():
    if not selected_audio or not selected_catalog:
        messagebox.showerror("Missing Files", "Please select both an audio file and a catalog CSV.")
        return

    # Copy files safely
    safe_copy_audio(selected_audio)
    safe_copy_catalog(selected_catalog)

    # Run the smart assistant script and capture all output
    try:
        result = subprocess.run(
            ["python", "main_smart.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # capture both stdout and stderr
            text=True
        )
        print("=== Assistant Output ===")
        print(result.stdout)  # also print to terminal
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, result.stdout)
    except Exception as e:
        output_box.insert(tk.END, f"Error running assistant: {str(e)}")

# === UI Layout ===
tk.Label(window, text="Audio File:").pack()
audio_label = tk.Label(window, text="No file selected")
audio_label.pack()
tk.Button(window, text="Choose Audio File", command=choose_audio).pack(pady=5)

tk.Label(window, text="Catalog File:").pack()
catalog_label = tk.Label(window, text="No file selected")
catalog_label.pack()
tk.Button(window, text="Choose Catalog CSV", command=choose_catalog).pack(pady=5)

tk.Button(window, text="Run Assistant", command=run_assistant, bg="green", fg="white").pack(pady=10)

output_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, height=10)
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

window.mainloop()
