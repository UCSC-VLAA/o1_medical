import json
import os
output_dir = '/workspace/evals/evals/registry/data/medqsum'
# Step 1: Customize the prompt and sample size
sample_size = 10  # You can change this number to specify how many samples you want in the sample JSONL file

# Step 2: Read the source JSON file
with open('/workspace/datasets/MedS-Bench/Text_summarization/task114_medqsum_text_summurization.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Step 3: Extract the list of instances
instances = data.get('Instances', [])

few_shot_case = """
Case1: Input: "SUBJECT: just a question\nMESSAGE: hi..just wanna ask... 1.how the aspirin can affect the ear? 2. what is the cause of suddenly ringging in the ear? isn't dangerous? tq.. :)"
        Output: "What causes ringing in the ear, and can aspirin affect the ear?"
Case2: Input: "Dear Doc,\nI am now turning 40years in November and all my life I have desired\nmiserably for a divine intervention to restore my smell sense so that I can\nfully appreciate and participate in this one life on earth. I truly wish to\nbe a part of your research if need be because the disorder had greatly\naffected my life. If you already have medical drugs to cure and restore my\nsmell sense kindly give information on how I can acquire to benefit from\nthis. I pray that God the Creator gracefully grants me favour with this so\nthat I can enjoy the beauty of His creation in this world, with respect to\nsmell, before I depart to continue with Him in heaven. Cheers for now as I\nwait to hear from you.\n[NAME], Ms.\nSmell disorder (anosmia) patient /sufferer,\nwriting from [LOCATION]. Cell: [CONTACT], [CONTACT].",
        Output: "What are the treatments for anosmia?"
Case3: Input: "SUBJECT: cosmetic leg shortening surgery\nMESSAGE  Hi,  I am a tall girl(5'8"), who wants to undergo leg shortening sugery of 2 inches for cosmetic purpose. It would be good if I can get more information about it. I would like to know the cost of this surgery, the recovery time and the risks associated with it. How long should I stay in the hospital?  Thanks and regards", output: "Where can I find information on leg shortening surgery, including risks, cost, and recovery time?"
        Output: "Where can I find information on leg shortening surgery, including risks, cost, and recovery time?"
        
"""
prompt = few_shot_case + data['Definition'][0] + "Please learn from the few-shot cases to see what content you have to output." 
# Initialize lists to hold the full data and sample data
full_data = []
sample_data = []

# Step 4: Process each instance
for idx, instance in enumerate(instances):
    # Extract the 'input' and 'output' from each instance
    input_text = instance.get('input', '')
    output_text = instance.get('output', '')

    # Construct the new JSON object as per the required format
    output_dict = {
        "input": [
            {
                "role": "user",
                "content": f"{prompt} {input_text}"
            }
        ],
        "ideal": output_text
    }
    
    
    # output_dict = {
    #             "input": [
    #                 {"role": "system", "content": prompt},
    #                 {"role": "user", "content": input_text}
    #             ],
    #             "ideal": output_text
    #         }

    # Add the new object to the full data list
    full_data.append(output_dict)

    # If the current index is less than the sample size, add to sample data
    if idx < sample_size:
        sample_data.append(output_dict)

# Step 5: Write the full data to a JSONL file
with open(os.path.join(output_dir,'full_data.jsonl'), 'w', encoding='utf-8') as f:
    for item in full_data:
        # Write each JSON object on a new line
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Step 6: Write the sample data to a separate JSONL file
with open(os.path.join(output_dir, 'sample_data.jsonl'), 'w', encoding='utf-8') as f:
    for item in sample_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
