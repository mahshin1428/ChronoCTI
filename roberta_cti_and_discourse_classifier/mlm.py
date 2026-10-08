import torch
from datasets import load_dataset
from transformers import (
    RobertaTokenizerFast,
    RobertaForMaskedLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)

def main():

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print("Using device:", device)

    batch_sizes = [8]

    for bs in batch_sizes:

        print(f"\nTraining with batch size: {bs}")

        tokenizer = RobertaTokenizerFast.from_pretrained("roberta-base")

        model = RobertaForMaskedLM.from_pretrained("roberta-base")


        dataset = load_dataset(
            "text",
            data_files={"train": "train.txt", "test": "test.txt"}
        )

        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=512
            )

        tokenized = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )

        tokenized.set_format("torch")

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=True,
            mlm_probability=0.15
        )

        args = TrainingArguments(
            output_dir=f"CTI-Roberta/outputs_{bs}",
            overwrite_output_dir=True,
            num_train_epochs=1,

            per_device_train_batch_size=bs,
            per_device_eval_batch_size=bs,

            evaluation_strategy="epoch",
            save_strategy="epoch",
            logging_steps=50,
            report_to="none",

            dataloader_num_workers=0,
            fp16=False,
            no_cuda=True
        )


        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=tokenized["train"],
            eval_dataset=tokenized["test"],
            data_collator=data_collator,
        )

        trainer.train()
        trainer.evaluate()


if __name__ == "__main__":
    main()