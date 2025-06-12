"""
This is a simple script to faciliate labeling images from subdirectories of a LABELS/ directory.

It does the following:
1. Loads the labels from the LABELS directory
2. Saves the labels to a JSON file

The labeling process has already been performed, you don't need to reuse this script.
"""

import json
import os

label_cats = {}
all_files = []
for subdir in os.listdir('./LABELS'):
    print(subdir)
    label_cats[subdir] = os.listdir(f'./LABELS/{subdir}')
    all_files += label_cats[subdir]
all_files = list(set(all_files))

file_to_cats = {}
for file in all_files:
    file_to_cats[file] = []
    for subdir in label_cats:
        if file in label_cats[subdir]:
            file_to_cats[file].append(subdir)

only_other = []
for k,v in file_to_cats.items():
    if len(v) == 1 and v[0] == 'other':
        only_other.append(k)
assert len(only_other) == 0, "There are some images that are only labeled as other"

file_to_cats = {}
for file in all_files:
    file_to_cats[file] = []
    for subdir in label_cats:
        if file in label_cats[subdir]:
            if subdir != 'other':
                file_to_cats[file].append(subdir)

os.makedirs('assets', exist_ok=True)
with open(os.path.join('assets', 'image_labels.json'), 'w') as f:
    json.dump(file_to_cats, f, indent=4)
