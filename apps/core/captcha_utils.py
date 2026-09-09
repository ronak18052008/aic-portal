import random
import io
import base64
from PIL import Image, ImageDraw, ImageFont

def generate_captcha_data():
    """
    Generate a 4-character CAPTCHA with a mix of numbers and letters,
    and render it onto an image with anti-bot distortion and noise.
    Returns: (code, data_uri)
    """
    letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    digits = '23456789'
    
    # 4-character combination guaranteed to have both letters and digits
    # e.g., 2 letters + 2 digits shuffled
    chars = random.sample(letters, 2) + random.sample(digits, 2)
    random.shuffle(chars)
    code = ''.join(chars)
    
    width, height = 160, 52
    image = Image.new('RGB', (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(image)
    
    # Noise points / dots
    for _ in range(120):
        xy = (random.randint(0, width), random.randint(0, height))
        draw.point(xy, fill=(random.randint(140, 210), random.randint(140, 210), random.randint(160, 220)))
        
    # Distortion lines
    for _ in range(4):
        start = (random.randint(0, 30), random.randint(0, height))
        end = (random.randint(width - 30, width), random.randint(0, height))
        draw.line(
            [start, end],
            fill=(random.randint(100, 180), random.randint(100, 180), random.randint(150, 220)),
            width=2
        )
        
    try:
        font = ImageFont.truetype('arial.ttf', 30)
    except Exception:
        try:
            font = ImageFont.truetype('segoeui.ttf', 30)
        except Exception:
            font = ImageFont.load_default(size=26)
        
    char_colors = [
        (15, 76, 129),   # Deep classic blue
        (67, 56, 202),   # Indigo
        (180, 83, 9),    # Amber/orange
        (13, 148, 136),  # Teal
        (159, 18, 57),   # Rose/crimson
        (30, 41, 59),    # Slate charcoal
    ]
    
    for i, char in enumerate(code):
        char_img = Image.new('RGBA', (36, 44), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((4, 2), char, font=font, fill=random.choice(char_colors))
        rotated = char_img.rotate(random.randint(-24, 24), expand=1, resample=Image.BICUBIC)
        x = 18 + i * 32
        y = (height - rotated.size[1]) // 2
        image.paste(rotated, (x, y), rotated)
        
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    data_uri = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
    return code, data_uri
