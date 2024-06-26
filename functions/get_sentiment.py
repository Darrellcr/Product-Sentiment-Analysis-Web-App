import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
import re

from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch

def preprocess_function(examples, aspect_token = '[ASPECT]', review_token = '[REVIEW]'):
    combined_txt_results = []
    
    for example in examples :
        combined_texts = aspect_token + example["variable"] + review_token + example["review"]
        combined_txt_results.append(combined_texts)
        
    return combined_txt_results

def get_sentiment(reviews_aspect : list) :

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")
    review_token = '[REVIEW]'
    aspect_token = '[ASPECT]'
    special_tokens_dict = {'additional_special_tokens': [review_token, aspect_token]}
    num_added_tokens = tokenizer.add_special_tokens(special_tokens_dict)

    # Load pre-trained model with a classification head <- change this to your model path
    model = AutoModelForSequenceClassification.from_pretrained(os.environ.get("INDOBERT_ABSA_PATH"), num_labels=3)
    model.resize_token_embeddings(len(tokenizer))
    
    # check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"Using {device}")

    # Define your batch size
    batch_size = 16

    # Assuming reviews is a list of your input texts
    num_batches = len(reviews_aspect) // batch_size + (1 if len(reviews_aspect) % batch_size != 0 else 0)

    # Initialize an empty list to store predicted labels
    all_predicted_labels = []

    for i in range(num_batches):
        # Get the current batch
        batch_reviews = reviews_aspect[i * batch_size:(i + 1) * batch_size]
        
        batch_reviews = preprocess_function(batch_reviews)
        batch_reviews = tokenizer(
            batch_reviews, 
            padding="max_length", 
            truncation=True, 
            max_length=128,
            return_tensors="pt"
        )
        
        # Forward pass
        device = model.device
        inputs = {key: value.to(device) for key, value in batch_reviews.items()}
        outputs = model(**inputs)

    # Get predicted label
        logits = outputs.logits
        
        predicted_class_id = torch.argmax(logits, dim=1)
        
        # Map class id to label (Assuming 0: Negative, 1: Neutral, 2: Positive)
        label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
        predicted_labels = [label_map[id.item()] for id in predicted_class_id]

        # Store the predicted labels
        all_predicted_labels.extend(predicted_labels)

    # all_predicted_labels now contains the predicted labels for all reviews

    results = []

    for result, predicted_labels in zip(reviews_aspect, all_predicted_labels):
        results.append({"review": result["review"], "aspect": result["variable"], "sentiment": predicted_labels})

    return results

def main() :
    results = [{'review': 'Sepatu bagus, nyaman dipakai', 'variable': 'barang'}, {'review': 'Sepatu tidak nyaman dipakai', 'variable': 'barang'}, {'review': 'Sepatu bagus, tapi tidak nyaman dipakai', 'variable': 'barang'}]
    results = get_sentiment(results)
    print(results)

if __name__ == '__main__' :
    main()


