from bertopic import BERTopic
import pandas as pd
from pathlib import Path

# Paths
OUTPUT_DIR = Path("bert_output")
MODEL_PATH = OUTPUT_DIR / "bertopic_model"

print("Loading BERTopic model...")
topic_model = BERTopic.load(str(MODEL_PATH))

# Get topic info DataFrame (contains: Topic, Name, Count, etc.)
topic_info = topic_model.get_topic_info()

def get_top_words(topic_id, n=10):
    """Return top-n words for a topic, comma-separated."""
    words_scores = topic_model.get_topic(topic_id)
    if words_scores:
        return ", ".join([word for word, _ in words_scores[:n]])
    return ""

topic_info["Top_Words"] = topic_info["Topic"].apply(lambda tid: get_top_words(tid))

# Save to CSV and print a preview
topic_info.to_csv(OUTPUT_DIR / "topic_info_with_words.csv", index=False)
print("\nTopic table saved to 'topic_info_with_words.csv'")
print("Preview of the first 10 topics:")

print(topic_info[["Topic", "Name", "Count", "Top_Words"]].head(10).to_string(index=False))
