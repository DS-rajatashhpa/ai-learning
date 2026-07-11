"""
AI meal planner — suggests lunch and dinner based on inventory.
"""

import json
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from core.inventory_manager import load_inventory, get_available_summary

load_dotenv()

RECIPES_PATH = Path(__file__).parent.parent / "data" / "recipes.json"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_recipes() -> list[dict]:
    with open(RECIPES_PATH) as f:
        return json.load(f)["recipes"]


def get_recipe_names_by_availability(inventory: dict, recipes: list[dict]) -> list[str]:
    """
    Filter recipes to those where key ingredients are available.
    A recipe is 'makeable' if at least 70% of its ingredients are in stock.
    """
    makeable = []
    all_stock = {}
    for section in ["staples", "vegetables", "dairy"]:
        all_stock.update(inventory.get(section, {}))

    for recipe in recipes:
        ingredients = recipe["ingredients"]
        available_count = sum(
            1 for ing in ingredients
            if all_stock.get(ing["name"], {}).get("quantity", 0) >= ing["quantity"] * 0.5
        )
        ratio = available_count / len(ingredients)
        if ratio >= 0.7:
            makeable.append(recipe["name"])

    return makeable


def plan_meals(people_count: int = 6, meal_history: list[str] = None) -> dict:
    """
    Ask AI to plan lunch and dinner based on current inventory.
    Avoids repeating meals from history.
    """
    inventory = load_inventory()
    recipes = load_recipes()

    inventory_summary = get_available_summary(inventory)
    makeable = get_recipe_names_by_availability(inventory, recipes)
    avoid = meal_history or []

    recipe_list = "\n".join([f"- {r['name']} ({r['category']})" for r in recipes])

    prompt = f"""You are a North Indian household meal planner for a family of {people_count} in Gurgaon.

AVAILABLE RECIPES:
{recipe_list}

{inventory_summary}

RECIPES THAT CAN BE MADE WITH CURRENT INVENTORY:
{chr(10).join(['- ' + m for m in makeable]) if makeable else 'Check inventory — most items available'}

RECENTLY COOKED (avoid repeating):
{chr(10).join(['- ' + m for m in avoid]) if avoid else 'No recent history'}

RULES:
- Always suggest 1 dal + 1 sabzi for lunch with roti/rice
- Always suggest 1 dal or sabzi for dinner with roti
- Prefer dishes where ingredients are in stock
- Do not repeat from recently cooked list
- Respond in JSON only

Respond with this exact JSON:
{{
  "lunch": {{
    "main": "recipe name",
    "side": "recipe name (roti or rice)",
    "extra": "salad or raita (optional)"
  }},
  "dinner": {{
    "main": "recipe name",
    "side": "recipe name (roti or rice)"
  }},
  "reasoning": "one line why these were chosen"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)
