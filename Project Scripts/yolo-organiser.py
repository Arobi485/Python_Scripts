import os
import shutil
import random
from pathlib import Path
import math

class DatasetSplitter:
    def __init__(self, source_path, train_ratio=0.8):
        self.source_path = Path(source_path)
        self.train_ratio = train_ratio
        
        # Define paths
        self.output_dir = self.source_path / 'split_dataset'
        self.train_img_dir = self.output_dir / 'images' / 'train'
        self.val_img_dir = self.output_dir / 'images' / 'val'
        self.train_label_dir = self.output_dir / 'labels' / 'train'
        self.val_label_dir = self.output_dir / 'labels' / 'val'

    def create_directories(self):
        """Create necessary directories"""
        dirs = [self.train_img_dir, self.val_img_dir, 
                self.train_label_dir, self.val_label_dir]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")

    def collect_files(self):
        """Collect all image and label pairs"""
        print("\nCollecting files...")
        
        # Get all PNG images and their corresponding labels
        image_files = []
        valid_pairs = []
        
        # Look in source directory and its subdirectories
        for img_path in self.source_path.rglob('*.png'):
            label_path = img_path.parent / f"{img_path.stem}.txt"
            
            if label_path.exists():
                valid_pairs.append((img_path, label_path))
            else:
                print(f"Warning: No label found for {img_path.name}")
        
        print(f"Found {len(valid_pairs)} valid image-label pairs")
        return valid_pairs

    def split_dataset(self):
        """Split the dataset into train and validation sets"""
        # Collect files
        valid_pairs = self.collect_files()
        
        # Shuffle the pairs
        random.shuffle(valid_pairs)
        
        # Calculate split
        num_train = math.ceil(len(valid_pairs) * self.train_ratio)
        
        # Split into train and validation sets
        train_pairs = valid_pairs[:num_train]
        val_pairs = valid_pairs[num_train:]
        
        print(f"\nSplitting dataset:")
        print(f"Training set: {len(train_pairs)} pairs")
        print(f"Validation set: {len(val_pairs)} pairs")
        
        # Copy training files
        print("\nCopying training files...")
        for img_path, label_path in train_pairs:
            shutil.copy2(img_path, self.train_img_dir / img_path.name)
            shutil.copy2(label_path, self.train_label_dir / label_path.name)
        
        # Copy validation files
        print("Copying validation files...")
        for img_path, label_path in val_pairs:
            shutil.copy2(img_path, self.val_img_dir / img_path.name)
            shutil.copy2(label_path, self.val_label_dir / label_path.name)

    def create_yaml(self):
        """Create data.yaml file"""
        yaml_content = {
            'train': str(self.train_img_dir),
            'val': str(self.val_img_dir),
            'nc': 1,  # number of classes
            'names': ['emergency vehicle']
        }
        
        import yaml
        yaml_path = self.output_dir / 'data.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        print(f"\nCreated data.yaml at {yaml_path}")

    def verify_split(self):
        """Verify the split was successful"""
        train_images = len(list(self.train_img_dir.glob('*.png')))
        train_labels = len(list(self.train_label_dir.glob('*.txt')))
        val_images = len(list(self.val_img_dir.glob('*.png')))
        val_labels = len(list(self.val_label_dir.glob('*.txt')))
        
        print("\nDataset Split Verification:")
        print(f"Training set: {train_images} images, {train_labels} labels")
        print(f"Validation set: {val_images} images, {val_labels} labels")
        
        if train_images != train_labels or val_images != val_labels:
            print("WARNING: Mismatch between number of images and labels!")
        else:
            print("✓ All image-label pairs are matched correctly")

def main():
    print("Dataset Splitting Tool")
    print("=====================")
    
    # Get source directory
    source_path = input("\nEnter the path to your dataset folder: ")
    
    # Create splitter instance
    splitter = DatasetSplitter(source_path)
    
    # Create directory structure
    splitter.create_directories()
    
    # Split dataset
    splitter.split_dataset()
    
    # Create yaml file
    splitter.create_yaml()
    
    # Verify split
    splitter.verify_split()
    
    print("\nDataset splitting complete!")
    print(f"New dataset location: {splitter.output_dir}")

if __name__ == "__main__":
    main()