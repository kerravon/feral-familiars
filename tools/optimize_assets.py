import os
import sys
import argparse
from PIL import Image, ImageOps

def remove_background(img, color_key="black"):
    """
    Makes a specific color transparent using a simple color key method.
    """
    img = img.convert("RGBA")
    datas = img.getdata()

    new_data = []
    
    # Define target color
    if color_key.lower() == "black":
        target = (0, 0, 0)
        threshold = 30 # Allow for near-black
    elif color_key.lower() == "white":
        target = (255, 255, 255)
        threshold = 225 # Allow for near-white
    else:
        # Default to black if unknown
        target = (0, 0, 0)
        threshold = 30

    for item in datas:
        # Check if the pixel color is close to our target color
        if color_key.lower() == "black":
            if item[0] < threshold and item[1] < threshold and item[2] < threshold:
                new_data.append((0, 0, 0, 0)) # Make transparent
            else:
                new_data.append(item)
        elif color_key.lower() == "white":
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                new_data.append((255, 255, 255, 0)) # Make transparent
            else:
                new_data.append(item)
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

def optimize_image(input_path, output_path, size=(512, 512), quality=80, bg_color=None):
    """
    Optimizes an image for Discord:
    1. Optionally removes solid background.
    2. Resizes to a standard square (512x512).
    3. Converts to WebP (highly efficient).
    """
    try:
        with Image.open(input_path) as img:
            # 1. Remove Background if requested
            if bg_color:
                img = remove_background(img, bg_color)
            elif img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 2. Resize
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            # 3. Save as WebP
            img.save(output_path, 'WEBP', quality=quality, method=6)
            
            original_size = os.path.getsize(input_path) / 1024
            new_size = os.path.getsize(output_path) / 1024
            
            print(f"✅ Optimized: {os.path.basename(input_path)}")
            print(f"   {original_size:.1f}KB -> {new_size:.1f}KB ({((original_size-new_size)/original_size)*100:.1f}% reduction)")
            if bg_color:
                print(f"   Background removal applied ({bg_color})")
            
    except Exception as e:
        print(f"❌ Error optimizing {input_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Optimize game assets for Discord (512x512 WebP)")
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("-o", "--output", help="Output directory (defaults to 'optimized_assets')")
    parser.add_argument("-q", "--quality", type=int, default=80, help="WebP quality (1-100, default 80)")
    parser.add_argument("--remove-bg", choices=["black", "white"], help="Attempt to make a solid color background transparent")
    
    args = parser.parse_args()
    
    output_dir = args.output or "optimized_assets"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if input is a directory or a single file
    if os.path.isdir(args.input):
        files = [f for f in os.listdir(args.input) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if not files:
            print("No image files found in directory.")
            return
        
        for f in files:
            in_path = os.path.join(args.input, f)
            filename = os.path.splitext(f)[0] + ".webp"
            out_path = os.path.join(output_dir, filename)
            optimize_image(in_path, out_path, quality=args.quality, bg_color=args.remove_bg)
    else:
        filename = os.path.splitext(os.path.basename(args.input))[0] + ".webp"
        out_path = os.path.join(output_dir, filename)
        optimize_image(args.input, out_path, quality=args.quality, bg_color=args.remove_bg)

if __name__ == "__main__":
    main()
