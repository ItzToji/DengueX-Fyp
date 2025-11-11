
# data/raw

This folder contains all **raw, unprocessed datasets** for DengueX.

## Files Stored Here
- Original Q&A dataset before cleaning
- Files may include malformed rows, duplicate IDs, punctuation issues, etc.

## Purpose
Raw data is never modified directly.  
All cleaning is performed using scripts in:

src/preprocessing/


## Important Notes
- Do not train models using raw data.
- All updates should be documented before preprocessing.
