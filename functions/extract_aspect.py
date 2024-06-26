import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
import re

from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch

def clean_text(texts):
    cleaned_text = []

    for text in texts:

        text = text.lower()

        text = re.sub(r"[^a-zA-Z?.!,¿]+", " ", text) # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",")

        punctuations = '@#!?+&*[]-%.:/();$=><|{}^' + "'`" + '_'
        for p in punctuations:
            text = text.replace(p,'') #Removing punctuations

        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text) #Removing emojis
        cleaned_text.append(text)

    return cleaned_text

def get_aspect(reviews : pd.DataFrame) :
    dataset = Dataset.from_pandas(reviews)

    # Define the labels and mappings
    labels = ["pelayanan", "pengiriman", "barang"]
    id2label = {idx: label for idx, label in enumerate(labels)}
    label2id = {label: idx for idx, label in enumerate(labels)}

    # Initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")

    # load the model <- change this to your model path
    model = AutoModelForSequenceClassification.from_pretrained(os.environ.get("INDOBERT_ASPECT_PATH"))

    # check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Using {device}")

    # only keep the review columns
    reviews = dataset.remove_columns(['rating'])
    reviews = reviews["review"]

    # Define your batch size
    batch_size = 32

    # Assuming reviews is a list of your input texts
    num_batches = len(reviews) // batch_size + (1 if len(reviews) % batch_size != 0 else 0)

    # Initialize an empty list to store predicted labels
    all_predicted_labels = []

    for i in range(num_batches):
        # Get the current batch
        batch_reviews = reviews[i * batch_size:(i + 1) * batch_size]
        batch_reviews = clean_text(batch_reviews)

        # Tokenize the batch
        encoding = tokenizer(batch_reviews, return_tensors="pt", padding="max_length", truncation=True, max_length=128)
        encoding = {k: v.to(model.device) for k, v in encoding.items()}

        # Forward pass
        outputs = model(**encoding)
        logits = outputs.logits

        # Apply sigmoid + threshold
        sigmoid = torch.nn.Sigmoid()
        probs = sigmoid(logits.squeeze().cpu())
        predictions = np.zeros(probs.shape)
        predictions[np.where(probs >= 0.5)] = 1

        # Turn predicted id's into actual label names
        predicted_labels = [[id2label[idx] for idx, label in enumerate(prediction) if label == 1.0] for prediction in predictions]

        # Store the predicted labels
        all_predicted_labels.extend(predicted_labels)

    results = []

    for review, predicted_labels in zip(reviews, all_predicted_labels):
        for label in predicted_labels:
            results.append({"review": review, "variable": label})

    return results

def main() :
    reviews = pd.DataFrame({
        "review" : ["Sepatu bagus, nyaman dipakai", "Sepatu tidak nyaman dipakai", "Sepatu bagus, tapi tidak nyaman dipakai"],
        "rating" : [5, 1, 3]
    })

    results = get_aspect(reviews)
    print(results)

    results = [{'review': 'Sepatu bagus, nyaman dipakai', 'variable': 'barang'}, {'review': 'Sepatu tidak nyaman dipakai', 'variable': 'barang'}, {'review': 'Sepatu bagus, tapi tidak nyaman dipakai', 'variable': 'barang'}]


if __name__ == '__main__' :
    main()







