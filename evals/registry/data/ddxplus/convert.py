import json

def convert_json_to_jsonl(source_file, full_file, sample_file, sample_size):
    with open(source_file, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    # Expect 'Definition' key to be present, raise an error if not
    definition = source_data["Definition"]
    if isinstance(definition, list):
        definition = definition[0].strip()
    else:
        definition = definition.strip()

    # Expect 'Instances' key to be present
    instances = source_data["Instances"]

    # Writing the full JSONL file
    with open(full_file, 'w', encoding='utf-8') as full_out:
        for instance in instances:
            input_content = instance["input"].strip()
            output_content = instance["output"].strip()

            # Extract the diagnosis from output_content
            diagnosis_prefix = "The diagnosis result is "
            if output_content.startswith(diagnosis_prefix):
                diagnosis = output_content[len(diagnosis_prefix):].strip()
                # Remove any trailing punctuation
                diagnosis = diagnosis.rstrip('.')
            else:
                diagnosis = output_content

            # Build the target JSON object
            target_object = {
                "input": [
                    {"role": "system", "content": definition},
                    {"role": "user", "content": input_content}
                ],
                "ideal": diagnosis
            }

            # Write the JSON object as a line in the JSONL file
            json_line = json.dumps(target_object, ensure_ascii=False)
            full_out.write(json_line + '\n')

    # Writing the sample JSONL file with specified number of lines
    with open(sample_file, 'w', encoding='utf-8') as sample_out:
        for instance in instances[:sample_size]:
            input_content = instance["input"].strip()
            output_content = instance["output"].strip()

            # Extract the diagnosis from output_content
            diagnosis_prefix = "The diagnosis result is "
            if output_content.startswith(diagnosis_prefix):
                diagnosis = output_content[len(diagnosis_prefix):].strip()
                # Remove any trailing punctuation
                diagnosis = diagnosis.rstrip('.')
            else:
                diagnosis = output_content

            # Build the target JSON object
            target_object = {
                "input": [
                    {"role": "system", "content": definition},
                    {"role": "user", "content": input_content}
                ],
                "ideal": diagnosis
            }

            # Write the JSON object as a line in the sample JSONL file
            json_line = json.dumps(target_object, ensure_ascii=False)
            sample_out.write(json_line + '\n')

# Usage example
convert_json_to_jsonl(
    '/workspace/datasets/MedS-Bench/Diagnosis/task130_DDXPlus_text_classification_test_new.json',
    '/workspace/evals/evals/registry/data/ddxplus/test_full_w_system.jsonl',
    '/workspace/evals/evals/registry/data/ddxplus/test_sample_w_system.jsonl',
    sample_size=1500  # Specify the number of samples for the sample file
)
