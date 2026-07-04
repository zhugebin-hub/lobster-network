"""
scripts/convert_weibo_data.py
Convert the Weibo stance dataset to the JSON format expected by RumorStanceDataset.

Input layout expected:
    <weibo_root>/Weibo.txt          -- "event_id  label  ..."  (tab-separated)
    <weibo_root>/Weibo_stance/      -- one <event_id>.json per event

Each event JSON contains a list of post objects with fields:
    id, uid, text, parent, stance, ...

Output: three JSON files
    data/processed/weibo_train.json
    data/processed/weibo_val.json
    data/processed/weibo_test.json

Usage:
    python scripts/convert_weibo_data.py \
        --weibo_root "C:/Users/24469/CascadeProjects/数据暂存/Weibo_stance" \
        --output_dir "data/processed" \
        --train_ratio 0.8 --val_ratio 0.1
"""

import argparse
import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


STANCE_REMAP = {
    'support':  'support',
    'deny':     'deny',
    'question': 'question',
    'comment':  'comment',
    'root':     'root',    # source post; kept but filtered out from reply list
}

LABEL_MAP = {
    '0': 'non-rumor',
    '1': 'rumor',
    0:   'non-rumor',
    1:   'rumor',
}


def load_event_labels(weibo_txt_path: str) -> Dict[str, str]:
    """
    Parse Weibo.txt.
    Format: "eid:EVENT_ID\tlabel:0_or_1\tPOST_ID1 POST_ID2 ..."
    """
    labels = {}
    with open(weibo_txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            # parts[0] = "eid:12345"   parts[1] = "label:0"
            eid_part   = parts[0].strip()
            label_part = parts[1].strip()
            if eid_part.startswith('eid:'):
                event_id = eid_part[4:]
            else:
                event_id = eid_part
            if label_part.startswith('label:'):
                raw_label = label_part[6:]
            else:
                raw_label = label_part
            labels[event_id] = LABEL_MAP.get(raw_label, raw_label)
    return labels


def build_parent_map(posts: List[Dict]) -> Dict[str, int]:
    """Map post-id (mid) → list index."""
    return {str(p['id']): i for i, p in enumerate(posts)}


def convert_event(event_id: str, posts_raw: List[Dict],
                  rumor_label: str, max_posts: int = 200) -> Optional[Dict]:
    """
    Convert one Weibo event to the model's JSON format.

    Root post: parent == null  (or stance == 'root')
    Replies  : all other posts
    """
    if not posts_raw:
        return None

    # Detect root post: parent is null/None or stance is 'root'
    source_posts = [p for p in posts_raw
                    if p.get('parent') is None or p.get('stance', '') == 'root']
    reply_posts  = [p for p in posts_raw
                    if p.get('parent') is not None and p.get('stance', '') != 'root']

    if not source_posts:
        source_posts = [posts_raw[0]]
        reply_posts  = posts_raw[1:]

    claim_text = source_posts[0].get('text', '').strip()
    if not claim_text:
        return None

    reply_posts = reply_posts[:max_posts]
    if not reply_posts:
        return None

    # Build id→index map (ids may be int or str in JSON)
    id_to_idx = {str(p['id']): i for i, p in enumerate(reply_posts)}
    source_id  = str(source_posts[0]['id'])

    posts_out   = []
    propagation = []

    for post in reply_posts:
        stance = post.get('stance', 'comment')
        if stance in ('root', None):
            stance = 'comment'

        text = post.get('text', '').strip()
        if not text:
            continue

        parent_raw = post.get('parent')
        parent_str = str(parent_raw) if parent_raw is not None else None

        if parent_str is None or parent_str == source_id:
            parent_idx = None          # direct reply to claim
        elif parent_str in id_to_idx:
            parent_idx = id_to_idx[parent_str]
        else:
            parent_idx = None

        cur_idx = len(posts_out)
        posts_out.append({
            'text':       text,
            'stance':     stance,
            'parent_idx': parent_idx,
            'post_id':    str(post['id']),
        })
        if parent_idx is not None:
            propagation.append({'parent_idx': parent_idx, 'child_idx': cur_idx})

    if not posts_out:
        return None

    return {
        'claim_id':    event_id,
        'claim':       claim_text,
        'rumor_label': rumor_label,
        'posts':       posts_out,
        'propagation': propagation,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weibo_root',  type=str,
                        default=r'C:\Users\24469\CascadeProjects\数据暂存\Weibo_stance')
    parser.add_argument('--output_dir',  type=str, default='data/processed')
    parser.add_argument('--train_ratio', type=float, default=0.8)
    parser.add_argument('--val_ratio',   type=float, default=0.1)
    parser.add_argument('--max_posts',   type=int,   default=100)
    parser.add_argument('--seed',        type=int,   default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    weibo_root   = Path(args.weibo_root)
    stance_dir   = weibo_root / 'Weibo_stance'
    weibo_txt    = weibo_root / 'Weibo.txt'

    if not weibo_txt.exists():
        # try alternative locations
        for candidate in weibo_root.rglob('Weibo.txt'):
            weibo_txt = candidate
            break

    print(f"Loading labels from: {weibo_txt}")
    event_labels = load_event_labels(str(weibo_txt))
    print(f"  Found {len(event_labels)} event labels")

    json_files = list(stance_dir.glob('*.json'))
    print(f"  Found {len(json_files)} event JSON files")

    converted = []
    skipped = 0

    for jf in json_files:
        event_id = jf.stem
        rumor_label = event_labels.get(event_id)
        if rumor_label is None:
            skipped += 1
            continue

        with open(jf, 'r', encoding='utf-8') as f:
            try:
                posts_raw = json.load(f)
            except json.JSONDecodeError:
                skipped += 1
                continue

        item = convert_event(event_id, posts_raw, rumor_label, args.max_posts)
        if item is None:
            skipped += 1
            continue

        converted.append(item)

    print(f"  Converted: {len(converted)}  Skipped: {skipped}")

    # Shuffle and split by event
    random.shuffle(converted)
    n      = len(converted)
    n_train = int(n * args.train_ratio)
    n_val   = int(n * args.val_ratio)

    train_data = converted[:n_train]
    val_data   = converted[n_train:n_train + n_val]
    test_data  = converted[n_train + n_val:]

    print(f"  Split → train={len(train_data)}  val={len(val_data)}  test={len(test_data)}")

    os.makedirs(args.output_dir, exist_ok=True)
    for split, data in [('train', train_data), ('val', val_data), ('test', test_data)]:
        out_path = os.path.join(args.output_dir, f'weibo_{split}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Saved {len(data)} samples → {out_path}")

    print("Done.")


if __name__ == '__main__':
    main()
