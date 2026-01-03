import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from torch.optim import AdamW
from tqdm import tqdm
import json

# --------------------
# Load label map
# --------------------
with open("intent_label_map.json") as f:
    label_map = json.load(f)

NUM_LABELS = len(label_map)

# --------------------
# Load tokenizer & model
# --------------------
tokenizer = DistilBertTokenizerFast.from_pretrained(
    "distilbert-base-uncased"
)

model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=NUM_LABELS
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# --------------------
# Dataset class
# --------------------
class DengueIntentDataset(Dataset):
    def __init__(self, csv_file, tokenizer, max_len=64):
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
# Load training data
# --------------------
train_dataset = DengueIntentDataset("bert_train.csv", tokenizer)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# --------------------
# Optimizer
# --------------------
optimizer = AdamW(model.parameters(), lr=2e-5)

# --------------------
# Training loop
# --------------------
EPOCHS = 4

for epoch in range(EPOCHS):
    print(f"\nEpoch {epoch+1}/{EPOCHS}")
    model.train()
    total_loss = 0

    for batch in tqdm(train_loader):
        optimizer.zero_grad()

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()

    avg_loss = total_loss / len(train_loader)
    print("Training loss:", round(avg_loss, 4))

# --------------------
# Save model
# --------------------
model.save_pretrained("dengue_intent_bert")
tokenizer.save_pretrained("dengue_intent_bert")

print("Training complete. Model saved.")
