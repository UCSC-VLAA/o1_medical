import json
import os

# Step 1: Customize the prompt and sample size
prompt = "Please summarize the following radiology report:"
sample_size = 100  # You can change this number to specify how many samples you want from each JSON file
input_dir = '/workspace/datasets/MedS-Bench/Text_summarization'
file_prefix = 'task'  # Specify the prefix to match files, e.g., 'task'
mid_prefix = '_mimic_mri'  # Specify the midfix to match files, e.g., '_mimic_ct'
json_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.startswith(file_prefix) and mid_prefix in f and f.endswith('.json')]
output_dir = '/workspace/evals/evals/registry/data/mimic-iv-mri'

# Step 2: Initialize lists to hold the full data and sample data
full_data = []
sample_data = []

# Step 3: Process each JSON file
for json_file in json_files:
    # Open and load the entire JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        instances = data.get('Instances', [])
        prompt = data['Definition'][0] if 'Definition' in data else prompt

        for idx, instance in enumerate(instances):
            input_text = instance.get('input', '')
            output_text = instance.get('output', '')

            # Construct the new JSON object as per the required format
            
            output_dict = {
                "input": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text}
                ],
                "ideal": output_text
            }

            # Add to the full data list
            full_data.append(output_dict)

            # Add to the sample data if within the sample size for the current file
            if idx < sample_size:
                sample_data.append(output_dict)

# Step 4: Write the full data to a JSONL file
with open(os.path.join(output_dir, 'full_data_w_system.jsonl'), 'w', encoding='utf-8') as f:
    for item in full_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Step 5: Write the sample data to a separate JSONL file
with open(os.path.join(output_dir, 'sample_w_system.jsonl'), 'w', encoding='utf-8') as f:
    for item in sample_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

