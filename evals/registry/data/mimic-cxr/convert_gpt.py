import json
import os
import random
import argparse

# Step 1: Parse command-line arguments
parser = argparse.ArgumentParser(description="Process MIMIC-CXR dataset.")
parser.add_argument('--i', type=str, required=True, help="Path to the input JSON file")
parser.add_argument('--o', type=str, required=True, help="Path to save output JSONL files")
parser.add_argument('--sample_size', type=int, default=100, help="Number of samples for the sample JSONL file")

args = parser.parse_args()

# Step 2: Read the source JSON file
with open(args.i, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Step 3: Extract the list of instances
instances = data.get('Instances', [])

# Check if we have enough instances
if len(instances) < 3:
    raise ValueError("Not enough instances to create few-shot examples.")

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
prompt = few_shot_case + data['Definition'][0] + "Please learn from the few-shot cases to see what content you have to output."

# Initialize lists to hold the full data and sample data
full_data = []
sample_data = []

# Step 4: Process each remaining instance
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
    if idx < args.sample_size:
        sample_data.append(output_dict)

# Step 5: Write the full data to a JSONL file
os.makedirs(args.o, exist_ok=True)
full_data_file = os.path.join(args.o, 'full_data.jsonl')
with open(full_data_file, 'w', encoding='utf-8') as f:
    for item in full_data:
        # Write each JSON object on a new line
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Step 6: Write the sample data to a separate JSONL file
sample_data_file = os.path.join(args.o, 'sample_data.jsonl')
with open(sample_data_file, 'w', encoding='utf-8') as f:
    for item in sample_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"Full data saved to {full_data_file}")
print(f"Sample data saved to {sample_data_file}")
