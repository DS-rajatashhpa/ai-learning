"""
AI layer — meal suggestions with availability awareness.
"""

import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv, find_dotenv
from api.db import get_conn

# Search up directory tree for .env (works when .env is in parent folder)
load_dotenv(find_dotenv(usecwd=True) or find_dotenv())

_groq_client = None

def _client():
    global _groq_client
    if _groq_client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set. Add it to your .env file.")
        _groq_client = Groq(api_key=key)
    return _groq_client


def get_inventory_snapshot() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT item_name, quantity, unit, threshold FROM inventory").fetchall()
    return {r["item_name"]: {"qty": r["quantity"], "unit": r["unit"], "threshold": r["threshold"]} for r in rows}


def get_all_recipes() -> list[dict]:
    with get_conn() as conn:
        recipes = conn.execute("SELECT * FROM recipes").fetchall()
        result = []
        for r in recipes:
            ings = conn.execute(
                "SELECT item_name, quantity FROM recipe_ingredients WHERE recipe_id = ?",
                (r["id"],)
            ).fetchall()
            result.append({
                "id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "frequency": r["frequency"],
                "cook_time": r["cook_time"],
                "ingredients": [{"name": i["item_name"], "quantity": i["quantity"]} for i in ings]
            })
    return result


def check_recipe_availability(recipe: dict, inventory: dict, people: int = 3) -> dict:
    """
    Check if a recipe can be made with current inventory.
    Returns status: 'ready' | 'low' | 'missing'
    """
    scale = people / 6.0
    missing = []
    low = []
    available = []

    for ing in recipe["ingredients"]:
        name = ing["name"]
        needed = ing["quantity"] * scale
        stock = inventory.get(name, {})
        qty = stock.get("qty", 0)
        threshold = stock.get("threshold", 50)

        if qty == 0:
            missing.append({"name": name, "needed": round(needed), "have": 0})
        elif qty < needed:
            missing.append({"name": name, "needed": round(needed), "have": round(qty)})
        elif qty < threshold:
            low.append({"name": name, "needed": round(needed), "have": round(qty)})
        else:
            available.append(name)

    if missing:
        status = "missing"
    elif low:
        status = "low"
    else:
        status = "ready"

    return {
        "status": status,
        "missing": missing,
        "low": low,
        "available_count": len(available),
        "total_count": len(recipe["ingredients"])
    }


def suggest_meals(prompt: str, meal_type: str, people: int, recent_meals: list[str] = None) -> list[dict]:
    """
    AI suggests 4 meal options based on inventory + prompt.
    Each option includes availability status.
    """
    inventory = get_inventory_snapshot()
    recipes = get_all_recipes()

    checked_recipes = []
    for r in recipes:
        avail = check_recipe_availability(r, inventory, people)
        checked_recipes.append({**r, "availability": avail})

    ready = [r for r in checked_recipes if r["availability"]["status"] == "ready"]
    low = [r for r in checked_recipes if r["availability"]["status"] == "low"]

    recipe_summary = []
    for r in checked_recipes:
        st = r["availability"]["status"]
        recipe_summary.append(f'{r["name"]} ({r["category"]}) [{st.upper()}]')

    avoid = recent_meals or []

    system = """You are a smart meal planner for a North Indian family in Gurgaon.
You suggest practical, varied meals. You know North Indian cooking well.
Respond only in valid JSON."""

    user_prompt = f"""Family: {people} people, Gurgaon, North Indian household
Meal type: {meal_type}
User request: "{prompt}"
Avoid repeating: {avoid}

ALL RECIPES WITH STOCK STATUS:
{chr(10).join(recipe_summary)}

Suggest exactly 4 recipe options that best match the request and meal type.
Prioritize READY recipes. Include 1-2 LOW ones if good options.
Avoid MISSING ones unless the user specifically asked for it.
Consider variety — not all the same category.

Respond with JSON:
{{
  "suggestions": [
    {{
      "recipe_name": "exact name from list",
      "reason": "why this fits (1 line)",
      "pair_with": "what to pair it with (roti/rice/nothing)"
    }}
  ]
}}"""

    response = _client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    ai_result = json.loads(response.choices[0].message.content)
    suggestions = ai_result.get("suggestions", [])

    result = []
    recipe_map = {r["name"]: r for r in checked_recipes}

    for s in suggestions[:4]:
        name = s["recipe_name"]
        recipe = recipe_map.get(name)
        if not recipe:
            continue
        result.append({
            "id": recipe["id"],
            "name": recipe["name"],
            "category": recipe["category"],
            "cook_time": recipe.get("cook_time", 30),
            "reason": s.get("reason", ""),
            "pair_with": s.get("pair_with", ""),
            "availability": recipe["availability"]
        })

    return result


def generate_shopping_list() -> list[dict]:
    """Find all items below threshold and generate order list."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT item_name, quantity, unit, threshold FROM inventory WHERE quantity <= threshold"
        ).fetchall()

    items = []
    for r in rows:
        deficit = r["threshold"] * 3 - r["quantity"]
        order_qty = max(deficit, r["threshold"] * 2)
        order_qty = round(order_qty / 100) * 100 if order_qty > 100 else 100

        items.append({
            "name": r["item_name"].replace("_", " "),
            "current": round(r["quantity"]),
            "unit": r["unit"],
            "order_qty": round(order_qty),
            "threshold": r["threshold"]
        })

    return items


def generate_week_plan(people: int = 3) -> dict:
    """AI generates a full Mon-Sun meal plan (breakfast + lunch + dinner)."""
    inventory = get_inventory_snapshot()
    recipes = get_all_recipes()

    checked = []
    for r in recipes:
        avail = check_recipe_availability(r, inventory, people)
        checked.append({**r, "availability": avail})

    ready = [f'{r["name"]} ({r["category"]})' for r in checked if r["availability"]["status"] == "ready"]
    low   = [f'{r["name"]} ({r["category"]})' for r in checked if r["availability"]["status"] == "low"]

    system = """You are a weekly meal planner for a vegetarian North Indian family in Gurgaon (3 people).
Plan diverse, realistic meals. Vary categories across the week. Don't repeat the same dish.
Breakfast = light (poha/upma/chila/oats/sandwich). Lunch = filling (dal+sabzi, pasta, noodles, wrap).
Dinner = medium (lighter than lunch, wraps/salad/sabzi+roti ok).
Respond ONLY with valid JSON."""

    prompt = f"""Plan a full Mon-Sun week for breakfast, lunch, dinner.

READY recipes (prefer these): {', '.join(ready[:40])}
LOW STOCK (use sparingly): {', '.join(low[:15])}

Rules:
- No dish repeated more than twice in the week
- Vary the category each day (don't do dal for lunch Mon AND Tue)
- Breakfast must be quick (under 20 min)
- Include at least 1 pasta, 1 noodles, 1 wrap, 1 burger or sandwich across the week
- Saturday dinner = special/fun (burger, pasta, brownie for dessert)
- Sunday lunch = elaborate (rajma/chole/biryani level)

Respond with JSON:
{{
  "days": {{
    "Monday": {{"breakfast": "recipe name", "lunch": "recipe name", "dinner": "recipe name"}},
    "Tuesday": {{"breakfast": "...", "lunch": "...", "dinner": "..."}},
    "Wednesday": {{"breakfast": "...", "lunch": "...", "dinner": "..."}},
    "Thursday": {{"breakfast": "...", "lunch": "...", "dinner": "..."}},
    "Friday": {{"breakfast": "...", "lunch": "...", "dinner": "..."}},
    "Saturday": {{"breakfast": "...", "lunch": "...", "dinner": "..."}},
    "Sunday": {{"breakfast": "...", "lunch": "...", "dinner": "..."}}
  }}
}}"""

    response = _client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        response_format={"type": "json_object"}
    )

    ai_result = json.loads(response.choices[0].message.content)
    days = ai_result.get("days", {})

    recipe_map = {r["name"]: r for r in checked}

    result = {}
    for day, meals in days.items():
        result[day] = {}
        for meal_type, recipe_name in meals.items():
            recipe = recipe_map.get(recipe_name)
            result[day][meal_type] = {
                "recipe_id": recipe["id"] if recipe else None,
                "recipe_name": recipe_name,
                "category": recipe["category"] if recipe else "unknown",
                "availability": recipe["availability"]["status"] if recipe else "unknown"
            }

    return result
