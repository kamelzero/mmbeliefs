import json
with open("results_with_images_std.json", "r") as f:
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

# Initialize counters for each answer type in each position
position_counts = {
    'correct': {'A': 0, 'B': 0, 'C': 0},
    'incorrect_internal': {'A': 0, 'B': 0, 'C': 0},
    'incorrect_external': {'A': 0, 'B': 0, 'C': 0}
}

abc = ['A', 'B', 'C']
task_data = []
for result in results:
    for image in result['images']:
        ideol_incorrect_internal = list(internal_ideologies_set - set(result['Ideology']))
        ideol_correct = random.sample(result['Ideology'], 1)
        ideol_incorrect_internal = random.sample(ideol_incorrect_internal, 1)
        ideol_incorrect_external = random.sample(external_ideologies, 1)
        
        # Create answer mapping
        answers = {
            'correct': ideol_correct[0],
            'incorrect_internal': ideol_incorrect_internal[0],
            'incorrect_external': ideol_incorrect_external[0]
        }
        
        # Find the most balanced arrangement
        min_imbalance = float('inf')
        best_arrangement = None
        
        for perm in [('correct', 'incorrect_internal', 'incorrect_external'),
                    ('correct', 'incorrect_external', 'incorrect_internal'),
                    ('incorrect_internal', 'correct', 'incorrect_external'),
                    ('incorrect_internal', 'incorrect_external', 'correct'),
                    ('incorrect_external', 'correct', 'incorrect_internal'),
                    ('incorrect_external', 'incorrect_internal', 'correct')]:
            # Calculate imbalance score for this arrangement
            imbalance = sum(position_counts[ans_type][pos] 
                          for ans_type, pos in zip(perm, abc))
            if imbalance < min_imbalance:
                min_imbalance = imbalance
                best_arrangement = perm
        
        # Update position counts and create questions
        questions = []
        for ans_type, pos in zip(best_arrangement, abc):
            position_counts[ans_type][pos] += 1
            questions.append((pos, answers[ans_type]))
            if ans_type == 'correct':
                correct = pos
        
        questions.sort(key=lambda x: x[0])
        questions += ('D', "None of the above"),
        question_text = "Answer with one letter (A, B, C, D); do not provide any other text.\nWhich ideology best relates to the following image?\n"
        question_text += '\n'.join([f'{ans[0]}) {ans[1]}' for ans in questions])
        
        # Find which positions contain incorrect answers
        incorrect_internal_pos = next(pos for ans_type, pos in zip(best_arrangement, abc) if ans_type == 'incorrect_internal')
        incorrect_external_pos = next(pos for ans_type, pos in zip(best_arrangement, abc) if ans_type == 'incorrect_external')
        
        task_data.append({  
            'question': question_text,
            'answer_target': correct,
            'candidate_answers': [q[1] for q in questions],
            'incorrect_internal_answer': incorrect_internal_pos,
            'incorrect_external_answer': incorrect_external_pos,
            'noneoftheabove_answer': 'D',
            'superset_correct_answers': result['Ideology'],
            'image_path': image,
            'source_info': image,
            'locations': result['Location'],
            'symbol_title': result['title']
        })

import pandas as pd
print("\nABC distribution for correct answers:", pd.DataFrame([d['answer_target'] for d in task_data]).value_counts())
print("\nPosition counts for each answer type:")
for ans_type, counts in position_counts.items():
    print(f"{ans_type}:", counts)

fn = "task_data_fc.json"
with open(fn, "w") as f:
    json.dump(task_data, f, indent=4)
print(f"\nWrote {fn}")
