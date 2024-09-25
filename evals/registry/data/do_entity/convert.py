import json
import os
output_dir = '/workspace/evals/evals/registry/data/do_entity'
# Step 1: Customize the prompt and sample size
sample_size = 50  # You can change this number to specify how many samples you want in the sample JSONL file

# Step 2: Read the source JSON file
with open('/workspace/datasets/MedS-Bench/Explanation/task46_do_entity_explanation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Step 3: Extract the list of instances
instances = data.get('Instances', [])
prompt = data['Definition'][0]
# Initialize lists to hold the full data and sample data
full_data = []
sample_data = []

# Step 4: Process each instance
for idx, instance in enumerate(instances):
    # Extract the 'input' and 'output' from each instance
    input_text = instance.get('input', '')
    output_text = instance.get('output', '')

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

# Step 5: Write the full data to a JSONL file
with open(os.path.join(output_dir,'full_data.jsonl'), 'w', encoding='utf-8') as f:
    for item in full_data:
        # Write each JSON object on a new line
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Step 6: Write the sample data to a separate JSONL file
with open(os.path.join(output_dir, 'sample_data.jsonl'), 'w', encoding='utf-8') as f:
    for item in sample_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')