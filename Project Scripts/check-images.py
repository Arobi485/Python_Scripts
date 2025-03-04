from pathlib import Path
import os

def analyze_dataset(dataset_path):
    print("Dataset Analysis")
    print("===============")
    
    # Check training images
    train_img_path = Path(dataset_path) / 'images' / 'train'
    train_label_path = Path(dataset_path) / 'labels' / 'train'
    
    # Check validation images
    val_img_path = Path(dataset_path) / 'images' / 'val'
    val_label_path = Path(dataset_path) / 'labels' / 'val'
    
    # Count files by type
    train_images = list(train_img_path.glob('*.png'))
    train_labels = list(train_label_path.glob('*.txt'))
    val_images = list(val_img_path.glob('*.png'))
    val_labels = list(val_label_path.glob('*.txt'))
    
    print("\nTraining Set:")
    print(f"Images found: {len(train_images)}")
    print(f"Labels found: {len(train_labels)}")
    
    print("\nValidation Set:")
    print(f"Images found: {len(val_images)}")
    print(f"Labels found: {len(val_labels)}")
    
    # Check image-label pairs
    print("\nChecking image-label pairs...")
    unpaired_images = []
    for img in train_images:
        label_file = train_label_path / f"{img.stem}.txt"
        if not label_file.exists():
            unpaired_images.append(img.name)
    
    if unpaired_images:
        print("\nImages without labels:")
        for img in unpaired_images:
            print(f"- {img}")
    
    # Check label content
    print("\nAnalyzing label contents...")
    empty_labels = []
    class_counts = {0: 0, 1: 0, 2: 0, 3: 0}  # For your 4 classes
    
    for label in train_labels:
        if label.stat().st_size == 0:
            empty_labels.append(label.name)
        else:
            with open(label) as f:
                for line in f:
                    try:
                        class_id = int(line.split()[0])
                        class_counts[class_id] += 1
                    except:
                        print(f"Error in label file: {label.name}")
    
    if empty_labels:
        print("\nEmpty label files:")
        for label in empty_labels:
            print(f"- {label}")
    
    print("\nClass distribution:")
    for class_id, count in class_counts.items():
        print(f"Class {class_id}: {count} instances")
    
    # Check data.yaml
    yaml_file = Path(dataset_path) / 'data.yaml'
    if yaml_file.exists():
        import yaml
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        print("\ndata.yaml contents:")
        print(f"Train path: {data.get('train')}")
        print(f"Val path: {data.get('val')}")
        print(f"Number of classes: {data.get('nc')}")
        print(f"Class names: {data.get('names')}")

if __name__ == "__main__":
    dataset_path = input("Enter the path to your dataset folder: ")
    analyze_dataset(dataset_path)