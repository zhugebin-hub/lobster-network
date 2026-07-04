import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def load_jsonl(path: Path) -> List[Dict]:
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def safe_div(a: float, b: float) -> float:
    return round(a / b, 4) if b else 0.0


def aggregate(rows: List[Dict]) -> Dict:
    total_tasks = len(rows)
    total_success = sum(1 for r in rows if r['success'])
    total_calls = sum(r['tool_call_count'] for r in rows)
    total_hall = sum(r['tool_hallucinations'] for r in rows)
    total_param_err = sum(r['param_errors'] for r in rows)
    avg_ait = round(sum(r['ait'] for r in rows) / total_tasks, 4) if total_tasks else 0.0

    retry_rows = [r for r in rows if r['retry_triggered']]
    retry_rec = sum(1 for r in retry_rows if r['retry_recovered'])

    total_correct_tool = sum(r['correct_tool_count'] for r in rows)
    total_gold_tool = sum(len(r['gold_tools']) for r in rows)
    multi_rows = [r for r in rows if r['level'] == 'multi']
    multi_success = sum(1 for r in multi_rows if r['success'])

    return {
        'N': total_tasks,
        'TSR': safe_div(total_success, total_tasks),
        'THR': safe_div(total_hall, total_calls),
        'PFER': safe_div(total_param_err, total_calls),
        'AIT': avg_ait,
        'RRR': safe_div(retry_rec, len(retry_rows)) if retry_rows else None,
        'TCR': safe_div(total_correct_tool, total_gold_tool),
        'MCSR': safe_div(multi_success, len(multi_rows)) if multi_rows else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    rows = load_jsonl(Path(args.input))
    grouped = defaultdict(list)
    for row in rows:
        grouped['overall'].append(row)
        grouped[row['level']].append(row)

    metrics = {level: aggregate(items) for level, items in grouped.items()}

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f'Wrote metrics to {out}')


if __name__ == '__main__':
    main()
