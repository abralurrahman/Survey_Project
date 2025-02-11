from PIL import Image
import os

# Define the directory containing your images and the target size
image_dir = "static/images"
output_dir = "static/resized_images"
target_size = (150, 150)  # Increased from 150x150 for better visibility

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Loop through all images in the directory
for filename in os.listdir(image_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
        img_path = os.path.join(image_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Open and resize the image while maintaining aspect ratio
        with Image.open(img_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Calculate aspect ratio
            aspect = img.width / img.height

            # Determine new dimensions maintaining aspect ratio
            if aspect > 1:
                new_width = target_size[0]
                new_height = int(target_size[1] / aspect)
            else:
                new_height = target_size[1]
                new_width = int(target_size[0] * aspect)

            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create new image with padding to maintain square aspect
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            paste_x = (target_size[0] - new_width) // 2
            paste_y = (target_size[1] - new_height) // 2
            new_img.paste(img_resized, (paste_x, paste_y))

            # Save the final image
            new_img.save(output_path, quality=95)

print("All images resized and saved to:", output_dir)
