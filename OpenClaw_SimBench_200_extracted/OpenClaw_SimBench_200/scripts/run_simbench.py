import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from jsonschema import Draft7Validator
except ImportError:
    Draft7Validator = None


def load_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def load_jsonl(path: Path):
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def infer_call_from_gold(task: Dict[str, Any], method: str) -> Tuple[List[Dict[str, Any]], int]:
    """A lightweight simulator so the whole pipeline can run without an actual model.
    Replace this with your real LLM / agent call later.
    """
    calls = []
    gold_tools = task['gold_tools']
    gold_params = task['gold_params']

    for i, (tool, args) in enumerate(zip(gold_tools, gold_params)):
        call = {'tool_name': tool, 'arguments': dict(args)}
        if method == 'zero_shot':
            if i == 0 and task['level'] != 'single':
                call['tool_name'] = tool + '_guess'
            if 'building' in call['arguments']:
                call['arguments']['building'] = 'D'
        elif method == 'react':
            if 'capacity' in call['arguments'] and i == 0:
                call['arguments']['capacity'] = str(call['arguments']['capacity'])
        elif method == 'openclaw_wo_validator':
            if 'style' in call['arguments']:
                call['arguments']['style'] = 'campus-formal'
        elif method == 'openclaw_wo_retry':
            pass
        elif method == 'openclaw_full':
            pass
        else:
            raise ValueError(f'Unsupported method: {method}')
        calls.append(call)

    ait = len(calls)
    return calls, ait


def validate_args(schema: Dict[str, Any], args: Dict[str, Any]) -> bool:
    if Draft7Validator is None:
        required = schema.get('required', [])
        for key in required:
            if key not in args:
                return False
        enum_props = {k: v.get('enum') for k, v in schema.get('properties', {}).items() if 'enum' in v}
        for key, allowed in enum_props.items():
            if key in args and args[key] not in allowed:
                return False
        return True
    validator = Draft7Validator(schema)
    return not list(validator.iter_errors(args))


def evaluate_task(task: Dict[str, Any], tools: Dict[str, Any], method: str) -> Dict[str, Any]:
    predicted_calls, ait = infer_call_from_gold(task, method)
    gold_tools = task['gold_tools']
    gold_params = task['gold_params']

    tool_hallucinations = 0
    param_errors = 0
    correct_tools = 0
    retry_triggered = False
    retry_recovered = False

    for i, pred in enumerate(predicted_calls):
        tool_name = pred['tool_name']
        if tool_name not in tools:
            tool_hallucinations += 1
            continue
        if i < len(gold_tools) and tool_name == gold_tools[i]:
            correct_tools += 1

        schema = tools[tool_name]['parameters']
        is_valid = validate_args(schema, pred['arguments'])
        if not is_valid:
            param_errors += 1
            if method == 'openclaw_full':
                retry_triggered = True
                repaired = dict(gold_params[i])
                if validate_args(schema, repaired):
                    retry_recovered = True

    success = (
        correct_tools == len(gold_tools)
        and tool_hallucinations == 0
        and (param_errors == 0 or retry_recovered)
    )

    return {
        'task_id': task['task_id'],
        'level': task['level'],
        'method': method,
        'predicted_calls': predicted_calls,
        'gold_tools': gold_tools,
        'tool_call_count': len(predicted_calls),
        'correct_tool_count': correct_tools,
        'tool_hallucinations': tool_hallucinations,
        'param_errors': param_errors,
        'ait': ait,
        'retry_triggered': retry_triggered,
        'retry_recovered': retry_recovered,
        'success': success,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tasks', required=True)
    parser.add_argument('--tools', required=True)
    parser.add_argument('--method', required=True,
                        choices=['zero_shot', 'react', 'openclaw_wo_validator', 'openclaw_wo_retry', 'openclaw_full'])
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    task_rows = load_jsonl(Path(args.tasks))
    tool_rows = load_json(Path(args.tools))
    tools = {t['name']: t for t in tool_rows}

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        for task in task_rows:
            result = evaluate_task(task, tools, args.method)
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

    print(f'Wrote task runs to {out_path}')


if __name__ == '__main__':
    main()
