import json
with open("results_with_images.json", "r") as f:
    results = json.load(f)

with open("internal.json", "r") as f:
    internal_ideologies = json.load(f)
internal_ideologies = [sis['Ideology'] for sis in internal_ideologies]
internal_ideologies_set = set(internal_ideologies)
assert len(internal_ideologies) == len(internal_ideologies_set)
internal_ideologies_set = set([rr for r in results for rr in r['Ideology']])

with open("external.json", "r") as f:
    external_ideologies = json.load(f)
external_ideologies = [sis['Ideology'] for sis in external_ideologies]
assert len(external_ideologies) == len(set(external_ideologies))

import random
random.seed(1)

abc = ['A', 'B', 'C']
task_data = []
for result in results:
    for image in result['images']:
        ideol_incorrect_internal = list(internal_ideologies_set - set(result['Ideology']))
        ideol_correct = random.sample(result['Ideology'], 1)
        ideol_incorrect_internal = random.sample(ideol_incorrect_internal, 1)
        ideol_incorrect_external = random.sample(external_ideologies, 1)
        random.shuffle(abc)
        correct = abc[0] # index 0 of the shuffled letters is correct
        questions = [
            (abc[0], ideol_correct[0]), 
            (abc[1], ideol_incorrect_internal[0]),
            (abc[2], ideol_incorrect_external[0]),
            ('D', "None of the above"),
            ('E', "I don't know")
        ]
        questions.sort(key=lambda x: x[0])
        question_text = "Answer with one letter (A, B, C, D, or E).\nWhich ideology best relates to the following image?\n"
        question_text += '\n'.join([f'{ans[0]}) {ans[1]}' for ans in questions])
        task_data.append({  
            'question': question_text,
            'answer_target': correct,
            'candidate_answers': [q[1] for q in questions],
            'incorrect_internal_answer': abc[1],
            'incorrect_external_answer': abc[2],
            'noneoftheabove_answer': 'D',
            'dontknow_answer': 'E',
            'superset_correct_answers': result['Ideology'],
            'image_path': image,
            'source_info': image,
            'locations': result['Location'],
            'symbol_title': result['title']
        })

import pandas as pd
print("ABC distribution:", pd.DataFrame([d['answer_target'] for d in task_data]).value_counts())

with open("task_data.json", "w") as f:
    json.dump(task_data, f, indent=4)
print("Wrote task_data.json")
