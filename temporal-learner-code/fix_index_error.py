import os
import re

directory = "."
pattern = re.compile(r"\[\s*x\['prob'\]\s+for\s+x\s+in\s+(.*?)\s+if\s+x\['id'\]\s*==\s*(.*?)\s*\]\[0\]")

for filename in os.listdir(directory):
    if filename.endswith(".py"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        new_content = pattern.sub(r"next((x['prob'] for x in \1 if x['id'] == \2), 0)", content)
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename}")
