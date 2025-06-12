import json
import os
import pytest

def test_all_images_are_labeled():
    """Test to ensure all images in images_std directory have corresponding labels."""
    with open('image_labels.json', 'r') as f:
        image_labels_dict = json.load(f)

    image_files = os.listdir('images_std')
    label_images = set(image_labels_dict.keys())
    
    # Get any missing or extra images
    unlabeled_images = set(image_files) - label_images
    extra_labels = label_images - set(image_files)
    
    # Provide more detailed error messages
    assert not unlabeled_images, f"Images missing labels: {unlabeled_images}"
    assert not extra_labels, f"Labels without corresponding images: {extra_labels}"
