import json
import os
import random

# Input parameters
input_dir = '/workspace/datasets/MedS-Bench/Text_summarization'
file_prefix = 'task'  # Specify the prefix to match files, e.g., 'task'
mid_prefix = '_mimic_ct'  # Specify the midfix to match files, e.g., '_mimic_ct'
json_files = [
    os.path.join(input_dir, f) for f in os.listdir(input_dir)
    if f.startswith(file_prefix) and mid_prefix in f and f.endswith('.json')
]

output_dir = '/workspace/evals/evals/registry/data/mimic-iv-ct'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
full_data_filename = os.path.join(output_dir, 'full_data.jsonl')
sample_data_filename = os.path.join(output_dir, 'sample_data.jsonl')
if os.path.exists(full_data_filename):
    os.remove(full_data_filename)
if os.path.exists(sample_data_filename):
    os.remove(sample_data_filename)
# Customize the prompt and sample size
sample_size = 100  # You can change this number to specify how many samples you want in the sample JSONL file

# For each JSON file in json_files
for json_file in json_files:
    # Read the source JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract the list of instances
    instances = data.get('Instances', [])
    
    # Check if we have enough instances
    if len(instances) < 3:
        raise ValueError(f"Not enough instances in {json_file} to create few-shot examples.")
    
    # Select the first three instances for few-shot examples
    few_shot_instances = instances[:3]
    
    # Remove few-shot instances from the list of instances
    remaining_instances = instances[3:]
    
    # Construct the few_shot_case string
    few_shot_case = ""
    for idx, instance in enumerate(few_shot_instances, 1):
        input_text = instance.get('input', '').strip()
        output_text = instance.get('output', '').strip()
        few_shot_case += f"Case{idx}: Input: \"{input_text}\", Output: \"{output_text}\"\n"
    
    # Construct the prompt
    prompt = few_shot_case + data['Definition'][0] + " Please learn from the few-shot cases to see what content you have to output."
    
    # Initialize lists to hold the full data and sample data for this file
    full_data = []
    sample_data = []
    
    # Process each remaining instance
    for idx, instance in enumerate(remaining_instances):
        # Extract the 'input' and 'output' from each instance
        input_text = instance.get('input', '').strip()
        output_text = instance.get('output', '').strip()
    
        # Construct the new JSON object as per the required format
        output_dict = {
            "input": [
                {
                    "role": "user",
                    "content": f"{prompt} {input_text}"
                }
            ],
            "ideal": output_text
        }
    
        # Add the new object to the full data list
        full_data.append(output_dict)
    
        # If the current index is less than the sample size, add to sample data
        if idx < sample_size:
            sample_data.append(output_dict)
    
    # Prepare filenames for output
    base_filename = os.path.basename(json_file)
    filename_without_ext = os.path.splitext(base_filename)[0]

    
    # Write the full data to a JSONL file
    with open(full_data_filename, 'a', encoding='utf-8') as f:
        for item in full_data:
            # Write each JSON object on a new line
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # Write the sample data to a separate JSONL file
    with open(sample_data_filename, 'a', encoding='utf-8') as f:
        for item in sample_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
