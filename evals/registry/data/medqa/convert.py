import json
import os
import random

# Define the customizable first content
first_content = (
"The following are multiple choice questions (with answers) about medical knowledge."
)
cot_content = "Before answering, reason in a step-by-step manner as to get the right answer, then conclude with the answer. Answer only with the full correct option. Your final output should strictly follow this format:<Reason>{your step-by-step reasoning}</Reason><Answer>{your answer}</Answer>"
# Define the subject (you can customize this as needed)


# Specify input and output file paths
input_file = '/workspace/MedQA-USMLE/questions/US/test.jsonl'    # Replace with your input JSON file path
output_dir = '/workspace/evals/evals/registry/data/medqa/'  # Replace with your desired output directory
output_file = os.path.join(output_dir, 'medqa_cot.jsonl')
sample_file = os.path.join(output_dir, 'medqa_cot_sample.jsonl')
sample_size = 50  # Specify the number of samples you want

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read all lines from the input file
with open(input_file, 'r') as f_in:
    lines = f_in.readlines()

# Process all lines and write to the full output file
with open(output_file, 'w') as f_out:
    for line in lines:
        sample = json.loads(line.strip())
        
        # Extract required fields with default empty values if not present
        question = sample.get("question", "")
        options = sample.get("options", {})
        answer_idx = sample.get("answer_idx", "")
        
        # Format the options
        formatted_options = ""
        for key in sorted(options.keys()):
            formatted_options += f"{key}) {options[key]}\n"
        formatted_options = formatted_options.strip()  # Remove trailing newline
        
        # Combine the question and options
        content_second_user = f"{question}\n\n{formatted_options}"
        
        # Find the ideal answer: "answer_idx) corresponding option text"
        ideal_option_text = options.get(answer_idx, "")
        ideal = f"{answer_idx}) {ideal_option_text}"
        
        # Create the "input" list of role-content dictionaries
        input_list = [
            {
                "role": "user",
                "content": first_content + content_second_user + cot_content
            },
        ]
        
        # Create the output JSON object
        output_obj = {
            "input": input_list,
            "ideal": ideal
        }
        
        # Write the JSON object as a line in the output JSONL file
        f_out.write(json.dumps(output_obj))
        f_out.write('\n')

# Create a sample file
sample_lines = random.sample(lines, min(sample_size, len(lines)))

with open(sample_file, 'w') as f_sample:
    for line in sample_lines:
        sample = json.loads(line.strip())
        
        # Extract required fields with default empty values if not present
        question = sample.get("question", "")
        options = sample.get("options", {})
        answer_idx = sample.get("answer_idx", "")
        
        # Format the options
        formatted_options = ""
        for key in sorted(options.keys()):
            formatted_options += f"{key}) {options[key]}\n"
        formatted_options = formatted_options.strip()  # Remove trailing newline
        
        # Combine the question and options
        content_second_user = f"{question}\n\n{formatted_options}"
        
        # Find the ideal answer: "answer_idx) corresponding option text"
        ideal_option_text = options.get(answer_idx, "")
        ideal = f"{answer_idx}) {ideal_option_text}"
        
        # Create the "input" list of role-content dictionaries
        input_list = [
            {
                "role": "user",
                "content": first_content + content_second_user + cot_content
            },
        ]
        
        
        # Create the output JSON object
        output_obj = {
            "input": input_list,
            "ideal": ideal
        }
        
        # Write the JSON object as a line in the sample JSONL file
        f_sample.write(json.dumps(output_obj))
        f_sample.write('\n')

print(f"Conversion completed successfully!")
print(f"Full dataset written to: {output_file}")
print(f"Sample dataset ({sample_size} entries) written to: {sample_file}")