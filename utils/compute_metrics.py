import json
from collections import defaultdict

def compute_average_metrics(jsonl_file):
    sums = defaultdict(float)  # Holds the sum of values for each key
    counts = defaultdict(int)  # Holds the count of occurrences for each key

    with open(jsonl_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            obj = json.loads(line)
            if obj.get("type") == "metrics":
                data = obj.get("data", {})
                for key, value in data.items():
                    if isinstance(value, list):
                        # If the value is a list, sum all elements in the list
                        if value:
                            sums[key] += sum(value)
                            counts[key] += len(value)
                    else:
                        sums[key] += value
                        counts[key] += 1

    # Calculate averages
    averages = {}
    for key in sums:
        averages[key] = sums[key] / counts[key]

    return averages

if __name__ == "__main__":
    jsonl_file = '/workspace/evals/evallogs/mednli_gen_2024-09-19_22-34-20_gpt-3.5-turbo.jsonl'  # Replace with your JSONL file path
    averages = compute_average_metrics(jsonl_file)
    for key, avg in averages.items():
        print(f"{key}: {avg}")
