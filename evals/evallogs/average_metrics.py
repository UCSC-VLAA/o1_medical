# read a jsonl file and calculate the average of the metrics
'''
Detailed Instructions:
1. Skip the first line
2. read each line as a json object, check its "type" field
3. if the type is "metrics", read its "data" field
4. for each key in the "data" field, add the value to the corresponding key in a dictionary
5. after reading all the lines, divide each value in the dictionary by the number of lines
6. write the dict back to the input file, add this line at the end of the file
'''

import json
import sys

def convert(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    metrics = {}
    for line in lines[1:]:
        obj = json.loads(line)
        if obj['type'] == 'metrics':
            for key, value in obj['data'].items():
                if key not in metrics:
                    metrics[key] = 0
                    
                if key == 'align_score':
                    try:
                        metrics[key] += value[0]
                    except:
                        metrics[key] += value
                        print(value)
                else:
                    metrics[key] += value
                    
                 if key == 'quality':
                    try:
                        metrics[key] += value[0]
                    except:
                        metrics[key] += value
                        print(value)
    for key in metrics:
        metrics[key] /= len(lines) - 1
    with open(file, 'a') as f:
        f.write(json.dumps({'type': 'average_metrics', 'data': metrics}) + '\n')
        
        
if __name__ == '__main__':
    floders = [
               'rct-text_2024-09-17_10-00-23_HumanF-MarkrAI',
               ]
    for floder in floders:
        file = floder + '/pub-llama-13B-v5.jsonl'
        convert(file)