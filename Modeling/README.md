# BERTopic Training & Topic Review Scripts

This repository contains scripts for topic modeling of Russian-language Telegram data using [BERTopic](https://maartengr.github.io/BERTopic/) and [sentence-transformers](https://www.sbert.net/).  
The workflow includes preprocessing, model training, and quick review/export of topic structure.

---
## 1. `training_bert.py` — Train BERTopic Model & Assign Topics

This script:
- Loads Telegram messages from a folder of JSON files (one per channel);
- Preprocesses text (removes links and punctuation, tokenizes, lemmatizes, removes stopwords);
- Trains a BERTopic model with multilingual embeddings;
- Assigns a topic number to each message and saves all results for further analysis.

### Usage

1. Place your Telegram channel `.json` files in a folder (default: `channels_list/`).
2. (Optional) Adjust paths or parameters at the top of the script.
3. Run:

    ```bash
    python training_bert.py
    ```

4. The script will save:
    - The trained BERTopic model (`bert_output/bertopic_model`)
    - An interactive HTML visualization of topics (`bert_output/topics.html`)
    - All message metadata with assigned topics (`bert_output/df_meta_with_topics.csv`)

### Main Parameters

At the top of the script you can set:
- `INPUT_DIR`: folder with your `.json` files;
- `OUTPUT_DIR`: where to save results (created if missing);
- Preprocessing and model parameters (see script comments).

### Output files

- **bertopic_model**: folder with the saved BERTopic model
- **topics.html**: interactive visualization of all topics
- **df_meta_with_topics.csv**: full table (each row = message, columns: original text, channel, date, preprocessed text, topic number)

## 2. `list_bert_topics.py` — Topic Overview and Export

This script:
- Loads a trained BERTopic model;
- Exports a summary table for all topics: topic number, name, size, and top-10 words per topic;
- Prints a preview to the console.

### Usage

1. Make sure you have a previously trained BERTopic model in `bert_output/bertopic_model`.
2. Run:

    ```bash
    python list_topics.py
    ```

3. The script will save:
    - `bert_output/topic_info_with_words.csv`: table with all topics and top words
    - Console output: preview of the first 10 topics

### Output columns (in CSV)

- `Topic`: numeric topic identifier
- `Name`: (auto-generated) topic label
- `Count`: number of messages in this topic
- `Top_Words`: top-10 keywords for this topic, comma-separated

## Access to the Trained BERTopic Model

Due to repository size and licensing restrictions, the trained BERTopic model is **not included** in this repository.

If you need the trained model for research or reproducibility purposes, please email your request to:  
**qatraxstudy@gmail.com**

_(Upon request, a direct download link (e.g., Google Drive) can be provided.)_
## Requirements

- Python 3.8+
- [pandas](https://pandas.pydata.org/)
- [nltk](https://www.nltk.org/)
- [pymorphy2](https://pymorphy2.readthedocs.io/en/latest/)
- [tqdm](https://tqdm.github.io/)
- [bertopic](https://maartengr.github.io/BERTopic/)
- [sentence-transformers](https://www.sbert.net/)

Install with:

```bash 
pip install pandas nltk pymorphy2 tqdm bertopic sentence-transformers
```
_The scripts automatically download required NLTK resources on first run._
## License
MIT License.

## Credits
Author: Egor Kozhevnikov, Charles University, 2025

