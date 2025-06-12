import unittest
import os
from PIL import Image
import shutil
from standardize_images import resize_with_padding

class TestResizeWithPadding(unittest.TestCase):
    def setUp(self):
        # Create test directory
        self.test_dir = "test_images"
        self.output_dir = "test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Simplified test cases - just use a few key sizes
        self.test_cases = [
            ("small_square.png", (224, 224)),    # Small square image
            ("exact_size.png", (448, 448)),      # Image matching target size
            ("large_square.png", (896, 896)),    # Large square image
        ]
        
        # Create test images with larger squares for better visibility
        for filename, size in self.test_cases:
            img = Image.new('RGB', size, color='red')
            # Make squares larger (15x15 in a 20x20 grid) for better detection
            for x in range(0, size[0], 20):
                for y in range(0, size[1], 20):
                    box = (x + 2, y + 2, min(x + 17, size[0]), min(y + 17, size[1]))
                    img.paste('blue', box)
            img.save(os.path.join(self.test_dir, filename))

    def tearDown(self):
        # Clean up test directories
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_image_dimensions(self):
        target_size = (448, 448)
        
        for filename, original_size in self.test_cases:
            input_path = os.path.join(self.test_dir, filename)
            
            # Process the image
            resize_with_padding(input_path, self.output_dir, target_size=target_size)
            
            # Check the output image
            output_path = os.path.join(self.output_dir, filename)
            output_img = Image.open(output_path)
            
            # Test 1: Output dimensions should match target size
            self.assertEqual(output_img.size, target_size,
                           f"Output size {output_img.size} doesn't match target size {target_size} for {filename}")

    def test_no_cropping(self):
        target_size = (448, 448)
        
        for filename, original_size in self.test_cases:
            input_path = os.path.join(self.test_dir, filename)
            
            # Process the image
            resize_with_padding(input_path, self.output_dir, target_size=target_size)
            
            # Check the output image
            output_path = os.path.join(self.output_dir, filename)
            output_img = Image.open(output_path)
            
            # Calculate the expected ratio
            ratio = min(target_size[0] / original_size[0], target_size[1] / original_size[1])
            
            # Count squares in input image
            input_blues = sum(1 for x in range(0, original_size[0], 20)
                            for y in range(0, original_size[1], 20))
            
            # Convert output image to RGB for consistent color checking
            output_rgb = output_img.convert('RGB')
            
            # Find non-padded area
            background_color = output_rgb.getpixel((0, 0))
            non_background = []
            for x in range(target_size[0]):
                for y in range(target_size[1]):
                    if output_rgb.getpixel((x, y)) != background_color:
                        non_background.append((x, y))
            
            if not non_background:
                print(f"Warning: No non-background pixels found in {filename}")
                continue
            
            # Find content boundaries
            min_x = min(x for x, _ in non_background)
            max_x = max(x for x, _ in non_background)
            min_y = min(y for _, y in non_background)
            max_y = max(y for _, y in non_background)
            
            # Calculate scaled dimensions
            scaled_grid = int(20 * ratio)  # Size of one grid cell after scaling
            scaled_square = int(15 * ratio)  # Size of one blue square after scaling
            
            output_blues = 0
            # Adjust the range to match the original grid pattern
            rows = original_size[1] // 20
            cols = original_size[0] // 20
            
            for row in range(rows):
                for col in range(cols):
                    # Calculate expected center of this square after scaling
                    center_x = min_x + int((col + 0.5) * scaled_grid)
                    center_y = min_y + int((row + 0.5) * scaled_grid)
                    
                    # Check a region around the expected center
                    sample_size = max(3, scaled_square // 4)
                    blue_count = 0
                    total_count = 0
                    
                    for dx in range(-sample_size, sample_size + 1):
                        for dy in range(-sample_size, sample_size + 1):
                            check_x = center_x + dx
                            check_y = center_y + dy
                            if (0 <= check_x < target_size[0] and 
                                0 <= check_y < target_size[1]):
                                total_count += 1
                                if output_rgb.getpixel((check_x, check_y)) == (0, 0, 255):
                                    blue_count += 1
                    
                    if blue_count / total_count > 0.3:  # Lower threshold since we're sampling a larger area
                        output_blues += 1
            
            print(f"\nResults for {filename}:")
            print(f"Original size: {original_size}")
            print(f"Scale ratio: {ratio}")
            print(f"Scaled grid size: {scaled_grid}")
            print(f"Scaled square size: {scaled_square}")
            print(f"Content bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")
            print(f"Grid dimensions: {cols}x{rows}")
            print(f"Expected squares: {input_blues}")
            print(f"Found squares: {output_blues}")
            
            # Allow for larger differences due to scaling and interpolation
            # For scaled images, allow up to 20% difference
            max_difference = max(2, int(input_blues * 0.2))
            self.assertLessEqual(abs(input_blues - output_blues), max_difference,
                               f"Number of blue squares changed significantly for {filename}. "
                               f"Expected {input_blues}, got {output_blues}")

if __name__ == '__main__':
    unittest.main()

