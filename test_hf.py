from transformers import pipeline
import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0,1,2,3,4"
# os.environ['HF_HOME'] = '/home/ec2-user/disk/huggingface/'
# os.environ['TRANSFORMERS_CACHE'] = '/home/ec2-user/disk/huggingface/'

pipe = pipeline(model="HumanF-MarkrAI/pub-llama-13B-v5", device_map="auto", torch_dtype="float16")
for i in range(100000):
    print(i)
    out = pipe("Please introduce yourself.")
    print(out)
    input()