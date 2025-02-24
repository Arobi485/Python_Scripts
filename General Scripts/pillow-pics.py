import random
from PIL import Image, ImageDraw

def generate_abstract_art(filename='abstract_art.png', img_size=(800, 800), num_shapes=20):
    # Create a new white image
    img = Image.new('RGB', img_size, color='white')
    draw = ImageDraw.Draw(img)

    # Generate random shapes
    for _ in range(num_shapes):
        shape_type = random.choice(['rectangle', 'ellipse'])
        
        # Generate top-left coordinates
        x1 = random.randint(0, img_size[0] - 2)
        y1 = random.randint(0, img_size[1] - 2)
        
        # Ensure that x2 > x1 and y2 > y1
        x2 = random.randint(x1 + 1, img_size[0] - 1)
        y2 = random.randint(y1 + 1, img_size[1] - 1)
        
        color = tuple(random.randint(0, 255) for _ in range(3))

        if shape_type == 'rectangle':
            draw.rectangle([x1, y1, x2, y2], fill=color)
        else:
            draw.ellipse([x1, y1, x2, y2], fill=color)

    # Save the image
    img.save(filename)
    print(f"Abstract art saved to {filename}")

if __name__ == '__main__':
    generate_abstract_art()