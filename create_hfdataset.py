import json
import argparse
from PIL import Image
from datasets import Dataset, DatasetDict
from huggingface_hub import create_repo, delete_repo
import os


def prepare_dataset(raw_data):
    processed_data = []
    for item in raw_data:        # Load and store the image in the dataset
        try:
            image = Image.open(item['image_path']).convert('RGB')
            item['image'] = image  # replace path with actual image object
            processed_data.append(item)
        except Exception as e:
            print(f"Error loading image {item['image_path']}: {e}")

    # Create dataset and wrap it in DatasetDict with 'test' split
    dataset = Dataset.from_list(processed_data)
    dataset_dict = DatasetDict({"validation": dataset})
    return dataset_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_images", type=int, default=-1)
    parser.add_argument("--task_data_path", type=str, default="task_data_fc.json")
    parser.add_argument("--dataset_name", type=str, default="mmbeliefs_mcq_fc")
    parser.add_argument("--private", type=bool, default=True)
    args = parser.parse_args()

    with open(args.task_data_path, "r") as f:
        task_data = json.load(f)
    num_images = min(args.num_images, len(task_data)) if args.num_images > 0 else len(task_data)
    if args.num_images > num_images:
        print(f"Warning: the specified num_images is greater than the number of images in the dataset. Using {num_images} images.")
    raw_data = task_data[:min(num_images, len(task_data))]
    dataset = prepare_dataset(raw_data)

    try:
        delete_repo(args.dataset_name, repo_type="dataset")
    except:
        pass
    create_repo(args.dataset_name, repo_type="dataset", private=args.private)
    dataset.push_to_hub(args.dataset_name)

    print(f"Dataset {args.dataset_name} ({'private' if args.private else 'public'}) with {num_images} images pushed to Hugging Face Hub")