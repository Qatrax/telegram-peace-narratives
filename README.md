# Peace Narratives in Pro-Kremlin Telegram Channels (Feb–Mar 2025)

This repository contains supplementary materials for a mixed-methods research project focused on how pro-Kremlin Telegram channels discussed peace negotiations between February and March 2025.

## Folder Structure

- `telegram_extraction/` — script for collecting Telegram data via official API using a list of channel links.
- `data/` — metadata file (`List of Telegram channels.xlsx`) with original names, links, follower counts, and assigned categories for all 86 channels.
- `modeling/` — Python scripts used for training the BERTopic model; includes preprocessing and saving routines.
- `coding/` — R script for automated qualitative coding using GPT-4.1 and a predefined dictionary of 16 narrative codes.
- `trained_model/` (external) — pre-trained BERTopic model (The link is available separately upon request. To get it, please email the author at `qatraxstudy@gmail.com`. ).

## Reproducibility

To reproduce topic modeling or qualitative coding:
- See `Modeling/training_bert.py` for training details
- See `Coding/coding_API.R` for how batches were submitted to GPT-4.1 via API

## Notes

- All Telegram data was collected via open channels using public APIs.
- Content includes only textual posts (media attachments excluded).
- Due to ethical and security considerations, the full content of the publication is not disclosed publicly, but the metadata is available.
