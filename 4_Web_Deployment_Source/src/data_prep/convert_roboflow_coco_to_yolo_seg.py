#!/usr/bin/env python3
"""Convert split Roboflow COCO polygons to Ultralytics YOLO segmentation."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path


CLASS_ORDER = [
    "apple",
    "bruise_discoloration",
    "cut_crack",
    "rot_mold_decay",
    "surface_spot_scar",
]


def convert_split(source: Path, destination: Path, split: str) -> dict:
    split_source = source / split
    coco_path = split_source / "_annotations.coco.json"
    coco = json.loads(coco_path.read_text(encoding="utf-8"))

    images_by_id = {image["id"]: image for image in coco["images"]}
    category_names = {category["id"]: category["name"] for category in coco["categories"]}
    class_ids = {name: index for index, name in enumerate(CLASS_ORDER)}
    annotations_by_image = defaultdict(list)
    for annotation in coco["annotations"]:
        annotations_by_image[annotation["image_id"]].append(annotation)

    image_destination = destination / split / "images"
    label_destination = destination / split / "labels"
    image_destination.mkdir(parents=True, exist_ok=True)
    label_destination.mkdir(parents=True, exist_ok=True)

    mask_counts = Counter()
    image_counts = Counter()
    empty_images = 0
    polygon_rows = 0

    for image_id, image in images_by_id.items():
        source_image = split_source / image["file_name"]
        if not source_image.is_file():
            raise FileNotFoundError(source_image)
        shutil.copy2(source_image, image_destination / source_image.name)

        width = float(image["width"])
        height = float(image["height"])
        rows = []
        classes_in_image = set()
        for annotation in annotations_by_image.get(image_id, []):
            class_name = category_names[annotation["category_id"]]
            if class_name not in class_ids:
                raise ValueError(f"Unexpected annotated class: {class_name}")
            for polygon in annotation.get("segmentation", []):
                if len(polygon) < 6 or len(polygon) % 2:
                    raise ValueError(f"Invalid polygon in image {image['file_name']}")
                normalized = []
                for position in range(0, len(polygon), 2):
                    x = min(1.0, max(0.0, float(polygon[position]) / width))
                    y = min(1.0, max(0.0, float(polygon[position + 1]) / height))
                    normalized.extend((x, y))
                coordinates = " ".join(f"{value:.6f}" for value in normalized)
                rows.append(f"{class_ids[class_name]} {coordinates}")
                polygon_rows += 1
                mask_counts[class_name] += 1
                classes_in_image.add(class_name)

        for class_name in classes_in_image:
            image_counts[class_name] += 1
        if not rows:
            empty_images += 1
        (label_destination / f"{source_image.stem}.txt").write_text(
            "\n".join(rows) + ("\n" if rows else ""), encoding="utf-8"
        )

    return {
        "images": len(images_by_id),
        "polygon_rows": polygon_rows,
        "empty_images": empty_images,
        "masks_by_class": {name: mask_counts[name] for name in CLASS_ORDER},
        "images_by_class": {name: image_counts[name] for name in CLASS_ORDER},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    if args.destination.exists():
        raise FileExistsError(f"Destination already exists: {args.destination}")

    audit = {split: convert_split(args.source, args.destination, split) for split in ("train", "valid", "test")}
    names = "\n".join(f"  {index}: {name}" for index, name in enumerate(CLASS_ORDER))
    data_yaml = (
        "path: .\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n\n"
        "names:\n"
        f"{names}\n"
    )
    (args.destination / "data.yaml").write_text(data_yaml, encoding="utf-8")
    (args.destination / "conversion_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    readme = """# Fruit Segmentation YOLO Export

Converted from the Roboflow COCO Segmentation export into Ultralytics YOLO
instance-segmentation polygon labels. Every image has a matching `.txt` label.

This package preserves the Roboflow train, validation, and test splits. The
unannotated placeholder COCO category `Fruit-Segmentation` was removed and the
five real classes were reindexed from 0 to 4. See `conversion_audit.json` for
counts. `cut_crack` is absent from the current test split, so that class cannot
yet receive a meaningful test metric.
"""
    (args.destination / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
