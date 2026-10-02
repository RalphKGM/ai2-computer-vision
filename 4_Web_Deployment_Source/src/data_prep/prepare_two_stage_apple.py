"""Create annotation views for whole-apple pretraining and three-class defects.

Images and frozen split assignments are preserved. This is project scaffolding
for the students to understand, verify, and adapt under the course AI policy.
"""

import collections
import hashlib
import json
import math
import os
from pathlib import Path
import shutil

import yaml


def prepare_label_view(source, destination, keep_classes, source_sha256):
    source, destination = Path(source), Path(destination)
    keep_classes = list(keep_classes)
    raw = yaml.safe_load((source / 'data.yaml').read_text())
    names = raw['names']
    source_names = list(names) if isinstance(names, list) else [
        names[k] for k in sorted(names, key=lambda k: int(k))
    ]
    if len(set(keep_classes)) != len(keep_classes) or not set(keep_classes) <= set(source_names):
        raise ValueError('Selected classes must be distinct names from the source dataset.')
    if source.resolve() == destination.resolve():
        raise ValueError('The derived dataset must have a separate directory.')
    mapping = {source_names.index(name): j for j, name in enumerate(keep_classes)}
    manifest = json.loads((source / 'manifest.json').read_text())
    if not isinstance(manifest, list) or not manifest:
        raise ValueError('Source manifest must contain image records.')

    view_sha256 = hashlib.sha256(json.dumps({
        'source_sha256': source_sha256, 'classes': keep_classes,
        'conversion': 'keep_polygons_reindex_only_v1',
    }, sort_keys=True).encode()).hexdigest()
    marker = destination / '.label_view_sha256'
    if marker.is_file() and marker.read_text().strip() == view_sha256:
        for row in json.loads((destination / 'manifest.json').read_text()):
            label = destination / row['split'] / 'labels' / Path(row['file']).with_suffix('.txt')
            if not label.is_file() or hashlib.sha256(label.read_bytes()).hexdigest() != row.get('label_sha256'):
                raise RuntimeError(f'Cached derived label changed: {label}')
        return json.loads((destination / 'audit.json').read_text())
    if destination.exists():
        raise RuntimeError(f'Derived directory has a different identity: {destination}. Use a new dataset name.')

    temporary = destination.with_name(destination.name + '.preparing')
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    count_images, count_masks, count_empty = (collections.Counter() for _ in range(3))
    class_images, class_masks = {}, {}
    class_groups = collections.defaultdict(set)
    output_manifest = []
    seen_files = set()
    groups, hashes = collections.defaultdict(set), collections.defaultdict(set)
    try:
        for row in manifest:
            split, filename = str(row['split']), str(row['file'])
            if '/' in filename or '\\' in filename or split not in {'train', 'valid', 'val', 'test', 'test_reserve'}:
                raise ValueError('Unexpected manifest path.')
            if (split, filename) in seen_files:
                raise ValueError('Duplicate manifest record.')
            seen_files.add((split, filename))
            groups[str(row['capture_group'])].add(split)
            hashes[str(row['pixel_hash'])].add(split)
            source_image = source / split / 'images' / filename
            source_label = source / split / 'labels' / Path(filename).with_suffix('.txt')
            target_image = temporary / split / 'images' / filename
            target_label = temporary / split / 'labels' / Path(filename).with_suffix('.txt')
            if not source_image.is_file() or not source_label.is_file():
                raise FileNotFoundError(f'Missing image/label pair: {filename}')
            target_image.parent.mkdir(parents=True, exist_ok=True)
            target_label.parent.mkdir(parents=True, exist_ok=True)
            selected, present = [], set()
            for line in source_label.read_text().splitlines():
                if not line.strip():
                    continue
                parts = line.split()
                values = [float(x) for x in parts]
                if len(values) < 7 or (len(values) - 1) % 2 or not all(math.isfinite(x) for x in values):
                    raise ValueError(f'Invalid segmentation polygon: {source_label}')
                class_id = int(values[0])
                if values[0] != class_id or not 0 <= class_id < len(source_names):
                    raise ValueError(f'Invalid class ID: {source_label}')
                if not all(0 <= x <= 1 for x in values[1:]):
                    raise ValueError(f'Invalid polygon coordinates: {source_label}')
                if class_id in mapping:
                    new_id = mapping[class_id]
                    selected.append(str(new_id) + ' ' + ' '.join(parts[1:]))
                    present.add(new_id)
                    class_masks.setdefault(split, collections.Counter())[keep_classes[new_id]] += 1
            if keep_classes == ['apple'] and not selected:
                raise ValueError(f'No apple mask: {source_label}')
            target_label.write_text('\n'.join(selected) + ('\n' if selected else ''))
            output_manifest.append(dict(row, label_sha256=hashlib.sha256(target_label.read_bytes()).hexdigest()))
            try:
                os.link(source_image, target_image)
            except OSError:
                shutil.copy2(source_image, target_image)
            count_images[split] += 1
            count_masks[split] += len(selected)
            count_empty[split] += int(not selected)
            for class_id in present:
                class_images.setdefault(split, collections.Counter())[keep_classes[class_id]] += 1
                class_groups[split, keep_classes[class_id]].add(str(row['capture_group']))

        if any(len(v) > 1 for v in groups.values()) or any(len(v) > 1 for v in hashes.values()):
            raise ValueError('Cross-split capture groups or exact-image hashes in source dataset.')
        cfg = {'path': '.', 'train': 'train/images', 'val': raw['val'], 'test': raw['test'],
               'names': dict(enumerate(keep_classes))}
        (temporary / 'data.yaml').write_text(yaml.safe_dump(cfg, sort_keys=False))
        (temporary / 'manifest.json').write_text(json.dumps(output_manifest, indent=2))
        audit = {
            'source_dataset': source.name, 'source_sha256': source_sha256,
            'dataset_sha256': view_sha256, 'class_names': keep_classes,
            'output_counts': dict(count_images), 'masks_by_split': dict(count_masks),
            'images_without_selected_mask_by_split': dict(count_empty),
            'images_by_class_by_split': {k: dict(v) for k, v in class_images.items()},
            'masks_by_class_by_split': {k: dict(v) for k, v in class_masks.items()},
            'distinct_capture_groups_by_class_by_split': {
                split: {name: len(class_groups[split, name]) for name in keep_classes}
                for split in count_images
            },
            'distinct_capture_groups_by_split': {
                split: len({str(row['capture_group']) for row in manifest if row['split'] == split})
                for split in count_images
            },
            'note': 'All images and frozen splits retained. Selected polygons unchanged; class IDs reindexed. Empty defect labels retained.',
        }
        (temporary / 'audit.json').write_text(json.dumps(audit, indent=2))
        (temporary / 'README.md').write_text(
            'Selected classes: ' + ', '.join(keep_classes) + '\n\n' + audit['note'] + '\n'
        )
        marker_in_temp = temporary / '.label_view_sha256'
        marker_in_temp.write_text(view_sha256)
        temporary.replace(destination)
        return audit
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
