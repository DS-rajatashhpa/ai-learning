"""
Manages pantry inventory — read, deduct, check low stock.
"""

import json
from pathlib import Path
from datetime import date

INVENTORY_PATH = Path(__file__).parent.parent / "data" / "inventory.json"


def load_inventory() -> dict:
    with open(INVENTORY_PATH) as f:
        return json.load(f)


def save_inventory(inventory: dict):
    inventory["last_updated"] = str(date.today())
    with open(INVENTORY_PATH, "w") as f:
        json.dump(inventory, f, indent=2)


def get_all_items(inventory: dict) -> dict:
    """Flatten all sections into one dict for easy lookup."""
    items = {}
    for section in ["staples", "vegetables", "dairy"]:
        items.update(inventory.get(section, {}))
    return items


def check_low_stock(inventory: dict) -> list[dict]:
    """Return items that are at or below their threshold."""
    low = []
    for section in ["staples", "vegetables", "dairy"]:
        for name, data in inventory.get(section, {}).items():
            if data["quantity"] <= data["threshold"]:
                low.append({
                    "name": name,
                    "current": data["quantity"],
                    "threshold": data["threshold"],
                    "unit": data["unit"],
                    "section": section
                })
    return low


def deduct_recipe(inventory: dict, recipe: dict, servings_ratio: float = 1.0) -> list[str]:
    """
    Deduct ingredients for a recipe from inventory.
    servings_ratio: 1.0 = full recipe (6 people), 0.5 = half recipe etc.
    Returns list of items that went below threshold.
    """
    all_items = get_all_items(inventory)
    warnings = []

    for ingredient in recipe["ingredients"]:
        name = ingredient["name"]
        needed = ingredient["quantity"] * servings_ratio

        for section in ["staples", "vegetables", "dairy"]:
            if name in inventory.get(section, {}):
                inventory[section][name]["quantity"] = max(
                    0,
                    inventory[section][name]["quantity"] - needed
                )
                remaining = inventory[section][name]["quantity"]
                threshold = inventory[section][name]["threshold"]
                if remaining <= threshold:
                    warnings.append(f"{name}: {remaining:.0f}g remaining (threshold: {threshold}g)")
                break

    return warnings


def update_item(name: str, quantity: float, operation: str = "set"):
    """
    Update a single item. operation: 'set', 'add', 'subtract'
    """
    inventory = load_inventory()
    for section in ["staples", "vegetables", "dairy"]:
        if name in inventory.get(section, {}):
            if operation == "set":
                inventory[section][name]["quantity"] = quantity
            elif operation == "add":
                inventory[section][name]["quantity"] += quantity
            elif operation == "subtract":
                inventory[section][name]["quantity"] = max(0, inventory[section][name]["quantity"] - quantity)
            save_inventory(inventory)
            return f"Updated {name}: {inventory[section][name]['quantity']}g"
    return f"Item '{name}' not found in inventory"


def get_available_summary(inventory: dict) -> str:
    """Return a readable summary of what's available for the LLM."""
    lines = ["CURRENT PANTRY INVENTORY:"]
    for section in ["staples", "vegetables", "dairy"]:
        lines.append(f"\n{section.upper()}:")
        for name, data in inventory.get(section, {}).items():
            status = "LOW" if data["quantity"] <= data["threshold"] else "OK"
            if data["quantity"] > 0:
                lines.append(f"  {name}: {data['quantity']}{data['unit']} [{status}]")
            else:
                lines.append(f"  {name}: OUT OF STOCK")
    return "\n".join(lines)
