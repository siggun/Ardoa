from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.auth import admin_required
from backend.database import get_session
from backend.models import FoodItem

router = APIRouter(prefix="/api/food", tags=["food"])

VALID_CATEGORIES = {"cheese", "charcuterie", "flatbread", "tapas", "pate", "dessert"}


class FoodItemIn(BaseModel):
    category: str
    name: str
    price: Optional[str] = None
    type: str = ""
    description: str = ""
    pairings: Optional[str] = None
    origin: Optional[str] = None
    pronunciation: Optional[str] = None


def item_to_dict(item: FoodItem) -> dict:
    return {
        "id": item.id,
        "category": item.category,
        "display_order": item.display_order,
        "name": item.name,
        "price": item.price,
        "type": item.type,
        "description": item.description,
        "pairings": item.pairings,
        "origin": item.origin,
        "pronunciation": item.pronunciation,
    }


@router.get("")
def list_all_food(session: Session = Depends(get_session)):
    items = session.exec(select(FoodItem).order_by(FoodItem.category, FoodItem.display_order)).all()
    result: dict = {cat: [] for cat in VALID_CATEGORIES}
    for item in items:
        if item.category in result:
            result[item.category].append(item_to_dict(item))
    return result


@router.get("/{category}")
def list_food_by_category(category: str, session: Session = Depends(get_session)):
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=404, detail="Unknown category")
    items = session.exec(
        select(FoodItem).where(FoodItem.category == category).order_by(FoodItem.display_order)
    ).all()
    return [item_to_dict(i) for i in items]


@router.get("/item/{item_id}")
def get_food_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(FoodItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    return item_to_dict(item)


@router.post("", dependencies=[Depends(admin_required)])
def create_food_item(data: FoodItemIn, session: Session = Depends(get_session)):
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    max_order = session.exec(
        select(FoodItem.display_order)
        .where(FoodItem.category == data.category)
        .order_by(FoodItem.display_order.desc())
    ).first()
    item = FoodItem(**data.model_dump(), display_order=(max_order or 0) + 1)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item_to_dict(item)


@router.put("/item/{item_id}", dependencies=[Depends(admin_required)])
def update_food_item(item_id: int, data: FoodItemIn, session: Session = Depends(get_session)):
    item = session.get(FoodItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    if data.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    session.commit()
    session.refresh(item)
    return item_to_dict(item)


@router.delete("/item/{item_id}", dependencies=[Depends(admin_required)])
def delete_food_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(FoodItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Food item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
