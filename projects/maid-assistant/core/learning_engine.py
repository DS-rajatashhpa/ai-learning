"""
Learning engine — tracks actual vs textbook ingredient usage.
Over time, learns the family's real consumption patterns.
"""

import json
from pathlib import Path
from datetime import date

HISTORY_PATH = Path(__file__).parent.parent / "memory" / "usage_history.json"
RECIPES_PATH = Path(__file__).parent.parent / "data" / "recipes.json"


def load_history() -> dict:
    with open(HISTORY_PATH) as f:
        return json.load(f)


def save_history(history: dict):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


def record_actual_usage(recipe_id: str, people: int, actual_ingredients: dict):
    """
    Record what was ACTUALLY used when cooking.
    actual_ingredients: {"tomato": 250, "onion": 180, ...}
    """
    history = load_history()
    history["records"].append({
        "date": str(date.today()),
        "recipe_id": recipe_id,
        "people": people,
        "actual_used": actual_ingredients
    })
    save_history(history)


def get_learned_quantity(recipe_id: str, ingredient: str, textbook_quantity: float) -> float:
    """
    Return the learned quantity for an ingredient in a recipe.
    Falls back to textbook if not enough data (< 3 records).
    """
    history = load_history()
    records = [
        r for r in history["records"]
        if r["recipe_id"] == recipe_id and ingredient in r.get("actual_used", {})
    ]

    if len(records) < 3:
        return textbook_quantity  # not enough data yet

    actuals = [r["actual_used"][ingredient] for r in records[-10:]]  # last 10 cooks
    learned = sum(actuals) / len(actuals)

    return round(learned, 0)


def get_learning_summary() -> str:
    """Show how the system's estimates have evolved."""
    history = load_history()
    records = history["records"]

    if not records:
        return "No cooking history yet. System will learn as meals are cooked."

    with open(RECIPES_PATH) as f:
        recipes_data = json.load(f)

    recipe_map = {r["id"]: r for r in recipes_data["recipes"]}
    lines = [f"Learning Summary ({len(records)} meals recorded):"]

    seen = {}
    for record in records:
        rid = record["recipe_id"]
        if rid not in seen:
            seen[rid] = 0
        seen[rid] += 1

    for recipe_id, count in seen.items():
        lines.append(f"\n  {recipe_id}: cooked {count} times")
        if recipe_id in recipe_map and count >= 3:
            for ing in recipe_map[recipe_id]["ingredients"]:
                learned = get_learned_quantity(recipe_id, ing["name"], ing["quantity"])
                if learned != ing["quantity"]:
                    lines.append(f"    {ing['name']}: textbook={ing['quantity']}g → learned={learned}g")

    return "\n".join(lines)
