import json
import argparse
from PIL import Image
import cairosvg
from datasets import Dataset, DatasetDict
from huggingface_hub import create_repo, delete_repo
import os
import shutil
import numpy as np

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

def get_contrasting_background(img):
    """
    Analyze the non-transparent pixels of the image and return a contrasting background color.
    Returns white if the image is predominantly dark, black if it's predominantly light.
    """
    # Convert image to numpy array with alpha
    img_array = np.array(img)
    
    # Handle different modes
    if img.mode == 'RGBA':
        mask = img_array[:, :, 3] > 0
        foreground_pixels = img_array[mask][:, :3]
    elif img.mode == 'LA':
        mask = img_array[:, :, 1] > 0  # Alpha is the second channel
        foreground_pixels = img_array[mask][:, 0]  # Just the luminance channel
    else:
        foreground_pixels = img_array.reshape(-1, 3) if len(img_array.shape) == 3 else img_array.reshape(-1)
    
    if len(foreground_pixels) == 0:
        return (255, 255, 255)  # Default to white if image is fully transparent
    
    # Calculate average brightness
    if img.mode == 'LA' or len(foreground_pixels.shape) == 1:
        brightness = np.average(foreground_pixels)
    else:
        # Using perceived brightness formula: 0.299R + 0.587G + 0.114B
        brightness = np.average(
            foreground_pixels[:, 0] * 0.299 +
            foreground_pixels[:, 1] * 0.587 +
            foreground_pixels[:, 2] * 0.114
        )
    
    # Return white for dark images, black for light images
    return (0, 0, 0) if brightness > 127 else (255, 255, 255)

def resize_with_padding(im_path, images_output_dir, target_size=(448, 448), fill_color=None):
    """
    Resize image to target size with padding.
    The larger dimension will be scaled to target size while preserving aspect ratio.
    Then pad the smaller dimension with an automatically chosen contrasting color.
    """
    img = Image.open(im_path)
    if img.size == target_size:
        return im_path
    
    # If fill_color is not specified, choose it based on image content
    if fill_color is None and (img.mode == 'RGBA' or img.mode == 'LA'):
        fill_color = get_contrasting_background(img)
    elif fill_color is None:
        fill_color = (0, 0, 0)  # Default to black for non-transparent images
    
    # Convert RGBA or LA to RGB with background color
    if img.mode in ('RGBA', 'LA'):
        # Create a new background image with the chosen fill_color
        background = Image.new('RGB', img.size, fill_color)
        # Paste the image using its alpha channel as mask
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:  # LA mode
            background.paste(img.convert('L'), mask=img.split()[1])
        img = background
    
    # Calculate scaling ratio based on larger dimension
    ratio = max(target_size[0] / img.size[0], target_size[1] / img.size[1])
    new_size = tuple(int(dim * ratio) for dim in img.size)
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    new_img = Image.new("RGB", target_size, fill_color)
    left = (target_size[0] - new_size[0]) // 2
    top = (target_size[1] - new_size[1]) // 2
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
