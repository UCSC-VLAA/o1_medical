from evaluate import load
mauve = load('mauve')
predictions = ["Special Question: Who can provide research assistance for a high school freshman conducting a research report on Sudden Cardiac Arrest in Adolescence?",]
references = ["Where can I find information on sudden cardiac arrest in adolescents?",]
mauve_results = mauve.compute(predictions=predictions, references=references, seed=0)
print(mauve_results.mauve)



from evaluate import load
mauve = load('mauve')
predictions = ["hello world", "goodnight moon"]
references = ["hello world",  "goodnight moon"]
print(mauve.compute(predictions=predictions, references=references).mauve)