#!/usr/bin/env python3
"""Build an apple-only dataset from Fruit Segmentation-9 with frozen held-outs."""
from __future__ import annotations

import collections
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

from build_sep29_fruit_dataset import new_key

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/Users/ralph/Downloads/Fruit Segmentation-9')
PREVIOUS = ROOT / 'data/pilots/apple-tomato-sep29-refresh/dataset'
OUT = ROOT / 'data/pilots/apple-sep30-fruit9'
DATA = OUT / 'dataset'
NAMES = ['apple', 'bruise_discoloration', 'rot_mold_decay', 'surface_damage']
OLD_TO_NEW = {0: 0, 2: 1, 3: 2, 4: 3}
SOURCE_TO_NEW = {'apple': 0, 'bruise_discoloration': 1,
                 'rot_mold_decay': 2, 'surface_damage': 3,
                 'surface_spot_scar': 3}


def pixel_hash(path):
    with Image.open(path) as image:
        rgb = image.convert('RGB')
        return hashlib.sha256(str(rgb.size).encode() + rgb.tobytes()).hexdigest()


def convert_polygons(annotations, category_names, width, height):
    lines, classes = [], set()
    skipped = collections.Counter()
    for ann in annotations:
        name = category_names[ann['category_id']]
        if name not in SOURCE_TO_NEW:
            if name == 'Fruit-Segmentation':
                continue
            raise ValueError(f'Unknown source class: {name}')
        cls = SOURCE_TO_NEW[name]
        polygons = ann.get('segmentation', [])
        if not isinstance(polygons, list):
            skipped['rle'] += 1
            continue
        for polygon in polygons:
            if len(polygon) < 6 or len(polygon) % 2:
                skipped['bad_polygon'] += 1
                continue
            coords = []
            for i in range(0, len(polygon), 2):
                coords.extend((max(0., min(1., float(polygon[i]) / width)),
                               max(0., min(1., float(polygon[i + 1]) / height))))
            if max(coords[::2]) - min(coords[::2]) < 1 / width or max(coords[1::2]) - min(coords[1::2]) < 1 / height:
                skipped['tiny_polygon'] += 1
                continue
            lines.append(str(cls) + ' ' + ' '.join(f'{x:.6f}' for x in coords))
            classes.add(cls)
    return lines, classes, skipped


def main():
    if OUT.exists():
        raise FileExistsError(f'Output already exists: {OUT}')
    old_rows = [r for r in json.loads((PREVIOUS / 'manifest.json').read_text()) if r['fruit'] == 'apple']
    old_heldout = [r for r in old_rows if r['split'] != 'train']
    prior_split = {}
    for row in old_rows:
        key = row['capture_group']
        if key in prior_split and prior_split[key] != row['split']:
            raise ValueError(f'Previous capture group crossed splits: {key}')
        prior_split[key] = row['split']

    source_groups = collections.defaultdict(list)
    input_counts = collections.Counter()
    for split in ('train', 'valid', 'test'):
        coco = json.loads((SOURCE / split / '_annotations.coco.json').read_text())
        names = {c['id']: c['name'] for c in coco['categories']}
        by_image = collections.defaultdict(list)
        for annotation in coco['annotations']:
            by_image[annotation['image_id']].append(annotation)
        for image in coco['images']:
            name = image['file_name']
            path = SOURCE / split / name
            if not path.is_file():
                raise FileNotFoundError(path)
            group = 'apple__' + new_key('apple', name.split('.rf.')[0])
            source_groups[group].append((split, image, path, by_image[image['id']], names))
            input_counts[split] += 1

    DATA.mkdir(parents=True)
    rows, exclusions = [], collections.Counter()
    used_names = set()
    for group, variants in sorted(source_groups.items()):
        protected = prior_split.get(group)
        if protected in ('valid', 'test', 'test_reserve'):
            exclusions['source_files_matching_frozen_heldout'] += len(variants)
            continue
        if protected == 'train':
            preferred = 'train' if any(v[0] == 'train' for v in variants) else variants[0][0]
            target_split = 'train'
        else:
            preferred = next(s for s in ('test', 'valid', 'train') if any(v[0] == s for v in variants))
            target_split = preferred
        selected = [v for v in variants if v[0] == preferred]
        exclusions['other_source_split_variants'] += len(variants) - len(selected)
        for source_split, image, source_path, annotations, categories in selected:
            with Image.open(source_path) as picture:
                width, height = picture.size
            if (width, height) != (image['width'], image['height']):
                exclusions['coco_size_mismatch'] += 1
                continue
            lines, classes, skipped = convert_polygons(annotations, categories, width, height)
            for reason, count in skipped.items():
                exclusions['skipped_' + reason] += count
            if 0 not in classes:
                exclusions['missing_apple_mask'] += 1
                continue
            name = 'apple__' + image['file_name']
            if name in used_names:
                raise ValueError(f'Duplicate output name: {name}')
            used_names.add(name)
            image_dir = DATA / target_split / 'images'
            label_dir = DATA / target_split / 'labels'
            image_dir.mkdir(parents=True, exist_ok=True)
            label_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, image_dir / name)
            (label_dir / (Path(name).stem + '.txt')).write_text('\n'.join(lines) + '\n')
            rows.append(dict(file=name, fruit='apple', split=target_split,
                             source='Fruit Segmentation-9', source_split=source_split,
                             capture_group=group, pixel_hash=None))

    for row in old_heldout:
        split, name = row['split'], row['file']
        if name in used_names:
            raise ValueError(f'Duplicate frozen name: {name}')
        used_names.add(name)
        for kind, filename in [('images', name), ('labels', Path(name).with_suffix('.txt').name)]:
            source = PREVIOUS / split / kind / filename
            target = DATA / split / kind / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            if kind == 'images':
                shutil.copy2(source, target)
            else:
                converted = []
                for line in source.read_text().splitlines():
                    parts = line.split()
                    cls = int(parts[0])
                    if cls not in OLD_TO_NEW:
                        raise ValueError(f'Unexpected old class {cls}: {source}')
                    converted.append(str(OLD_TO_NEW[cls]) + ' ' + ' '.join(parts[1:]))
                target.write_text('\n'.join(converted) + '\n')
        rows.append(dict(row, source='frozen_sep29_heldout', pixel_hash=None))
        exclusions['frozen_heldout_copied'] += 1

    split_groups, split_hashes = collections.defaultdict(set), collections.defaultdict(set)
    image_classes, masks = collections.Counter(), collections.Counter()
    for row in rows:
        image = DATA / row['split'] / 'images' / row['file']
        label = DATA / row['split'] / 'labels' / Path(row['file']).with_suffix('.txt')
        digest = pixel_hash(image)
        row['pixel_hash'] = digest
        split_groups[row['capture_group']].add(row['split'])
        split_hashes[digest].add(row['split'])
        classes = set()
        for line in label.read_text().splitlines():
            values = [float(x) for x in line.split()]
            assert len(values) >= 7 and (len(values) - 1) % 2 == 0
            assert values[0].is_integer() and 0 <= int(values[0]) < 4
            assert all(0 <= x <= 1 for x in values[1:])
            cls = int(values[0])
            classes.add(cls)
            masks[NAMES[cls]] += 1
        assert 0 in classes, f'Missing apple mask: {label}'
        for cls in classes:
            image_classes[NAMES[cls]] += 1
    assert all(len(v) == 1 for v in split_groups.values()), 'Capture-group leakage'
    assert all(len(v) == 1 for v in split_hashes.values()), 'Exact-pixel leakage'
    assert all(prior_split.get(r['capture_group']) not in ('valid', 'test', 'test_reserve')
               for r in rows if r['split'] == 'train')
    assert len([r for r in rows if r['source'] == 'frozen_sep29_heldout']) == len(old_heldout)

    counts = dict(collections.Counter(r['split'] for r in rows))
    report = dict(source='Fruit Segmentation-9 COCO export', input_counts=dict(input_counts),
                  output_counts=counts, distinct_by_split={s: len({r['capture_group'] for r in rows
                    if r['split'] == s}) for s in counts},
                  images_by_class=dict(image_classes), masks_by_class=dict(masks),
                  exclusions=dict(exclusions), classes=NAMES,
                  note='Training labels from Fruit Segmentation-9; apple heldouts from September 29 dataset preserved.')
    (DATA / 'manifest.json').write_text(json.dumps(rows, indent=2))
    (DATA / 'audit.json').write_text(json.dumps(report, indent=2))
    (DATA / 'data.yaml').write_text('path: .\ntrain: train/images\nval: valid/images\ntest: test/images\nnames:\n' +
                                    ''.join(f'  {i}: {name}\n' for i, name in enumerate(NAMES)))
    (DATA / 'README.md').write_text(
        '# Apple-only dataset from Fruit Segmentation-9\n\n'
        'Training images and polygons come from the provided Roboflow COCO export. '
        'Roboflow training files include augmented variants. Previous apple validation, '
        'test, and test-reserve images are frozen; their class IDs were remapped without '
        'changing polygon coordinates. `surface_spot_scar` maps to `surface_damage`. '
        'See audit.json for counts and exclusions.\n')
    shutil.copy2(SOURCE / 'README.roboflow.txt', DATA / 'README.roboflow.txt')

    archive = OUT / 'apple-sep30-fruit9.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for file in sorted(DATA.rglob('*')):
            if file.is_file():
                z.write(file, file.relative_to(DATA))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    (OUT / 'dataset_sha256.txt').write_text(sha + '\n')
    print(json.dumps(report, indent=2))
    print('ZIP', archive, archive.stat().st_size, 'SHA256', sha)


if __name__ == '__main__':
    main()
