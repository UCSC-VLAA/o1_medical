# MedMCQA data converter

# BEFORE PROCEEDING: Download train.json from the official repo:
# https://github.com/MedMCQA/MedMCQA

# (direct data link: https://drive.google.com/uc?export=download&id=15VkJdq5eyWIkfb_aoD3oS8i4tScbHYky)

# Extract the archive and you are ready to go. :)

import json

input_file = "/workspace/dev.json"
output_file = "//workspace/dev.jsonl"


prompt = """
The following are multiple choice questions (with answers) about medical knowledge.
"""
# IMPORTANT: Option to include expert answer explanation for training purpose (in addition to correct answer)
include_expert_answer = False  # Set to True to include expert answer explanation

# IMPORTANT:
# Hard-coded limit (increase this to 182823 lines to use the full dataset)
line_limit = 300  # Increase this to 182823 to use the full dataset

def index_to_answer(index, obj):
    output = ""
    if index == 1:
        output = f"a) {obj['opa']}"
    elif index == 2:
        output = f"b) {obj['opb']}"
    elif index == 3:
        output = f"c) {obj['opc']}"
    elif index == 4:
        output = f"d) {obj['opd']}"
    if include_expert_answer:
        output += f"\n\n{obj['exp']}"
    return output

try:
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        i = 0
        for line in infile:
            if i >= line_limit:
                break
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as err:
                print(f"Failed to parse JSON: {err}")
                continue  # Skip lines that can't be parsed
            transformed_obj = {
                "input": [

                    {
                        "role": "user",
                        "content": f"{prompt}\n\nSubject: {obj['subject_name']}\n\n{obj['question']}\n\na) {obj['opa']}\nb) {obj['opb']}\nc) {obj['opc']}\nd) {obj['opd']}"
                    },
                ],
                "ideal": index_to_answer(obj["cop"], obj),
            }
            outfile.write(json.dumps(transformed_obj) + "\n")
            i += 1
    print("Output file created successfully.")
except Exception as e:
    print(f"Error: {e}")
