import json
import os
import glob
from alignscore import AlignScore
from tqdm import tqdm

# Initialize the scorer
scorer = AlignScore(
    model='roberta-base',
    batch_size=1,
    device='cuda:0',
    ckpt_path='./AlignScore/ckpt/AlignScore-large.ckpt',
    evaluation_mode='nli_sp'
)

# Specify the directory where the .jsonl files are located
jsonl_dir = '/workspace/evals/evallogs'  # <-- Specify the correct directory

# Specify the output file
output_file = '/workspace/evals/align_scores_output_c.txt'  # <-- Specify the correct output path

# List of allowed first words (prefixes) to filter the .jsonl files
allowed_prefixes = ['chatDoctor']  # <-- Specify the allowed prefixes

# Get all .jsonl files in the directory
jsonl_files = glob.glob(os.path.join(jsonl_dir, '*.jsonl'))
# Function to compute the align scores and output results
def compute_align_scores(jsonl_files):
    with open(output_file, 'w') as out_f:
        for jsonl_file in jsonl_files:
            # Get the file name without the directory path
            file_name = os.path.basename(jsonl_file)
            # Extract the first word before the first underscore
            prefix = file_name.split('_')[0]

            # Only process files whose prefix is in the allowed list
            if prefix in allowed_prefixes:
                align_scores = []
                try:
                    with open(jsonl_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in tqdm(lines, desc=f"Processing {file_name}", unit="line"):
                            try:
                                data = json.loads(line)
                                if 'type' in data.keys() and data.get('type') == 'match':
                                    sampled = data['data']['sampled']
                                    correct_answer = data['data']['options'][0]
                                    try:
                                        # Score the sampled and correct_answer pair
                                        align_score = scorer.score(contexts=[correct_answer], claims=[sampled])
                                        if isinstance(align_score, list) and len(align_score) > 0:
                                            align_score = align_score[0]  # Extract the first element if it's a list

                                        align_scores.append(align_score)
                                    except Exception as e:
                                        print(f"Error computing score for {jsonl_file}: {e}")
                                        continue
                            except Exception as e:
                                print(f"Error processing line: {e}")
                                continue
                    
                    # Calculate the average score for the current jsonl file
                    if len(align_scores) > 0:
                        average_score = sum(align_scores) / len(align_scores)
                    else:
                        average_score = 0
                    
                    # Write the result to the output file
                    out_f.write(f"{file_name}: {average_score}\n")
                    out_f.flush()  # Ensure the buffer is flushed
                    print(f"Processed {jsonl_file}, Average Align Score: {average_score}")

                except FileNotFoundError as e:
                    print(f"File not found: {jsonl_file}")
                    continue

# Run the function to compute scores
compute_align_scores(jsonl_files)