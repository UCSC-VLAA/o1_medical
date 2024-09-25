import json
import random
import os

input_file = '/workspace/pubmedqa/data/test_set.json'    # Replace with your input JSON file path
output_dir = '/workspace/evals/evals/registry/data/pubmedqa/'  # Replace with your desired output directory
output_file = os.path.join(output_dir, 'pubmedqa_w_system.jsonl')
sample_file = os.path.join(output_dir, 'pubmedqa_sample_w_system.jsonl')
sample_size = 50  # Specify the number of samples you want
prompt = """
You are a highly intelligent doctor who answers the following multiple choice question correctly.\nOnly write the answer down.
"""
# Option mapping for the ideal answer
option_mapping = {
    'yes': 'A) yes',
    'no': 'B) no',
    'maybe': 'C) maybe'
}

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read the input JSON file
with open(input_file, 'r') as f_in:
    data = json.load(f_in)

# Function to process and write a sample
def process_and_write_sample(sample_id, sample, file, prompt):
    question = sample.get("QUESTION", "")
    contexts = sample.get("CONTEXTS", [])
    reasoning_required_pred = sample.get("final_decision", "").lower()

    contexts_str = "\n".join(contexts)
    combined_context = f"Context: {contexts_str}"
    formatted_question = f"Question: {question}"
    options = "A) yes\nB) no\nC) maybe"
    content = f"{prompt}\n{combined_context}\n\n{formatted_question}\n\n{options}"
    ideal = option_mapping.get(reasoning_required_pred, "")

    input_list = [
                    {"role": "system", "content": f"{prompt}\n"},
                    {"role": "user", "content": f"{combined_context}\n\n{formatted_question}\n\n{options}"}
    ]
    

    output_obj = {
        "input": input_list,
        "ideal": ideal
    }

    file.write(json.dumps(output_obj))
    file.write('\n')

# Process all samples and write to the full output file
with open(output_file, 'w') as f_out:
    for sample_id, sample in data.items():
        process_and_write_sample(sample_id, sample, f_out, prompt)

# Select random samples and write to the sample file
sample_ids = random.sample(list(data.keys()), min(sample_size, len(data)))
with open(sample_file, 'w') as f_sample:
    for sample_id in sample_ids:
        process_and_write_sample(sample_id, data[sample_id], f_sample, prompt)

print(f"Conversion completed successfully!")
print(f"Full output file: {output_file}")
print(f"Sample file with {len(sample_ids)} entries: {sample_file}")