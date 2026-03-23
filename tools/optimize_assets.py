import os
import sys
import argparse
from PIL import Image

def optimize_image(input_path, output_path, size=(512, 512), quality=80):
    """
    Optimizes an image for Discord:
    1. Resizes to a standard square (512x512).
    2. Converts to WebP (highly efficient).
    3. Reduces file size significantly.
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGBA if not already (to preserve transparency)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Use high-quality Lanczos resampling for resizing
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Save as WebP
            img.save(output_path, 'WEBP', quality=quality, method=6)
            
            original_size = os.path.getsize(input_path) / 1024
            new_size = os.path.getsize(output_path) / 1024
            
            print(f"✅ Optimized: {os.path.basename(input_path)}")
            print(f"   {original_size:.1f}KB -> {new_size:.1f}KB ({((original_size-new_size)/original_size)*100:.1f}% reduction)")
            
    except Exception as e:
        print(f"❌ Error optimizing {input_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Optimize game assets for Discord (512x512 WebP)")
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("-o", "--output", help="Output directory (defaults to 'optimized_assets')")
    parser.add_argument("-q", "--quality", type=int, default=80, help="WebP quality (1-100, default 80)")
    
    args = parser.parse_args()
    
    output_dir = args.output or "optimized_assets"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if input is a directory or a single file
    if os.path.isdir(args.input):
        files = [f for f in os.listdir(args.input) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
            print("No image files found in directory.")
            return
        
        for f in files:
            in_path = os.path.join(args.input, f)
            filename = os.path.splitext(f)[0] + ".webp"
            out_path = os.path.join(output_dir, filename)
            optimize_image(in_path, out_path, quality=args.quality)
    else:
        filename = os.path.splitext(os.path.basename(args.input))[0] + ".webp"
        out_path = os.path.join(output_dir, filename)
        optimize_image(args.input, out_path, quality=args.quality)

if __name__ == "__main__":
    main()
