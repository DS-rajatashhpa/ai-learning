"""
Maid Assistant — Main Orchestrator

Runs the daily flow:
  1. Plan today's meals
  2. Deduct ingredients from inventory
  3. Check what's low
  4. Generate shopping list
  5. Show confirmation message (WhatsApp later)
  6. Show maid's instruction card
"""

import json
import os
from groq import Groq
from dotenv import load_dotenv
from core.inventory_manager import (
    load_inventory, save_inventory, check_low_stock,
    deduct_recipe, get_available_summary
)
from core.meal_planner import plan_meals, load_recipes
from core.learning_engine import get_learning_summary

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def find_recipe(name: str, recipes: list[dict]) -> dict | None:
    for r in recipes:
        if r["name"].lower() == name.lower():
            return r
    return None


def generate_shopping_list(low_items: list[dict]) -> str:
    if not low_items:
        return "Nothing to order today."

    items_text = "\n".join([
        f"- {item['name']}: {item['current']}{item['unit']} left (need more)"
        for item in low_items
    ])

    prompt = f"""You are helping order groceries from Blinkit for a North Indian family of 6 in Gurgaon.

LOW/OUT OF STOCK items:
{items_text}

Generate a practical shopping list with realistic quantities to order.
Order enough for 5-7 days. Be specific about quantity and unit.

Respond in JSON:
{{
  "items": [
    {{"name": "item name as searchable on Blinkit", "quantity": "500g or 1kg etc", "reason": "for which dish"}}
  ],
  "estimated_cost": "rough estimate in rupees",
  "priority": "high/medium — is this urgent?"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


def run_daily(people: int = 6):
    print("\n" + "=" * 60)
    print("MAID ASSISTANT — DAILY PLAN")
    print("=" * 60)

    # Step 1: Plan meals
    print("\n[1/4] Planning meals...")
    meal_plan = plan_meals(people_count=people)

    print(f"\nLUNCH:")
    print(f"  Main  : {meal_plan['lunch']['main']}")
    print(f"  Side  : {meal_plan['lunch']['side']}")
    if meal_plan['lunch'].get('extra'):
        print(f"  Extra : {meal_plan['lunch']['extra']}")

    print(f"\nDINNER:")
    print(f"  Main  : {meal_plan['dinner']['main']}")
    print(f"  Side  : {meal_plan['dinner']['side']}")

    print(f"\nReasoning: {meal_plan['reasoning']}")

    # Step 2: Deduct from inventory
    print("\n[2/4] Updating inventory...")
    inventory = load_inventory()
    recipes = load_recipes()
    all_warnings = []

    for meal_slot in ["lunch", "dinner"]:
        for dish_key in ["main", "side", "extra"]:
            dish_name = meal_plan[meal_slot].get(dish_key)
            if not dish_name:
                continue
            recipe = find_recipe(dish_name, recipes)
            if recipe:
                warnings = deduct_recipe(inventory, recipe)
                all_warnings.extend(warnings)

    save_inventory(inventory)
    print(f"  Inventory updated for today's meals")

    # Step 3: Check low stock
    print("\n[3/4] Checking stock levels...")
    low_items = check_low_stock(inventory)

    if low_items:
        print(f"  {len(low_items)} items low or out of stock:")
        for item in low_items:
            print(f"    ⚠ {item['name']}: {item['current']}{item['unit']}")
    else:
        print("  All items well stocked")

    # Step 4: Shopping list
    print("\n[4/4] Generating shopping list...")
    shopping = generate_shopping_list(low_items)

    if isinstance(shopping, dict):
        print(f"\n  Priority: {shopping.get('priority', 'N/A').upper()}")
        print(f"  Est. cost: {shopping.get('estimated_cost', 'N/A')}")
        print(f"\n  ORDER FROM BLINKIT:")
        for item in shopping.get("items", []):
            print(f"    • {item['name']} — {item['quantity']} ({item['reason']})")

    # Confirmation message (WhatsApp later)
    print("\n" + "=" * 60)
    print("CONFIRMATION MESSAGE (→ WhatsApp to you):")
    print("=" * 60)

    lunch_main = meal_plan['lunch']['main']
    lunch_side = meal_plan['lunch']['side']
    dinner_main = meal_plan['dinner']['main']
    dinner_side = meal_plan['dinner']['side']

    order_items = ""
    if isinstance(shopping, dict) and shopping.get("items"):
        order_items = ", ".join([f"{i['name']} {i['quantity']}" for i in shopping["items"][:5]])

    print(f"""
Today's plan for {people} people:
  Lunch  → {lunch_main} + {lunch_side}
  Dinner → {dinner_main} + {dinner_side}

{"Blinkit order ready: " + order_items if order_items else "Pantry is well stocked — no order needed"}

Reply YES to confirm order | Reply CHANGE to get new suggestions
""")

    # Maid instruction card
    print("=" * 60)
    print("MAID INSTRUCTION CARD (→ WhatsApp to maid):")
    print("=" * 60)
    print(f"""
Aaj banana hai ({people} log):

LUNCH:
  → {lunch_main}
  → {lunch_side}
  {"→ " + meal_plan['lunch'].get('extra', '') if meal_plan['lunch'].get('extra') else ''}

DINNER:
  → {dinner_main}
  → {dinner_side}

{"⚡ Blinkit delivery aa raha hai — check karo ghar pe." if order_items else "Sabh kuch ghar pe hai."}
""")


if __name__ == "__main__":
    import sys
    people = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    run_daily(people=people)
