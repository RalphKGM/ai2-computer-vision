#!/usr/bin/env python3
"""Build the September 29 fruit masks dataset without reusing held-out photos for training."""
from __future__ import annotations

import collections
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'data/pilots/apple-tomato-sep27-members/dataset'
POLICY = ROOT / 'data/pilots/apple-tomato-sep27-members/split_policy_702010.json'
OUT = ROOT / 'data/pilots/apple-tomato-sep29-refresh'
DATA = OUT / 'dataset'
RAW = {'apple': ROOT / 'data/raw/apple-sep29-roboflow',
       'tomato': ROOT / 'data/raw/tomato-sep29-roboflow'}
NAMES = ['apple', 'tomato', 'bruise_discoloration', 'rot_mold_decay', 'surface_damage']
MAP = {
    'apple': {'apple': 0, 'bruise_discoloration': 2,
              'rot_mold_decay': 3, 'surface_spot_scar': 4, 'surface_damage': 4},
    'tomato': {'tomato': 1, 'bruise-discoloration': 2,
               'rot-mold': 3, 'scar-cut': 4, 'healthy': None},
}


def old_key(row):
    return row['capture_group'].split('__', 1)[1]


def new_key(fruit, stem):
    if fruit == 'tomato':
        key = stem
    elif stem.startswith(('apple_member_sep27__', 'apple_surface_member_sep27__')):
        key = 'member_sep27__' + stem.split('__')[-1]
    elif 'apple_candidate__lab2wild__' in stem:
        key = stem[stem.index('apple_candidate__lab2wild__'):]
    elif 'IMG' in stem:
        key = stem[stem.index('IMG'):]
    else:
        key = stem
    if re.fullmatch(r'IMG_20[0-9]{6}_[0-9]{6}_(jpg|png)', key):
        key = key.rsplit('_', 1)[0]
    return key


def polygons_to_lines(fruit, anns, category_names, width, height):
    lines = []
    classes = set()
    skipped = collections.Counter()
    for ann in anns:
        name = category_names[ann['category_id']]
        if name not in MAP[fruit]:
            raise ValueError(f'Unknown {fruit} class: {name}')
        cls = MAP[fruit][name]
        if cls is None:
            skipped[name] += 1
            continue
        segmentation = ann.get('segmentation', [])
        if not isinstance(segmentation, list):
            skipped['unsupported_rle'] += 1
            continue
        for polygon in segmentation:
            if len(polygon) < 6 or len(polygon) % 2:
                skipped['bad_polygon'] += 1
                continue
            xs = [float(polygon[i]) / width for i in range(0, len(polygon), 2)]
            ys = [float(polygon[i]) / height for i in range(1, len(polygon), 2)]
            if max(xs) - min(xs) < 1 / width or max(ys) - min(ys) < 1 / height:
                skipped['tiny_polygon'] += 1
                continue
            values = []
            for x, y in zip(xs, ys):
                values.extend((max(0.0, min(1.0, x)), max(0.0, min(1.0, y))))
            lines.append(str(cls) + ' ' + ' '.join(f'{v:.6f}' for v in values))
            classes.add(cls)
    return lines, classes, skipped


def main():
    if OUT.exists():
        raise FileExistsError(f'Output already exists: {OUT}')
    DATA.mkdir(parents=True)
    old_rows = json.loads((OLD / 'manifest.json').read_text())
    frozen = json.loads(POLICY.read_text())
    moved = set(frozen['moved_train_to_valid'])
    reserved = set(frozen['reserved_test_files'])
    prior_groups = {}
    active_heldout = []
    for row in old_rows:
        split = ('valid' if row['file'] in moved else
                 'test_reserve' if row['file'] in reserved else row['split'])
        group_id = (row['fruit'], old_key(row))
        if group_id in prior_groups and prior_groups[group_id] != split:
            raise ValueError(f'Old group crosses split: {group_id}')
        prior_groups[group_id] = split
        if split != 'train':
            active_heldout.append((row, split))

    entries = collections.defaultdict(list)
    input_counts = collections.Counter()
    for fruit, base in RAW.items():
        for source_split in ('train', 'valid', 'test'):
            coco = json.loads((base / source_split / '_annotations.coco.json').read_text())
            categories = {c['id']: c['name'] for c in coco['categories']}
            annotations = collections.defaultdict(list)
            for ann in coco['annotations']:
                annotations[ann['image_id']].append(ann)
            for image in coco['images']:
                file = image['file_name']
                source = base / source_split / file
                if not source.is_file():
                    raise FileNotFoundError(source)
                key = new_key(fruit, file.split('.rf.')[0])
                entries[(fruit, key)].append(dict(fruit=fruit, key=key,
                    source_split=source_split, source=source, file=file,
                    width=int(image['width']), height=int(image['height']),
                    anns=annotations[image['id']], categories=categories))
                input_counts[(fruit, source_split)] += 1

    output_rows = []
    audit = collections.Counter()
    used_names = set()
    for (fruit, key), variants in sorted(entries.items()):
        protected = prior_groups.get((fruit, key))
        if protected in ('valid', 'test', 'test_reserve'):
            audit['new_export_files_for_heldout_groups_excluded'] += len(variants)
            continue
        # Existing training groups remain training even if Roboflow changed their split.
        if protected == 'train':
            preferred = 'train' if any(v['source_split'] == 'train' for v in variants) else variants[0]['source_split']
            selected = [v for v in variants if v['source_split'] == preferred]
            destination = 'train'
        else:
            preferred = next(s for s in ('test', 'valid', 'train') if any(v['source_split'] == s for v in variants))
            selected = [v for v in variants if v['source_split'] == preferred]
            destination = preferred
        audit['cross_export_split_variants_excluded'] += len(variants) - len(selected)
        for item in selected:
            with Image.open(item['source']) as im:
                width, height = im.size
            if (width, height) != (item['width'], item['height']):
                audit['coco_size_mismatch_excluded'] += 1
                continue
            lines, classes, skipped = polygons_to_lines(
                fruit, item['anns'], item['categories'], width, height)
            audit.update({f'skipped_{k}': v for k, v in skipped.items()})
            if (0 if fruit == 'apple' else 1) not in classes:
                audit['missing_whole_fruit_excluded'] += 1
                continue
            name = f'{fruit}__{item["file"]}'
            if name in used_names:
                raise ValueError(f'Name collision: {name}')
            used_names.add(name)
            images = DATA / destination / 'images'
            labels = DATA / destination / 'labels'
            images.mkdir(parents=True, exist_ok=True)
            labels.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item['source'], images / name)
            (labels / (Path(name).stem + '.txt')).write_text('\n'.join(lines) + '\n')
            output_rows.append(dict(file=name, fruit=fruit, split=destination,
                source='sep29_' + fruit, source_split=item['source_split'],
                capture_group=f'{fruit}__{key}', pixel_hash=None))

    # Preserve every previously held-out image and label byte for byte.
    for old_row, split in active_heldout:
        source_split = old_row['split']
        name = old_row['file']
        if name in used_names:
            raise ValueError(f'Name collision: {name}')
        used_names.add(name)
        for kind, filename in [('images', name), ('labels', Path(name).with_suffix('.txt').name)]:
            target = DATA / split / kind / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(OLD / source_split / kind / filename, target)
        output_rows.append(dict(old_row, split=split, source='frozen_sep27_heldout'))
        audit['frozen_heldout_images_copied'] += 1

    split_groups = collections.defaultdict(set)
    split_hashes = collections.defaultdict(set)
    masks = collections.Counter()
    image_classes = collections.Counter()
    for row in output_rows:
        image = DATA / row['split'] / 'images' / row['file']
        label = DATA / row['split'] / 'labels' / Path(row['file']).with_suffix('.txt')
        with Image.open(image) as im:
            rgb = im.convert('RGB')
            digest = hashlib.sha256(str(rgb.size).encode() + rgb.tobytes()).hexdigest()
        row['pixel_hash'] = digest
        split_groups[row['capture_group']].add(row['split'])
        split_hashes[digest].add(row['split'])
        cls = []
        for line in label.read_text().splitlines():
            vals = [float(v) for v in line.split()]
            assert len(vals) >= 7 and (len(vals) - 1) % 2 == 0
            assert int(vals[0]) == vals[0] and 0 <= vals[0] < len(NAMES)
            assert all(0 <= v <= 1 for v in vals[1:])
            cls.append(int(vals[0]))
            masks[NAMES[int(vals[0])]] += 1
        assert (0 if row['fruit'] == 'apple' else 1) in cls
        for c in set(cls):
            image_classes[NAMES[c]] += 1
    assert all(len(x) == 1 for x in split_groups.values()), 'Capture group leakage'
    assert all(len(x) == 1 for x in split_hashes.values()), 'Exact-pixel leakage'
    frozen_rows = [r for r in output_rows if r['source'] == 'frozen_sep27_heldout']
    assert len(frozen_rows) == len(active_heldout)
    assert collections.Counter(r['split'] for r in frozen_rows) == {'valid': 347, 'test': 174, 'test_reserve': 102}
    # Prior test and validation groups cannot enter new training.
    for row in output_rows:
        if row['split'] == 'train':
            assert prior_groups.get((row['fruit'], row['capture_group'].split('__', 1)[1])) not in ('valid', 'test', 'test_reserve')

    counts = dict(collections.Counter(r['split'] for r in output_rows))
    (DATA / 'manifest.json').write_text(json.dumps(output_rows, indent=2))
    report = dict(inputs={str(k): v for k, v in input_counts.items()},
        output_counts=counts, distinct_capture_groups=len(split_groups),
        distinct_by_split={s: len({r['capture_group'] for r in output_rows if r['split'] == s}) for s in counts},
        images_by_class=dict(image_classes), masks_by_class=dict(masks),
        exclusions=dict(audit), source_exports=[str(x.relative_to(ROOT)) for x in RAW.values()],
        class_mapping=MAP, frozen_split_policy=str(POLICY.relative_to(ROOT)),
        note='New export training labels; prior validation/test/reserve copied unchanged. Source exports contain 3 variants per training original.')
    (DATA / 'audit.json').write_text(json.dumps(report, indent=2))
    (DATA / 'data.yaml').write_text('path: .\ntrain: train/images\nval: valid/images\ntest: test/images\nnames:\n' +
        ''.join(f'  {i}: {name}\n' for i, name in enumerate(NAMES)))
    (DATA / 'README.md').write_text(
        '# September 29 apple and tomato training dataset\n\n'
        'Training images and masks come from the two September 29 Roboflow COCO exports. '
        'Original Roboflow training photos include three augmented variants per source photo. '
        'Prior validation, test, and test-reserve images and labels are copied byte for byte from '
        'the September 27 dataset under the frozen 70/20/10 policy. New export images that '
        'were previously held out are excluded from training. `healthy` tomato polygons are '
        'dropped because healthy is not a model class; whole-tomato masks remain. Apple '
        '`surface_spot_scar` maps to `surface_damage`. Missing whole-fruit masks are excluded. '
        'See `audit.json` for counts and exclusions. No notebook augmentation is applied to this version.\n')
    for fruit, base in RAW.items():
        shutil.copy2(base / 'README.roboflow.txt', DATA / f'{fruit}__README.roboflow.txt')
    archive = OUT / 'apple-tomato-sep29-refresh.zip'
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
