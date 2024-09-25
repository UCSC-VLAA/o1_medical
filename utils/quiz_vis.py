import json

def process_jsonl_file(filename):
    """
    Processes a JSONL file and returns a dictionary with sample_id as keys.
    Each value is a dictionary containing 'prompt', 'sampled', and 'correct' status.
    """
    data = {}
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 1  # Start from the second line (index 1)
    while i < len(lines):
        # Read the 'sampling' and 'match' entries
        sampling_line = lines[i-1].strip()  # Odd-numbered lines (index i-1)
        match_line = lines[i].strip()       # Even-numbered lines (index i)
        i += 2

        sampling_data = json.loads(sampling_line)
        match_data = json.loads(match_line)
        sample_id = sampling_data['sample_id']

        # Extract 'prompt' and 'sampled' from the sampling data
        prompt = sampling_data['data'].get('prompt', None)
        sampled = sampling_data['data'].get('sampled', None)

        # Extract 'correct' status from the match data
        correct = match_data['data'].get('correct', None)

        data[sample_id] = {
            'prompt': prompt,
            'sampled': sampled,
            'correct': correct
        }

    return data

def main():
    # Process both JSONL files
    B_data = process_jsonl_file('/workspace/evals/evallogs/lancet_cot_2024-09-17_00-34-33_o1-preview.jsonl')
    A_data = process_jsonl_file('/workspace/evals/evallogs/lancet_cot_2024-09-16_23-50-59_gpt-4-0125-preview.jsonl')
    # B_data = process_jsonl_file('/workspace/evals/evallogs/nejm_cot_2024-09-16_23-59-02_o1-preview.jsonl')
    # A_data = process_jsonl_file('/workspace/evals/evallogs/nejm_cot_2024-09-16_23-59-06_gpt-4-0125-preview.jsonl')
    # Find common sample_ids
    common_sample_ids = set(A_data.keys()).intersection(set(B_data.keys()))

    with open('/workspace/evals/evallogs/compare_lancet_4_o1.jsonl', 'w', encoding='utf-8') as fout:
        for sample_id in common_sample_ids:
            A_correct = A_data[sample_id]['correct']
            B_correct = B_data[sample_id]['correct']

            # Check if A answered correctly and B answered incorrectly
            if A_correct and not B_correct:
                # Extract and format the prompt
                prompt_list = A_data[sample_id]['prompt']
                prompt_text = '\n'.join([msg['content'] for msg in prompt_list]) if prompt_list else ''

                # Extract the first sampled answer from each model
                sampled_A = A_data[sample_id]['sampled'] if A_data[sample_id]['sampled'] else ''
                sampled_B = B_data[sample_id]['sampled'] if B_data[sample_id]['sampled'] else ''

                # Prepare the output data
                output_data = {
                    'prompt': prompt_text,
                    'sampled_A': sampled_A,
                    'sampled_B': sampled_B
                }

                # Write to the output file
                fout.write(json.dumps(output_data, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()
