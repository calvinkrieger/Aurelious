import os

# === Automatically find first audio file ===
AUDIO_FILE = None
for filename in os.listdir():
    if filename.lower().endswith((".mp3", ".wav", ".m4a")):
        AUDIO_FILE = filename
        break

if AUDIO_FILE is None:
    raise FileNotFoundError("No audio file (.mp3, .wav, or .m4a) found in this folder.")

import pandas as pd
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

# === 1. CONFIGURATION ===
OPENAI_API_KEY = "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"  # Replace with your real key or use an environment variable
CATALOG_FILE = "TrialCSVCatalog.csv"             # CSV product catalog

# === 2. SETUP ===
client = OpenAI(api_key=OPENAI_API_KEY)
model = SentenceTransformer('all-MiniLM-L6-v2')

# === 3. TRANSCRIBE AUDIO ===
print("Transcribing audio...")
with open(AUDIO_FILE, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
customer_question = transcription.text
print("\n🗣️ Customer asked:", customer_question)

# === 4. LOAD PRODUCT CATALOG ===
print("\nLoading product catalog...")
catalog_df = pd.read_csv(CATALOG_FILE)
catalog_df['combined_text'] = (
    catalog_df['Description'].astype(str) +
    " | Price: $" + catalog_df['Retail'].astype(str) +
    " | Location: " + catalog_df['Loc'].astype(str)
)

# === 5. VECTOR SEARCH ===
print("Finding matching products...")
product_texts = catalog_df['combined_text'].tolist()
product_embeddings = model.encode(product_texts, show_progress_bar=False)

query_embedding = model.encode(customer_question, convert_to_tensor=True)
scores = util.cos_sim(query_embedding, product_embeddings)[0]
top_indices = np.argsort(-scores.numpy())[:3]
matches = catalog_df.iloc[top_indices][['Description', 'Retail', 'Loc']]
print("\n🔎 Top Matching Products:")
print(matches.to_string(index=False))

# === 6. FORMAT PROMPT FOR GPT ===
top_products = matches.to_dict(orient="records")
product_summary = "\n".join([
    f"- {p['Description']} (${p['Retail']}, located at {p['Loc']})"
    for p in top_products
])
gpt_prompt = f"""
Customer asked: "{customer_question}"

Here are the most relevant store products:
{product_summary}

As a helpful hardware store assistant, explain what the customer should do and why these products are suitable.
"""

# === 7. GET GPT REASONING ===
print("\n🧠 GPT's Suggestion:")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": gpt_prompt}],
    temperature=0.7
)
print(response.choices[0].message.content)
