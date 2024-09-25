pip install -e .
pip install transformers

git clone https://github.com/yuh-zha/AlignScore
pip install ./AlignScore/.
pip install -r AlignScore/requirements.txt
wget -P ./AlignScore/ckpt https://huggingface.co/yzha/AlignScore/resolve/main/AlignScore-large.ckpt 
wget -P ./AlignScore/ckpt https://huggingface.co/yzha/AlignScore/resolve/main/AlignScore-base.ckpt


pip install spacy
python3 -m spacy download en_core_web_sm
pip install mauve-text 
pip install python-dotenv
pip install pytorch-ignite

git lfs install
git clone https://huggingface.co/datasets/UCSC-VLAA/o1_medical
rsync -a --ignore-existing ./o1_medical/data/ ./evals/registry/data/
rm -r  ./o1_medical