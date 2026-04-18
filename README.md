# Zynni_Laptop_assistant

Zynni is a Python-based laptop assistant for file search and system utilities.

## NLP Concepts Implemented

This project now includes foundational NLP features for lab assignments:

- Text normalization (lowercasing user input)
- Tokenization
- Stopword removal (for search queries)
- Rule-based intent detection
- POS (Part-of-Speech) tagging using NLTK
- NER (Named Entity Recognition) using NLTK

## Install

```bash
pip install psutil nltk
```

## Run

```bash
python main.py
```

## NLP Commands (examples)

- `pos tag Rahul is reading a book in Delhi`
- `part of speech Apple launches new iPhone today`
- `ner Barack Obama visited India`
- `named entity Microsoft opened a new office in Hyderabad`

If sentence text is not provided in the same line, Zynni prompts for input.