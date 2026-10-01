import json
from typing import Any


def plan_to_json(plan: Any) -> str:
    if hasattr(plan, "model_dump"):
        return json.dumps(
            plan.model_dump(),
            indent=2,
            ensure_ascii=False,
        )

    if isinstance(plan, dict):
        return json.dumps(
            plan,
            indent=2,
            ensure_ascii=False,
        )

    return str(plan)


def pretty_plan(plan_text: str) -> str:
    try:
        data = json.loads(plan_text)

        return json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )

    except (json.JSONDecodeError, TypeError):
        return plan_text