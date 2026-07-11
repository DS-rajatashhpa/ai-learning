"""
Maid Assistant — FastAPI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import date
from api.db import setup, get_conn
from api.ai import suggest_meals, check_recipe_availability, get_inventory_snapshot, generate_shopping_list, get_all_recipes

app = FastAPI(title="Maid Assistant")

# Serve static files
STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup():
    setup()


@app.get("/")
def home():
    return FileResponse(str(STATIC_DIR / "index.html"))


# --- Inventory ---

@app.get("/api/inventory")
def get_inventory():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT item_name, category, quantity, unit, threshold FROM inventory ORDER BY category, item_name"
        ).fetchall()
    return {
        "items": [dict(r) for r in rows],
        "low_count": sum(1 for r in rows if r["quantity"] <= r["threshold"]),
        "out_count": sum(1 for r in rows if r["quantity"] == 0)
    }


class UpdateInventoryRequest(BaseModel):
    item_name: str
    quantity: float
    operation: str = "set"  # set | add | subtract


@app.post("/api/inventory/update")
def update_inventory(req: UpdateInventoryRequest):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT quantity FROM inventory WHERE item_name = ?", (req.item_name,)
        ).fetchone()

        if not row:
            raise HTTPException(404, f"Item '{req.item_name}' not found")

        if req.operation == "set":
            new_qty = req.quantity
        elif req.operation == "add":
            new_qty = row["quantity"] + req.quantity
        else:
            new_qty = max(0, row["quantity"] - req.quantity)

        conn.execute(
            "UPDATE inventory SET quantity = ? WHERE item_name = ?",
            (new_qty, req.item_name)
        )

    return {"item": req.item_name, "new_quantity": new_qty}


class AddInventoryRequest(BaseModel):
    item_name: str
    category: str
    quantity: float
    unit: str = "grams"
    threshold: float = 100


@app.post("/api/inventory/add")
def add_inventory_item(req: AddInventoryRequest):
    name = req.item_name.strip().lower().replace(" ", "_")
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT item_name FROM inventory WHERE item_name = ?", (name,)
        ).fetchone()
        if existing:
            raise HTTPException(409, f"Item '{name}' already exists")
        conn.execute(
            "INSERT INTO inventory (item_name, category, quantity, unit, threshold) VALUES (?,?,?,?,?)",
            (name, req.category, req.quantity, req.unit, req.threshold)
        )
    return {"item": name, "status": "added"}


@app.delete("/api/inventory/{item_name}")
def delete_inventory_item(item_name: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
    return {"item": item_name, "status": "deleted"}


class UpdateThresholdRequest(BaseModel):
    item_name: str
    threshold: float


@app.post("/api/inventory/threshold")
def update_threshold(req: UpdateThresholdRequest):
    with get_conn() as conn:
        conn.execute(
            "UPDATE inventory SET threshold = ? WHERE item_name = ?",
            (req.threshold, req.item_name)
        )
    return {"item": req.item_name, "threshold": req.threshold}


# --- Meal Suggestions ---

class SuggestRequest(BaseModel):
    prompt: str = "suggest something good"
    meal_type: str = "lunch"
    people: int = 3
    recent_meals: list[str] = []


@app.post("/api/suggest")
def suggest(req: SuggestRequest):
    suggestions = suggest_meals(
        prompt=req.prompt,
        meal_type=req.meal_type,
        people=req.people,
        recent_meals=req.recent_meals
    )
    return {"suggestions": suggestions}


# --- Meal Plan ---

class ConfirmMealRequest(BaseModel):
    recipe_id: str
    meal_type: str
    people: int = 3
    plan_date: str = None


@app.post("/api/plan/confirm")
def confirm_meal(req: ConfirmMealRequest):
    plan_date = req.plan_date or str(date.today())

    inventory = get_inventory_snapshot()
    recipes = get_all_recipes()
    recipe = next((r for r in recipes if r["id"] == req.recipe_id), None)

    if not recipe:
        raise HTTPException(404, "Recipe not found")

    scale = req.people / 6.0
    deducted = []

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO meal_plans (plan_date, meal_type, recipe_id, people, confirmed) VALUES (?,?,?,?,1)",
            (plan_date, req.meal_type, req.recipe_id, req.people)
        )

        for ing in recipe["ingredients"]:
            needed = ing["quantity"] * scale
            conn.execute(
                "UPDATE inventory SET quantity = MAX(0, quantity - ?) WHERE item_name = ?",
                (needed, ing["name"])
            )
            conn.execute(
                "INSERT INTO consumption_log (logged_date, item_name, estimated_used) VALUES (?,?,?)",
                (plan_date, ing["name"], needed)
            )
            deducted.append({"item": ing["name"], "used": round(needed, 1)})

    low_items = generate_shopping_list()

    return {
        "confirmed": True,
        "recipe": recipe["name"],
        "deducted": deducted,
        "low_stock": low_items
    }


# --- Today's Plan ---

@app.get("/api/plan/today")
def today_plan():
    today = str(date.today())
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT mp.meal_type, r.name, r.category, mp.people
            FROM meal_plans mp
            JOIN recipes r ON r.id = mp.recipe_id
            WHERE mp.plan_date = ? AND mp.confirmed = 1
            ORDER BY mp.id
        """, (today,)).fetchall()
    return {"date": today, "meals": [dict(r) for r in rows]}


# --- Shopping ---

@app.get("/api/shopping/list")
def shopping_list():
    items = generate_shopping_list()
    return {"items": items, "total_items": len(items)}


class ConfirmOrderRequest(BaseModel):
    items: list[dict]


@app.post("/api/shopping/confirm")
def confirm_order(req: ConfirmOrderRequest):
    today = str(date.today())
    with get_conn() as conn:
        for item in req.items:
            name = item["name"].replace(" ", "_")
            qty = item["order_qty"]
            conn.execute(
                "INSERT INTO orders (order_date, item_name, quantity, unit, confirmed) VALUES (?,?,?,?,1)",
                (today, name, qty, "grams")
            )
            conn.execute(
                "UPDATE inventory SET quantity = quantity + ? WHERE item_name = ?",
                (qty, name)
            )
    return {"ordered": len(req.items), "status": "confirmed"}


# --- Recipes ---

@app.get("/api/recipes")
def list_recipes(category: str = None):
    with get_conn() as conn:
        if category:
            rows = conn.execute(
                "SELECT * FROM recipes WHERE category = ? ORDER BY name", (category,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM recipes ORDER BY category, name").fetchall()

    inventory = get_inventory_snapshot()
    all_recipes = get_all_recipes()
    recipe_map = {r["id"]: r for r in all_recipes}

    result = []
    for r in rows:
        recipe = recipe_map.get(r["id"], {})
        avail = check_recipe_availability(recipe, inventory)
        result.append({**dict(r), "availability": avail})

    return {"recipes": result}
