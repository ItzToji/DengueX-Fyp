import pandas as pd
import json

train = pd.read_csv("bert_train.csv")
val = pd.read_csv("bert_val.csv")
test = pd.read_csv("bert_test.csv")

print("Train size:", len(train))
print("Val size:", len(val))
print("Test size:", len(test))

print("Columns:", train.columns)
print("Unique labels:", train["label"].nunique())

with open("intent_label_map.json") as f:
    label_map = json.load(f)

print("Label map:", label_map)
