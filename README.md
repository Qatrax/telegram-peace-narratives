# Peace Narratives in Pro-Kremlin Telegram Channels (Feb–Mar 2025)

This repository contains supplementary materials for a mixed-methods research project focused on how pro-Kremlin Telegram channels discussed peace negotiations between February and March 2025.

## Folder Structure

- `telegram_extraction/` — script for collecting Telegram data via official API using a list of channel links.
- `data/` — metadata file (`channels_metadata.csv`) with original names, links, follower counts, and assigned categories for all 87 channels.
- `modeling/` — Python scripts used for training the BERTopic model; includes preprocessing and saving routines.
- `coding_R/` — R scripts for automated qualitative coding using GPT-4.1 and a predefined dictionary of 16 narrative codes.
- `figures/` — key figures used in the memo or presentation (e.g., daily posting volume).
- `trained_model/` (optional / external) — pre-trained BERTopic model (available separately via external link due to file size limits).

## Reproducibility

To reproduce topic modeling or qualitative coding:
- See `Modeling/training_bert.py` for training details
- See `Coding/coding_API.R` for how batches were submitted to GPT-4.1 via API

## Notes

- All Telegram data was collected via open channels using public APIs.
- Content includes only textual posts (media attachments excluded).
- Due to Telegram's terms, full post content is not shared, but model and metadata are.