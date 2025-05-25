import json
import argparse
from PIL import Image
import cairosvg
from datasets import Dataset, DatasetDict
from huggingface_hub import create_repo, delete_repo
import os
import shutil

def compress_image(in_path, max_size_mb=5):
    quality = 95
    MAX_SIZE_BYTES = max_size_mb * 1024 * 1024
    while quality > 10:
        img = Image.open(in_path).convert("RGB")
        suffix = os.path.splitext(in_path)[1]
        out_path = in_path.replace(suffix, f'_compressed{suffix}')
        img.save(out_path, format='JPEG', optimize=True, quality=quality)
        if os.path.getsize(out_path) < MAX_SIZE_BYTES:
            return out_path
        quality -= 5
    return None

def check_valid_image_size(im_path, max_size_mb=5):
    MAX_SIZE_BYTES = max_size_mb * 1024 * 1024
    size = os.path.getsize(im_path)
    return size <= MAX_SIZE_BYTES

def resize_with_padding(im_path, images_output_dir, target_size=(448, 448), fill_color=(0, 0, 0)):
    """
    Resize image to target size with padding.
    Save the resized image to the same path.
    """
    img = Image.open(im_path)
    if img.size == target_size:
        return im_path
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    new_img = Image.new("RGB", target_size, fill_color)
    left = (target_size[0] - img.size[0]) // 2
    top = (target_size[1] - img.size[1]) // 2
    new_img.paste(img, (left, top))
    new_img.save(os.path.join(images_output_dir, os.path.basename(im_path)))
    return im_path

def prepare_dataset(results_input_path, results_output_path, images_output_dir, max_size_mb=5, verbose=False):
    with open(results_input_path, "r") as f:
        results = json.load(f)

    all_new_image_paths = []
    for item in results:
        new_image_paths = []
        for image_path in item['images']:
            # if SVG, convert to PNG
            if image_path.endswith('.svg'):
                if verbose:
                    print(f"Converting {image_path} to PNG")
                new_path = os.path.join(images_output_dir, os.path.basename(image_path.replace('.svg', '.png')))
                cairosvg.svg2png(url=image_path, write_to=new_path)
                new_image_paths.append(images_output_dir + '/' + os.path.basename(new_path))
                if verbose:
                    print(f"Converted {image_path} to {new_image_paths[-1]}")
            else:
                new_image_paths.append(images_output_dir + '/' + os.path.basename(image_path))
                shutil.copy(image_path, new_image_paths[-1])
                if verbose:
                    print(f"Copied {image_path} to {new_image_paths[-1]}")
        item['images'] = new_image_paths

        for image_path in item['images']:
            resize_with_padding(image_path, images_output_dir)

            if not check_valid_image_size(image_path):
                print(f"Warning: Image {image_path} is > {max_size_mb}MB.")
 
    with open(results_output_path, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_input_path", type=str, default="results_with_images.json")
    parser.add_argument("--results_output_path", type=str, default="results_with_images_std.json")
    parser.add_argument("--images_output_dir", type=str, default="images_std")
    parser.add_argument("--max_size_mb", type=int, default=5)
    args = parser.parse_args()

    os.makedirs(args.images_output_dir, exist_ok=True)
    prepare_dataset(args.results_input_path, args.results_output_path, args.images_output_dir, args.max_size_mb)
