

Prompt = '''You are a medical professional and you have been asked to answer a question based on the patient note provided.
The patient note is a record of a patient's visit to the doctor. 
Note that you should not provide a diagnosis, but rather only answer the question based on the information provided in the note.
Your response should be a numerical value, which is the answer to the question.
'''

input_format = '''
Patient Note:
{Note}
Question:
{Question}
'''

### read the input file, which is a parquet file, and generate the jsonl file
# each line in the jsonl file is a json object with the following keys
'''
read the input file, which is a parquet file, and generate the jsonl file
each line in the jsonl file is a json object with the following keys
{
    "input": [
     {"role": "system", "content": Prompt},
     {"role": "user", "content": input_format.format(Note=note, Question=question)}
    ],
    "ideal": GroundTruth Answer
}
'''

import pandas as pd
import json

input_file = 'test-00000-of-00001.parquet'
output_file = 'full.jsonl'
sample_file = 'sample.jsonl'

sample_num = 50

df = pd.read_parquet(input_file)
with open(output_file, 'w') as f:
    for i, row in df.iterrows():
        note = row['Patient Note']
        question = row['Question']
        answer = row['Ground Truth Answer']
        
        # dict_line = {
        #     "input": [
        #         {"role": "system", "content": Prompt},
        #         {"role": "user", "content": input_format.format(Note=note, Question=question)}
        #     ],
        #     "ideal": answer
        # }
        
        dict_line = {
            "input": [
                {"role": "user",  "content": Prompt + input_format.format(Note=note, Question=question)}
            ],
            "ideal": answer
        }
        
        json_line = json.dumps(dict_line)
        f.write(json_line + '\n')

with open(sample_file, 'w') as f:
    for i, row in df.sample(sample_num).iterrows():
        note = row['Patient Note']
        question = row['Question']
        answer = row['Ground Truth Answer']
        
        # dict_line = {
        #     "input": [
        #         {"role": "system", "content": Prompt},
        #         {"role": "user", "content": input_format.format(Note=note, Question=question)}
        #     ],
        #     "ideal": answer
        # }
        
        dict_line = {
            "input": [
                {"role": "user",  "content": Prompt + input_format.format(Note=note, Question=question)}
            ],
            "ideal": answer
        }
        
        json_line = json.dumps(dict_line)
        f.write(json_line + '\n')
        

print('Done!')

