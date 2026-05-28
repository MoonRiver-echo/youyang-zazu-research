from PIL import Image, ImageDraw, ImageFilter
import random
import math
import os

out_dir = r'C:\Users\lx\Desktop\前期准备\youyang-website\images'
os.makedirs(out_dir, exist_ok=True)

def generate_abstract(w=800, h=1000, palette=None, seed=0):
    random.seed(seed)
    img = Image.new('RGB', (w, h), palette['bg'])
    draw = ImageDraw.Draw(img)
    
    # Background gradient-ish noise
    for _ in range(3000):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        r = random.randint(0, 20)
        color = palette['accent1'] if random.random() > 0.7 else palette['bg']
        draw.ellipse([x, y, x+r, y+r], fill=color)
    
    # Large organic shapes
    for _ in range(8):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        rx = random.randint(100, 400)
        ry = random.randint(100, 400)
        draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=palette['shape'])
    
    # Flowing lines
    for _ in range(20):
        points = []
        x = random.randint(0, w)
        y = random.randint(0, h)
        for _ in range(random.randint(5, 15)):
            x += random.randint(-80, 80)
            y += random.randint(-80, 80)
            points.append((x, y))
        if len(points) > 1:
            draw.line(points, fill=palette['line'], width=random.randint(1, 3))
    
    # Central figure silhouette suggestion
    cx, cy = w//2, h//2
    # Abstract human-like form
    body_h = random.randint(300, 500)
    body_w = random.randint(80, 140)
    draw.ellipse([cx-body_w//2, cy-body_h//3, cx+body_w//2, cy+body_h//3], fill=palette['figure'])
    # Head
    head_r = random.randint(50, 80)
    draw.ellipse([cx-head_r, cy-body_h//3-head_r*2, cx+head_r, cy-body_h//3], fill=palette['figure'])
    
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    return img

stories = [
    {'name': 'wugang', 'seed': 1, 'palette': {'bg':(5,8,18), 'accent1':(40,50,80), 'shape':(20,30,60), 'line':(180,190,210), 'figure':(220,225,235)}},  # Moon silver
    {'name': 'xiuyueren', 'seed': 2, 'palette': {'bg':(15,12,8), 'accent1':(60,50,30), 'shape':(40,35,20), 'line':(200,180,140), 'figure':(230,215,180)}},  # Gold
    {'name': 'hutao', 'seed': 3, 'palette': {'bg':(10,5,5), 'accent1':(60,15,15), 'shape':(35,10,10), 'line':(160,60,60), 'figure':(200,80,80)}},  # Blood red
    {'name': 'liulushi', 'seed': 4, 'palette': {'bg':(8,12,8), 'accent1':(20,40,25), 'shape':(15,30,20), 'line':(140,160,130), 'figure':(180,200,170)}},  # Dark green
    {'name': 'yecha', 'seed': 5, 'palette': {'bg':(12,8,15), 'accent1':(40,20,50), 'shape':(25,15,35), 'line':(160,100,160), 'figure':(200,140,200)}},  # Purple
]

for s in stories:
    img = generate_abstract(800, 1000, s['palette'], s['seed'])
    img.save(os.path.join(out_dir, f"{s['name']}.jpg"), quality=90)
    print(f"Generated {s['name']}.jpg")

print("All images generated.")
