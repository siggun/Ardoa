"""One-shot idempotent seed: migrate JS array data into the database."""
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///./dev.db")

from sqlmodel import Session, select

from backend.database import create_db_and_tables, engine
from backend.models import Beer, FoodItem, Wine, WineFoodPairing
from backend.seed_data import (
    ARCHIVED_WINES,
    BEERS,
    CHARCUTERIE,
    CHEESES,
    DESSERTS,
    FLATBREADS,
    PATES,
    TAPAS,
    WINES,
)


def seed_wines(session: Session):
    inserted = 0
    all_wines = [(w, False) for w in WINES] + [(w, True) for w in ARCHIVED_WINES]
    for order, (data, is_archived) in enumerate(all_wines):
        exists = session.exec(
            select(Wine).where(Wine.name == data["name"], Wine.vintage == data["vintage"])
        ).first()
        if exists:
            continue
        wine = Wine(
            display_order=order,
            is_archived=is_archived,
            archived_date=data.get("archivedDate"),
            replaced_by=data.get("replacedBy"),
            name=data["name"],
            vintage=data["vintage"],
            type=data["type"],
            grape=data["grape"],
            grape_detail=data.get("grapeDetail", ""),
            region=data.get("region", ""),
            appellation=data.get("appellation", ""),
            country=data.get("country", ""),
            winemaker=data.get("winemaker", ""),
            tasting=data.get("tasting", ""),
            food=data.get("food", ""),
            alcohol=data.get("alcohol", ""),
            serving=data.get("serving", ""),
            notes=data.get("notes", ""),
            pronunciation=data.get("pronunciation"),
            pronunciation_guide_only=data.get("pronunciationGuideOnly", False),
        )
        session.add(wine)
        session.flush()
        for i, p in enumerate(data.get("foodPairings", [])):
            session.add(WineFoodPairing(wine_id=wine.id, item=p["item"], why=p["why"], sort_order=i))
        inserted += 1
    return inserted


def seed_beers(session: Session):
    inserted = 0
    for order, data in enumerate(BEERS):
        exists = session.exec(select(Beer).where(Beer.name == data["name"])).first()
        if exists:
            continue
        session.add(Beer(
            display_order=order,
            name=data["name"],
            brewery=data.get("brewery", ""),
            location=data.get("location", ""),
            style=data.get("style", ""),
            type=data.get("type", ""),
            abv=data.get("abv", ""),
            body=data.get("body", ""),
            tasting=data.get("tasting", ""),
            notes=data.get("notes", ""),
        ))
        inserted += 1
    return inserted


def seed_food(session: Session):
    categories = [
        ("cheese", CHEESES),
        ("charcuterie", CHARCUTERIE),
        ("flatbread", FLATBREADS),
        ("tapas", TAPAS),
        ("pate", PATES),
        ("dessert", DESSERTS),
    ]
    inserted = 0
    for category, items in categories:
        for order, data in enumerate(items):
            exists = session.exec(
                select(FoodItem).where(FoodItem.category == category, FoodItem.name == data["name"])
            ).first()
            if exists:
                continue
            session.add(FoodItem(
                category=category,
                display_order=order,
                name=data["name"],
                price=data.get("price"),
                type=data.get("type", ""),
                description=data.get("description", ""),
                pairings=data.get("pairings"),
                origin=data.get("origin"),
                pronunciation=data.get("pronunciation"),
            ))
            inserted += 1
    return inserted


def main():
    create_db_and_tables()
    with Session(engine) as session:
        wines_n = seed_wines(session)
        beers_n = seed_beers(session)
        food_n = seed_food(session)
        session.commit()
    print(f"Seeded: {wines_n} wines, {beers_n} beers, {food_n} food items")


if __name__ == "__main__":
    main()
