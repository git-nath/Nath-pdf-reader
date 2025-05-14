from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a white background
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue circle
    circle_margin = 10
    draw.ellipse(
        [(circle_margin, circle_margin), 
         (size - circle_margin, size - circle_margin)],
        fill=(0, 120, 215),  # Windows blue
        outline=(255, 255, 255, 0)
    )
    
    # Add text (N)
    try:
        font = ImageFont.truetype("segoeui.ttf", 150)
    except:
        font = ImageFont.load_default()
    
    text = "N"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size - text_width) // 2, (size - text_height) // 2 - 20)
    draw.text(position, text, font=font, fill=(255, 255, 255))
    
    # Save as ICO
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    icon_path = os.path.join(assets_dir, 'icon.ico')
    
    # Create ICO with multiple sizes
    img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print(f"Icon created at: {icon_path}")

if __name__ == "__main__":
    create_icon()
