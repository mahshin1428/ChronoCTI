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

# WHY I CHANGED THIS: Suppressing tokenizers parallelism warning which can cause hanging on Mac
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def compute_metrics(eval_pred):
    # WHY I CHANGED THIS: Hugging Face Trainer requires a custom function to calculate metrics during training
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
    # WHY I CHANGED THIS: Explicitly verify and print that we are using the Mac GPU (MPS) instead of CPU
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print("Using device:", device)

    # 1. Load data
    with open('discourse_train_v2.json', 'r') as file:
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
        'label': labels # Note: Hugging Face expects the column to be named exactly 'label'
    })

    print("Data shape:", data_df.shape)

    # 2. Split data
    train_df, eval_df = train_test_split(data_df, test_size=0.20, random_state=42)
    print("Train size:", len(train_df))

    # WHY I CHANGED THIS: Hugging Face Trainer works best with its own Dataset class, so we convert the pandas dataframe
    train_dataset = Dataset.from_pandas(train_df)
    eval_dataset = Dataset.from_pandas(eval_df)

    # 3. Load Tokenizer and Model
    # WHY I CHANGED THIS: I pointed this exactly to the checkpoint folder you created so it loads the pre-trained weights
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

   
    training_args = TrainingArguments(
        output_dir="./discourse_model_output",
        overwrite_output_dir=True,
        num_train_epochs=7,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",  # evaluate at the end of each epoch
        save_strategy="epoch",        # save at the end of each epoch
        logging_steps=100,
        load_best_model_at_end=True,  # required for early stopping
        metric_for_best_model="f1_weighted",
        
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
        # WHY I CHANGED THIS: Replaces simpletransformers' early stopping. Stops if validation F1 doesn't improve for 5 epochs.
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