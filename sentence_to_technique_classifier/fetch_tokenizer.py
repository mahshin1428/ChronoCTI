from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("roberta-base")
tokenizer.save_pretrained("../roberta_cti_and_discourse_classifier/Roberta-CTI/checkpoint-40969")
print("Successfully saved tokenizer files to checkpoint-40969")
