# Automated Thematic Coding of Telegram Messages with GPT and R

This script automates the content analysis and thematic coding of large batches of Telegram messages using the OpenAI GPT API.  
It is tailored for research projects requiring systematic coding based on a predefined codebook (with codes and their descriptions).

---
## 1. What the Script Does

- Loads Telegram messages from a JSON file (one message per row).
- Loads a codebook (text file) with codes and optional descriptions.
- Batches the messages and sends them to GPT (OpenAI API) with a structured prompt.
- For each message, the model assigns up to 5 codes from the codebook, and detects whether there is explicit author opinion.
- Outputs structured results in both JSON and CSV format.

The script is designed for transparent, reproducible, and scalable annotation of large text datasets.

---
## 2. Codebook Format Example

The codebook should be a plain text file (`.txt`), one line per code.  
Each line consists of a numeric code, a short theme description, and an optional comment, separated by a tab character.

Example (See real codes in `codes_with_desc_RU.txt`):

```yaml
1 Farm # Texts mentioning farms or agricultural production
2 City # Urban themes, city life, or municipal issues
3 Animals # Mentions of animals, livestock, or wildlife
99 Nothing # Used when no main theme applies to the message
```

Lines starting with `#` are ignored in script names. Descriptions and comments help improve GPT accuracy, but are not mandatory.

---
## 3. How to Use

**1. Prepare your files:**
- `filtered_by_topics.json`: Input file with Telegram messages, each row as a message.
- `codes_with_desc_RU.txt`: Your codebook (see example above).

**2. Set your parameters at the top of the script:**
- Input/output file paths
- OpenAI API key and model (e.g., `"gpt-4o"`, `"gpt-4.1"`)
- Batch size and processing range

**3. Run the script in R:**

```r
source("your_script_name.R")
```
---
## 4. Output Structure

For every processed batch, you will get:

- **output_X_to_Y.json**: Array of coded messages, with assigned codes and opinion flag
- **output_X_to_Y.csv**: Same data in tabular format
- **processing_log.txt**: Chronological log of all actions, errors, and batch information

_*X and Y here are the numbers of the json elements in the file you uploaded.
If you want to process the entire array, specify elements from 1 to `NA`._

**Example output (CSV):**

| global_id | text                 | Codes  | Opinion |
|-----------|----------------------|--------|---------|
|    1      | The farm is large... | 1;3    |   0     |
|    2      | City life is busy    | 2      |   1     |
|    3      | ...                  | 99     |   0     |

---

## 5. Prompt Structure and Coding Guidelines

The script constructs a precise prompt for GPT using your codebook.  
- GPT can assign up to 5 codes to each message.
- If no code fits, code `99` is assigned.
- The model also detects if a message expresses an explicit opinion (`Opinion`: 1 = yes, 0 = no).

**Prompt Example:**

You are a professional academic researcher and expert in thematic content analysis of texts.
Your task is to analyze each of the following texts separately...

For each text, determine:

1. Which codes from the provided list are present (max 5 codes per text).
2. Whether the text contains explicit opinion or commentary by the author (respond 0 or 1). 
3. If the text does not fit any theme, use code '99'. If you think new themes should be added, suggest them separately. Output strictly in JSON format — an array of objects: 'id' (message number), 'Codes' (array), 'Opinion' (0 or 1).

_The prompt is already in the code, this is just a clearer example!_

---
## 6. Requirements

- R 4.x
- Packages: `httr`, `jsonlite`, `stringr`, `readr`

Install with:

```r
install.packages(c("httr", "jsonlite", "stringr", "readr"))
```
---

## License
MIT License

## Credits
Author: Egor Kozhevnikov, Charles University, 2025

