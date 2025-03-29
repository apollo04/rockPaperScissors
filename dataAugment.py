import os
import cv2
import glob
import albumentations as A
import shutil
from tqdm import tqdm

DATASET_PATH = "dataset" 
IMAGE_DIR = os.path.join(DATASET_PATH, "train/images")
LABEL_DIR = os.path.join(DATASET_PATH, "train/labels")
OUTPUT_IMAGE_DIR = os.path.join(DATASET_PATH, "train_aug/images")
OUTPUT_LABEL_DIR = os.path.join(DATASET_PATH, "train_aug/labels")


os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_LABEL_DIR, exist_ok=True)

transform = A.Compose([
    A.HorizontalFlip(p=0.7),
    A.RandomBrightnessContrast(p=0.6),
    A.Blur(p=0.3),
    A.Rotate(limit=120, p=0.5),
    A.ShiftScaleRotate(shift_limit=0.2, scale_limit=0.3, rotate_limit=100, p=0.65),
    A.GaussNoise(p=0.4),
], bbox_params=A.BboxParams(format='yolo', label_fields=['category_id']))

for img_path in tqdm(glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))):  
    filename = os.path.basename(img_path)
    label_path = os.path.join(LABEL_DIR, filename.replace(".jpg", ".txt"))

    image = cv2.imread(img_path)
    height, width = image.shape[:2]

    if not os.path.exists(label_path):
        continue  

    with open(label_path, "r") as f:
        lines = f.readlines()

    bboxes = []
    category_ids = []

    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        x_center, y_center, bbox_width, bbox_height = map(float, parts[1:])
        bboxes.append([x_center, y_center, bbox_width, bbox_height])
        category_ids.append(class_id)

    augmented = transform(image=image, bboxes=bboxes, category_id=category_ids)
    aug_image = augmented['image']
    aug_bboxes = augmented['bboxes']

    aug_img_path = os.path.join(OUTPUT_IMAGE_DIR, filename)
    cv2.imwrite(aug_img_path, aug_image)

    with open(os.path.join(OUTPUT_LABEL_DIR, filename.replace(".jpg", ".txt")), "w") as f:
        for bbox, class_id in zip(aug_bboxes, category_ids):
            f.write(f"{class_id} {' '.join(map(str, bbox))}\n")

print("Completed!")
