import os
import json
import re
import tqdm
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

TAXONOMY_PATH = "../selected_assetsWName.json"

def create_promptv2_from_dataset(dataset_path, prompt_path):
    examples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            text = data['text']
            labels = [key for key in data['cats'].keys() if data['cats'][key] == 1.0]
            labels_str = ', '.join(labels) if labels else "None"
            examples.append({
                'messages': [
                    {"role": "user", "content": text},
                    {"role": "assistant", "content": labels_str}
                ]
            })

    with open(prompt_path, 'w', encoding='utf-8') as writer:
        for ex in examples:
            writer.write(json.dumps(ex, ensure_ascii=False) + "\n")

def generate_all_prompts():
    for i in range(5):
        create_promptv2_from_dataset(
            f'../assets/train_test_splits/train_assets_split_{i}.jsonl',
            f'../assets/train_test_prompt_splits/train_assets_promptv2_split_{i}.jsonl'
        )
        create_promptv2_from_dataset(
            f'../assets/train_test_splits/test_assets_split_{i}.jsonl',
            f'../assets/train_test_prompt_splits/test_assets_promptv2_split_{i}.jsonl'
        )
    print("Generated all prompt splits for OpenAI fine-tuning.")

def eval_model(fold, model_id):
    responses = []
    test_file = f'../assets/train_test_splits/test_assets_split_{fold}.jsonl'
    
    lines = []
    with open(test_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                lines.append(json.loads(line))
                
    for data in tqdm.tqdm(lines):
        try:
            text = data['text']
            completion = openai.ChatCompletion.create(
                model=model_id,
                messages=[{"role": "user", "content": text}]
            )
            answer = completion.choices[0].message.content
            pattern = r"A\d{4}"
            matches = re.findall(pattern, answer)

            responses.append({
                "text": text,
                "actual": [k for k, v in data['cats'].items() if v == 1.0],
                "predicted": matches
            })
        except Exception as e:
            print(f"Error during eval: {e}")
            
    out_file = f'../assets/train_test_response_splits/test_response_split_{fold}.jsonl'
    with open(out_file, 'w', encoding='utf-8') as writer:
        for r in responses:
            writer.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved responses to {out_file}")

def compute_confusion_report(fold):
    with open(TAXONOMY_PATH) as f:
        taxonomy = json.load(f)
    asset_ids = sorted([x['id'] for x in taxonomy])
    
    y_true = []
    y_pred = []
    
    res_file = f'../assets/train_test_response_splits/test_response_split_{fold}.jsonl'
    with open(res_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            actual = data['actual']
            predicted = data['predicted']
            y_true.append([1 if aid in actual else 0 for aid in asset_ids])
            y_pred.append([1 if aid in predicted else 0 for aid in asset_ids])
            
    try:
        from sklearn.metrics import classification_report
        report = classification_report(y_true, y_pred, target_names=asset_ids, zero_division=0)
        print(f"=== OpenAI GPT Evaluation Report (Fold {fold}) ===")
        print(report)
    except ImportError:
        print(f"Evaluated {len(y_true)} predictions for fold {fold}.")

if __name__ == "__main__":
    generate_all_prompts()

