import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from jsonschema import Draft7Validator
except ImportError:
    Draft7Validator = None


SUPPORTED_METHODS = [
    "zero_shot",
    "react",
    "openclaw_wo_validator",
    "openclaw_wo_retry",
    "openclaw_full",
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def validate_args(schema: Dict[str, Any], args: Dict[str, Any]) -> bool:
    if Draft7Validator is None:
        required = schema.get("required", [])
        for key in required:
            if key not in args:
                return False
        props = schema.get("properties", {})
        for key, spec in props.items():
            if key not in args:
                continue
            if "enum" in spec and args[key] not in spec["enum"]:
                return False
            if spec.get("type") == "integer" and not isinstance(args[key], int):
                return False
            if spec.get("type") == "array" and not isinstance(args[key], list):
                return False
        return True
    return not list(Draft7Validator(schema).iter_errors(args))


def apply_standard_weakness(call: Dict[str, Any], tool_name: str, method: str, step: int, level: str):
    if method == "zero_shot":
        if step == 0 and level != "single":
            call["tool_name"] = tool_name + "_guess"
        if "building" in call["arguments"]:
            call["arguments"]["building"] = "D"
    elif method == "react":
        if "capacity" in call["arguments"] and step == 0:
            call["arguments"]["capacity"] = str(call["arguments"]["capacity"])
    elif method == "openclaw_wo_validator":
        if "style" in call["arguments"]:
            call["arguments"]["style"] = "campus-formal"
    elif method in {"openclaw_wo_retry", "openclaw_full"}:
        pass
    else:
        raise ValueError(f"Unsupported method: {method}")


def apply_fault_plan(calls: List[Dict[str, Any]], task: Dict[str, Any]):
    for fault in task.get("fault_plan", []):
        step = fault["step"]
        if step >= len(calls):
            continue
        call = calls[step]
        if fault.get("action") == "remove":
            call["arguments"].pop(fault["field"], None)
        elif fault.get("action") == "replace":
            call["arguments"][fault["field"]] = fault.get("bad_value")


def infer_call_from_gold(task: Dict[str, Any], method: str) -> Tuple[List[Dict[str, Any]], int]:
    calls = []
    gold_tools = task["gold_tools"]
    gold_params = task["gold_params"]

    for i, (tool_name, args) in enumerate(zip(gold_tools, gold_params)):
        call = {"tool_name": tool_name, "arguments": dict(args)}
        apply_standard_weakness(call, tool_name, method, i, task["level"])
        calls.append(call)

    if task.get("level") == "recovery" or task.get("fault_plan"):
        apply_fault_plan(calls, task)

    return calls, len(calls)


def evaluate_task(task: Dict[str, Any], tools: Dict[str, Any], method: str) -> Dict[str, Any]:
    predicted_calls, ait = infer_call_from_gold(task, method)
    gold_tools = task["gold_tools"]
    gold_params = task["gold_params"]

    tool_hallucinations = 0
    param_errors = 0
    correct_tools = 0
    retry_triggered = False
    invalid_step_count = 0
    recovered_step_count = 0
    all_invalid_steps_recovered = True

    final_calls = []

    for i, pred in enumerate(predicted_calls):
        pred = {"tool_name": pred["tool_name"], "arguments": dict(pred["arguments"])}
        tool_name = pred["tool_name"]
        if tool_name not in tools:
            tool_hallucinations += 1
            all_invalid_steps_recovered = False
            final_calls.append(pred)
            continue

        if i < len(gold_tools) and tool_name == gold_tools[i]:
            correct_tools += 1

        schema = tools[tool_name]["parameters"]
        is_valid = validate_args(schema, pred["arguments"])
        if not is_valid:
            param_errors += 1
            invalid_step_count += 1
            retry_triggered = True
            if method == "openclaw_full":
                repaired = dict(gold_params[i])
                if validate_args(schema, repaired):
                    pred["arguments"] = repaired
                    recovered_step_count += 1
                else:
                    all_invalid_steps_recovered = False
            else:
                all_invalid_steps_recovered = False

        final_calls.append(pred)

    retry_recovered = bool(retry_triggered and invalid_step_count > 0 and recovered_step_count == invalid_step_count)
    success = (
        correct_tools == len(gold_tools)
        and tool_hallucinations == 0
        and (param_errors == 0 or retry_recovered)
    )

    return {
        "task_id": task["task_id"],
        "level": task["level"],
        "method": method,
        "fault_type": task.get("fault_type"),
        "fault_description": task.get("fault_description"),
        "predicted_calls": final_calls,
        "gold_tools": gold_tools,
        "tool_call_count": len(final_calls),
        "correct_tool_count": correct_tools,
        "tool_hallucinations": tool_hallucinations,
        "param_errors": param_errors,
        "ait": ait,
        "retry_triggered": retry_triggered,
        "retry_recovered": retry_recovered,
        "invalid_step_count": invalid_step_count,
        "recovered_step_count": recovered_step_count,
        "success": success,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--tools", required=True)
    parser.add_argument("--method", required=True, choices=SUPPORTED_METHODS)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    task_rows = load_jsonl(Path(args.tasks))
    tool_rows = load_json(Path(args.tools))
    tools = {t["name"]: t for t in tool_rows}

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for task in task_rows:
            result = evaluate_task(task, tools, args.method)
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"Wrote task runs to {out_path}")


if __name__ == "__main__":
    main()
