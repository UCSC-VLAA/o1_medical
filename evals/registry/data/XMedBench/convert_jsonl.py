'''
Read from input_file and write to output_file in jsonl format
Detail: 
1. input file is a json file with the following format:
{
    "question": {question} (string),
    "options": {options} (string),
    "answer": {answer} (string)
}
2. output file is a jsonl file with the following format:
{
    "input":["role": "user', "content": "You are a doctor. You are attending a medical knowledge test{instructions}", role: "user", "content": "{input}" ], "ideal": {output}
}
'''


prompts = {
    'zh': '''你是资深的医学专家，现在正在参加专业医学知识的测试，需要回答如下的单项选择题：
问题：
{question}
选项：
{options}
        
注意，你的回答应该只包含选择的选项，比如(A),(B),(C),(D),(E)等，不要包含其它任何内容
    ''',
    'en': '''You are a senior medical expert and are now taking a professional medical knowledge test. You need to answer the following multiple-choice question:
Question: 
{question}
Options: 
{options}
        
Note that your answer should only include the chosen option, such as (A), (B), (C), (D), (E), etc., without any other content.
    ''',
    'es': '''Usted es un experto médico senior y ahora está realizando una prueba de conocimientos médicos profesionales. Debe responder a la siguiente pregunta de opción múltiple:
Pregunta: 
{question}
Opciones: 
{options}

Tenga en cuenta que su respuesta debe incluir solo la opción elegida, como (A), (B), (C), (D), (E), etc., sin ningún otro contenido.
    ''',
    'fr': '''Vous êtes un expert médical chevronné et vous passez actuellement un test de connaissances médicales professionnelles. Vous devez répondre à la question à choix multiples suivante :
Question : 
{question}
Options : 
{options}

Notez que votre réponse ne doit inclure que l'option choisie, comme (A), (B), (C), (D), (E), etc., sans aucun autre contenu.
    ''',
    'ar': '''أنت خبير طبي متمرس وتخضع الآن لاختبار في المعرفة الطبية المهنية. عليك الإجابة على سؤال الاختيار من متعدد التالي:
السؤال: 
{question}
الخيارات: 
{options}

لاحظ أن إجابتك يجب أن تتضمن فقط الخيار المحدد، مثل (A)، (B)، (C)، (D)، (E)، إلخ، دون أي محتوى آخر.
    ''',
    'hi': '''आप एक वरिष्ठ चिकित्सा विशेषज्ञ हैं और अब पेशेवर चिकित्सा ज्ञान की परीक्षा दे रहे हैं। आपको निम्नलिखित बहुविकल्पीय प्रश्न का उत्तर देना होगा:
प्रश्न: 
{question}
विकल्प: 
{options}

ध्यान दें कि आपके उत्तर में केवल चुना गया विकल्प शामिल होना चाहिए, जैसे (A), (B), (C), (D), (E) आदि, बिना किसी अन्य सामग्री के।  
    '''
}

import json
import os
import sys
import argparse


def convert_jsonl(input_file, output_file):
    
    language = input_file.split('.')[0].split('_')[-1]
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    with open(output_file, 'w') as f:
        for i, item in enumerate(data):
            question = item['question']
            options = item['options']
            answer = item['answer']
            prompt = prompts[language].format(question=question, options=options)
            f.write(json.dumps({
                "input": [
                    {"role": "user", "content": prompt},
                ],
                "ideal": [answer]
            }, ensure_ascii=False) + '\n')
            if i % 100 == 0:
                print(f'Convert {i} samples')
    # print(f'Convert {input_file} to {output_file} successfully!')
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='test_zh.json' ,help='input file')
    parser.add_argument('--output_file', type=str, default='test_zh.jsonl', help='output file')
    args = parser.parse_args()
    convert_jsonl(args.input_file, args.output_file)
    
if __name__ == '__main__':
    main()