# 🖼 Asset Management & Optimization

To ensure a smooth user experience, all game assets (Essence and Spirit images) should be optimized for Discord.

## 🛠 Asset Optimization Tool
We have provided a tool to automate this process. It resizes images to **512x512px**, converts them to **WebP** format, and significantly reduces file size (typically by 70-90%).

### Prerequisites
Install the required dependencies:
```bash
pip install Pillow
```

### Usage
Run the script from the root directory:

**Optimize a single image:**
```bash
python tools/optimize_assets.py path/to/image.png
```

**Optimize a whole directory:**
```bash
python tools/optimize_assets.py path/to/raw_assets/
```

**Adjust Quality:**
If the output is too blurry, increase the quality (default is 80):
```bash
python tools/optimize_assets.py path/to/image.png -q 95
```

**Remove Solid Background:**
If your generated image has a pure black or white background, you can attempt to make it transparent:
```bash
# For black backgrounds
python tools/optimize_assets.py path/to/image.png --remove-bg black

# For white backgrounds
python tools/optimize_assets.py path/to/image.png --remove-bg white
```

The optimized images will be saved in the `optimized_assets/` folder.

## 📐 Image Standards
- **Size:** 512x512 pixels.
- **Format:** WebP (preferred) or PNG.
- **File Size:** Aim for **< 100 KB** per image.
- **Hosting:** Upload the optimized `.webp` files to a reliable host (like ImgBB or GitHub) and update `bot/utils/constants.py`.

## ✍️ Familiar Prompter Tool
We have provided a tool to help generate consistent AI image prompts for every combination of Spirit, Rarity, and Essence.

### Usage
Run the script from the root directory:
```bash
python tools/familiar_prompter.py --spirit [type] --rarity [rarity] --essence [element]
```

**Example:**
```bash
python tools/familiar_prompter.py --spirit feline --rarity legendary --essence fire
```
This will output a full, styled prompt ready to be pasted into DALL-E or Midjourney.
