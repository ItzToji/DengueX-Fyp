import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import accuracy_score, classification_report
import json

# --------------------
# Load label map
# --------------------
with open("intent_label_map.json") as f:
    label_map = json.load(f)

id2label = {v: k for k, v in label_map.items()}
NUM_LABELS = len(label_map)

# --------------------
# Load model & tokenizer
# --------------------
tokenizer = DistilBertTokenizerFast.from_pretrained("dengue_intent_bert")
model = DistilBertForSequenceClassification.from_pretrained(
    "dengue_intent_bert",
    num_labels=NUM_LABELS
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# --------------------
# Dataset class
# --------------------
class DengueIntentDataset(Dataset):
    def __init__(self, csv_file, tokenizer, max_len=48):
        self.data = pd.read_csv(csv_file)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = str(self.data.iloc[idx]["text"])
        label = int(self.data.iloc[idx]["label"])

        encoding = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(label, dtype=torch.long)
        }

# --------------------
# Load test data
# --------------------
test_dataset = DengueIntentDataset("bert_test.csv", tokenizer)
test_loader = DataLoader(test_dataset, batch_size=32)

# --------------------
# Evaluation loop
# --------------------
true_labels = []
pred_labels = []

with torch.no_grad():
    for batch in test_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        preds = torch.argmax(outputs.logits, dim=1)

        true_labels.extend(labels.cpu().numpy())
        pred_labels.extend(preds.cpu().numpy())

# --------------------
# Metrics
# --------------------
accuracy = accuracy_score(true_labels, pred_labels)

print("\nTest Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:\n")
print(classification_report(true_labels, pred_labels, target_names=id2label.values()))
