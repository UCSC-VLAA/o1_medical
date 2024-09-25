import csv
import json

# Input CSV file and output JSONL file
csv_file = '/workspace/ChallengeClinicalQA/medbullets/medbullets_op4.csv'
jsonl_file = '/workspace/evals/evals/registry/data/medbullets/full.jsonl'
system_prompt = "You are a helpful assistant that answers multiple choice questions about medical knowledge."
user_prompt = "The following are multiple choice questions (with answers) about medical knowledge."
constraint_promot = "Answer only with the correct option."
# Template for input prompt and ideal output
prompt_template = "**QUESTION:** {{question}} ANSWER CHOICES: A) {{opa}} B) {{opb}} C) {{opc}} D) {{opd}}"
ideal_template = "{{correct_option}}) {{correct_answer}}"
withsystem = False
# Open the CSV and JSONL file for reading and writing respectively
with open(csv_file, mode='r') as infile, open(jsonl_file, mode='w') as outfile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        # Create the prompt by replacing placeholders with actual data from the CSV
        prompt = prompt_template.replace('{{question}}', row['question'])\
                                .replace('{{opa}}', row['opa'])\
                                .replace('{{opb}}', row['opb'])\
                                .replace('{{opc}}', row['opc'])\
                                .replace('{{opd}}', row['opd'])
        
        # Get the correct answer and convert answer_idx to correct option (e.g., C -> C) <correct answer>)
        correct_option = row['answer_idx'].upper()
        ideal = ideal_template.replace('{{correct_option}}', correct_option)\
                              .replace('{{correct_answer}}', row['answer'])
        
        # Construct the final JSONL format
        if withsystem:
            jsonl_content = {
                "input": [{
                    "role": "system",
                    "content": system_prompt},
                    {
                    "role": "user",
                    "content": user_prompt + prompt + constraint_promot}],
                "ideal": ideal
            }
        else:
            jsonl_content = {
                "input": [{
                    "role": "user",
                    "content": system_prompt + user_prompt +  prompt + constraint_promot}],
                "ideal": ideal
            }

        # Write to JSONL file
        outfile.write(json.dumps(jsonl_content) + "\n")

print("Conversion completed. The output file is saved as", jsonl_file)
