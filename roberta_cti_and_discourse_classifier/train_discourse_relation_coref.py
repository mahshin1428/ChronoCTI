import torch
import pandas as pd
import json
import os
import sklearn.metrics
import numpy as np
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    RobertaTokenizerFast,
    RobertaForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)

# Suppressing tokenizers parallelism warning which can cause hanging on Mac
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def compute_metrics(eval_pred):
    # Hugging Face Trainer requires a custom function to calculate metrics during training
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    # Calculate F1 scores just like the original code
    f1_weighted = sklearn.metrics.f1_score(labels, predictions, average='weighted')
    f1_macro = sklearn.metrics.f1_score(labels, predictions, average='macro')
    f1_micro = sklearn.metrics.f1_score(labels, predictions, average='micro')
    
    return {
        "f1_weighted": f1_weighted,
        "f1_macro": f1_macro,
        "f1_micro": f1_micro
    }

def main():
    # Explicitly verify and print that we are using the Mac GPU (MPS) instead of CPU
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print("Using device:", device)

    # 1. Load data
    # NOTE: Changed to the coref dataset!
    with open('discourse_train_v2_coref.json', 'r') as file:
        data = json.load(file)

    uniquelabels = list(set([d['relation'] for d in data]))
    uniquelabels.sort()
    labelCount = len(uniquelabels)
    print("Labels found:", uniquelabels)

    text_a = [dt['S1'] for dt in data]
    text_b = [dt['S2'] for dt in data]
    labels = [uniquelabels.index(dt['relation']) for dt in data]

    data_df = pd.DataFrame({
        'text_a': text_a,
        'text_b': text_b,
        'label': labels # Hugging Face expects the column to be named exactly 'label'
    })

    print("Data shape:", data_df.shape)

    # 2. Split data
    train_df, eval_df = train_test_split(data_df, test_size=0.20, random_state=42)
    print("Train size:", len(train_df))

    # Convert pandas dataframe to Hugging Face Dataset
    train_dataset = Dataset.from_pandas(train_df)
    eval_dataset = Dataset.from_pandas(eval_df)

    # 3. Load Tokenizer and Model
    # Pointed to the exact checkpoint folder for your pre-trained MLM weights
    model_path = "Roberta-CTI/checkpoint-40969"
    
    tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")
    
    # Load sequence classification model and tell it how many classes we are predicting
    model = RobertaForSequenceClassification.from_pretrained(model_path, num_labels=labelCount)

    # 4. Tokenize data
    def tokenize_function(examples):
        # We pass text_a and text_b together so the model understands it's a sentence pair task
        return tokenizer(
            examples['text_a'], 
            examples['text_b'], 
            padding="max_length", 
            truncation=True, 
            max_length=512
        )

    # Apply tokenization
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

    # 5. Define Training Arguments
    # Translated SimpleTransformers args to HF TrainingArguments.
    training_args = TrainingArguments(
        output_dir="./discourse_coref_model_output", # Changed output dir so it doesn't overwrite your first model
        overwrite_output_dir=True,
        num_train_epochs=7, # I set this to 7 since you preferred that in the last run!
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",  
        save_strategy="epoch",        
        logging_steps=100,
        load_best_model_at_end=True,  
        metric_for_best_model="f1_weighted",
        
        # Disable Weights & Biases (wandb) prompt permanently
        report_to="none",
        
        # Mac specifics
        no_cuda=True,
        fp16=False,
        dataloader_num_workers=0
    )

    # 6. Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        compute_metrics=compute_metrics,
        # Replaces simpletransformers' early stopping
        callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
    )

    # 7. Train
    print("Starting training...")
    trainer.train()

    # 8. Final Evaluation
    print("Evaluating final model...")
    predictions = trainer.predict(tokenized_eval)
    y_pred = np.argmax(predictions.predictions, axis=-1)
    y_true = predictions.label_ids

    print('weighted:', sklearn.metrics.f1_score(y_true, y_pred, average='weighted'))
    print('macro:', sklearn.metrics.f1_score(y_true, y_pred, average='macro'))
    print('micro:', sklearn.metrics.f1_score(y_true, y_pred, average='micro'))
    print(sklearn.metrics.classification_report(y_true, y_pred, target_names=uniquelabels))

if __name__ == "__main__":
    main()
 