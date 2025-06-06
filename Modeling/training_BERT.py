import os
import json
import re
import string
from tqdm import tqdm
from pathlib import Path

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy2

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# --- Download NLTK resources (only runs once per environment) ---
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words("russian"))
morph = pymorphy2.MorphAnalyzer()

# --- Paths and folders ---
INPUT_DIR = Path("channels_list")       # Folder with input .json files (each is a Telegram channel)
OUTPUT_DIR = Path("bert_output")        # Output directory for model and results
OUTPUT_DIR.mkdir(exist_ok=True)

def load_messages(input_dir):
    """Load all messages from JSON files in the input directory.
    Returns: list of texts and DataFrame with metadata."""
    texts = []
    metadata = []
    for file_path in input_dir.glob("*.json"):
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
        for msg in data.get("messages", []):
            text = msg.get("text", "")
            if isinstance(text, str) and len(text.strip()) > 30:
                texts.append(text)
                metadata.append({
                    "text": text,
                    "channel": data.get("channel"),
                    "date": msg.get("date")
                })
    return texts, pd.DataFrame(metadata)

def preprocess(text):
    """Basic preprocessing: remove links, lowercase, remove punctuation, tokenize, remove stopwords, lemmatize."""
    text = re.sub(r"http\S+", "", text)
    text = text.lower()
    text = re.sub(rf"[{string.punctuation}«»…]", " ", text)
    tokens = word_tokenize(text, language="russian")
    tokens = [t for t in tokens if t not in stop_words and t.isalpha()]
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    return " ".join(lemmas)

def main():
    print("Loading messages from JSON files...")
    raw_texts, df_meta = load_messages(INPUT_DIR)
    print(f"Loaded {len(df_meta)} messages.")

    print("Preprocessing texts (lemmatization, tokenization)...")
    df_meta["processed"] = [preprocess(t) for t in tqdm(df_meta["text"])]

    print("Training BERTopic model...")
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    topic_model = BERTopic(embedding_model=embedding_model, language="multilingual")

    topics, _ = topic_model.fit_transform(df_meta["processed"])
    df_meta["topic"] = topics

    # Save model and interactive HTML visualization
    topic_model.save(str(OUTPUT_DIR / "bertopic_model"))
    topic_model.visualize_topics().write_html(str(OUTPUT_DIR / "topics.html"))
    df_meta.to_csv(OUTPUT_DIR / "df_meta_with_topics.csv", index=False)

    print(f"Model and results saved in '{OUTPUT_DIR}'.")
    print("You can now analyze topics or assign them to new data.")

if __name__ == "__main__":
    main()
