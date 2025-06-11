import os
import pandas as pd
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

# === Configuration ===
OPENAI_API_KEY = "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"
CATALOG_FILE = "TrialCSVCatalog.csv"

client = OpenAI(api_key=OPENAI_API_KEY)
model = SentenceTransformer('all-MiniLM-L6-v2')

# === Step 1: Detect audio file ===
AUDIO_FILE = None
for f in os.listdir():
    if f.lower().endswith((".mp3", ".wav", ".m4a")):
        AUDIO_FILE = f
        break
if AUDIO_FILE is None:
    raise FileNotFoundError("No audio file (.mp3, .wav, or .m4a) found in folder.")

# === Step 2: Transcribe audio ===
print("Transcribing customer question...")
with open(AUDIO_FILE, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
customer_question = transcription.text.strip()
print("\n🗣️ Customer asked:", customer_question)

# === Step 3: Ask GPT for ideal product categories ===
category_prompt = f"""
Customer asked: "{customer_question}"

List the general product types, chemicals, tools, or materials that would be used to solve this problem. Do NOT mention brand names. Give 5-7 distinct product types in a list.
"""

category_response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": category_prompt}],
    temperature=0.3
)
product_ideas = category_response.choices[0].message.content.strip().split("\n")
product_keywords = [line.strip("-• ").lower() for line in product_ideas if line.strip()]
print("\n💡 GPT suggests these types of products:")
for kw in product_keywords:
    print("-", kw)

# === Step 4: Load catalog and search ===
print("\nSearching your catalog...")
catalog_df = pd.read_csv(CATALOG_FILE)
catalog_df["combined_text"] = (
    catalog_df["Description"].astype(str) + " | $" +
    catalog_df["Retail"].astype(str)
)

# Filter catalog rows that contain any product keyword
matches = []
for kw in product_keywords:
    kw_matches = catalog_df[catalog_df["combined_text"].str.lower().str.contains(kw)]
    matches.extend(kw_matches.to_dict(orient="records"))

# Deduplicate matches
unique_matches = {m["Description"]: m for m in matches}.values()
top_matches = list(unique_matches)[:3]  # top 3

if not top_matches:
    print("\n⚠️ No matches found in your catalog for suggested product types.")
    print("Consider adding a fallback or retry loop here.")
    exit()

# === Step 5: Ask GPT to explain recommendation ===
product_summary = "\n".join([
    f"- {p['Description']} (${p['Retail']})" for p in top_matches
])
explanation_prompt = f"""
Customer asked: "{customer_question}"

Your store has the following matching products:
{product_summary}

As a helpful hardware store assistant, explain what the customer should do and why these products are good choices.
"""

print("\n🧠 AI Recommendation:")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": explanation_prompt}],
    temperature=0.7
)
print(response.choices[0].message.content.strip())
