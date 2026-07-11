"""
SQLite database setup and queries.
"""

import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data" / "maid.db"
RECIPES_PATH = Path(__file__).parent.parent / "data" / "recipes.json"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS inventory (
                item_name   TEXT PRIMARY KEY,
                category    TEXT NOT NULL,
                quantity    REAL NOT NULL DEFAULT 0,
                unit        TEXT NOT NULL DEFAULT 'grams',
                threshold   REAL NOT NULL DEFAULT 100
            );

            CREATE TABLE IF NOT EXISTS recipes (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                category    TEXT NOT NULL,
                frequency   TEXT NOT NULL,
                cook_time   INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                recipe_id   TEXT NOT NULL,
                item_name   TEXT NOT NULL,
                quantity    REAL NOT NULL,
                unit        TEXT NOT NULL DEFAULT 'grams',
                PRIMARY KEY (recipe_id, item_name)
            );

            CREATE TABLE IF NOT EXISTS meal_plans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_date   TEXT NOT NULL,
                meal_type   TEXT NOT NULL,
                recipe_id   TEXT NOT NULL,
                people      INTEGER NOT NULL DEFAULT 3,
                confirmed   INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                order_date  TEXT NOT NULL,
                item_name   TEXT NOT NULL,
                quantity    REAL NOT NULL,
                unit        TEXT NOT NULL,
                source      TEXT DEFAULT 'blinkit',
                confirmed   INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS consumption_log (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                logged_date     TEXT NOT NULL,
                item_name       TEXT NOT NULL,
                estimated_used  REAL NOT NULL,
                source          TEXT DEFAULT 'recipe_deduction'
            );
        """)


def seed_from_json():
    """Load recipes.json into DB if recipes table is empty."""
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        if count > 0:
            return

        with open(RECIPES_PATH) as f:
            data = json.load(f)

        for r in data["recipes"]:
            conn.execute(
                "INSERT OR IGNORE INTO recipes (id, name, category, frequency, cook_time) VALUES (?,?,?,?,?)",
                (r["id"], r["name"], r["category"], r["frequency"], r["cook_time_minutes"])
            )
            for ing in r["ingredients"]:
                conn.execute(
                    "INSERT OR IGNORE INTO recipe_ingredients (recipe_id, item_name, quantity, unit) VALUES (?,?,?,?)",
                    (r["id"], ing["name"], ing["quantity"], ing.get("unit", "grams"))
                )


def seed_inventory():
    """Load inventory.json into DB if inventory table is empty."""
    inv_path = Path(__file__).parent.parent / "data" / "inventory.json"
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
        if count > 0:
            return

        with open(inv_path) as f:
            data = json.load(f)

        for section in ["staples", "vegetables", "dairy"]:
            for name, info in data.get(section, {}).items():
                conn.execute(
                    "INSERT OR IGNORE INTO inventory (item_name, category, quantity, unit, threshold) VALUES (?,?,?,?,?)",
                    (name, section, info["quantity"], info["unit"], info["threshold"])
                )


def setup():
    DB_PATH.parent.mkdir(exist_ok=True)
    init_db()
    seed_from_json()
    seed_inventory()
