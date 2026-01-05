# Dengue Chatbot AI Module

## Requirements
- Python 3.9+
- torch
- transformers

## Files
- dengue_intent_bert/: Trained DistilBERT model
- intent_label_map.json: Intent mapping
- chatbot.py: Inference logic

## Usage
Import `chatbot_reply()` from chatbot.py and pass user text.

The model returns dengue-specific responses and warns for non-dengue queries.
