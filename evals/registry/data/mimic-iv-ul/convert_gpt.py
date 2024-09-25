import json
import os
output_dir = '/workspace/evals/evals/registry/data/mimic-iv-ul'
# Step 1: Customize the prompt and sample size
sample_size = 100  # You can change this number to specify how many samples you want in the sample JSONL file

# Step 2: Read the source JSON file
with open('/workspace/datasets/MedS-Bench/Text_summarization/task78_mimic_ultrasound_summarization.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Step 3: Extract the list of instances
instances = data.get('Instances', [])

few_shot_case = """
Case1: Input: "Minimal intra-abdominal fluid was observed within the right and left lower\nquadrants as well as adjacent to the bladder.", Output: "Minimal ascites. No paracentesis was performed."
Case2: Input: "There is a single live intrauterine gestation in cephalic presentation.  The\ncervix measures 3 cm in length.  An anterior placenta is noted with no\nevidence of abruption at this time.  The uterus has a normal gravid\nappearance.\n\nThe right ovary is poorly visualized however, grossly normal in appearance. \nDilated, patent veins are evident in the right adnexa measuring up to 14 mm in\ndiameter.\n\nThe left ovary has a normal appearance, is normal in size, and demonstrates\narterial and venous flow with color and spectral Doppler.  Immediately\nadjacent to the left ovary, there continues to be an oblong simple cyst which\nmeasures 6.7 x 3.4 x 6.2 cm, previously 6.6 x 3.7 x 6.3 cm.  There is no\ninternal vascularity or nodularity demonstrated within this cyst.", Output: "1. Single live intrauterine gestation.\n2. Stable simple left adnexal cyst which is unchanged in size and appearance\nwhen compared to prior ultrasound.  Recommend follow-up ultrasound after the\nbaby is born\n3. Normal appearing left ovary adjacent to the simple left adnexal cyst with\nno sonographic evidence of torsion .\n4. Dilated, patent right adnexal vessels.\n5. Poorly visualized right ovary however, grossly normal in appearance.\n\nNOTIFICATION:  The findings were discussed with ___, R.N.  In OB triage by\n___ on the telephone on ___ at 3:23 pm, 10 minutes after\ndiscovery of the findings."
Case3: Input: "RIGHT:\nThe right carotid vasculature has moderate atherosclerotic plaque.\nThe peak systolic velocity in the right common carotid artery is 67 cm/sec.\nThe peak systolic velocities in the proximal, mid, and distal right internal\ncarotid artery are 124, 95, and 73 cm/sec, respectively.  The peak end\ndiastolic velocity in the right internal carotid artery is 39 cm/sec.\nThe ICA/CCA ratio is 2.1.\nThe external carotid artery has peak systolic velocity of 166 cm/sec.\nThe vertebral artery is patent with antegrade flow.\n\nLEFT:\nThe left carotid vasculature has moderate atherosclerotic plaque.\nThe peak systolic velocity in the left common carotid artery is 70 cm/sec.\nThe peak systolic velocities in the proximal, mid, and distal left internal\ncarotid artery are 124, 81, and 76 cm/sec, respectively.  The peak end\ndiastolic velocity in the left internal carotid artery is 32 cm/sec.\nThe ICA/CCA ratio is 1.8.\nThe external carotid artery has peak systolic velocity of 82 cm/sec.\nThe vertebral artery is patent with antegrade flow.", Output: "40-59% stenosis of the right internal carotid artery.\n40-59% stenosis of the left internal carotid artery."
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
