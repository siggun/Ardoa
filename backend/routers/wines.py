from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.auth import admin_required
from backend.database import get_session
from backend.models import Wine, WineFoodPairing
from backend.services.ai_research import research_wine

router = APIRouter(prefix="/api/wines", tags=["wines"])


class FoodPairingIn(BaseModel):
    item: str
    why: str
    sort_order: int = 0


class WineIn(BaseModel):
    name: str
    vintage: str
    type: str
    grape: str
    grape_detail: str = ""
    region: str = ""
    appellation: str = ""
    country: str = ""
    position: Optional[int] = None
    winemaker: str = ""
    alcohol: str = ""
    body: str = ""
    aromatics: str = ""
    palate: str = ""
    structure: str = ""
    finish: str = ""
    winemaking: str = ""
    story: str = ""
    pronunciation: Optional[str] = None
    pronunciation_guide_only: bool = False
    tech_sheet_url: Optional[str] = None
    food_pairings: List[FoodPairingIn] = []


class ArchiveIn(BaseModel):
    archived_date: str
    replaced_by: Optional[str] = None


class ReorderIn(BaseModel):
    new_order: int


class PositionIn(BaseModel):
    position: Optional[int] = None


class ResearchIn(BaseModel):
    name: str
    producer: str = ""
    region: str = ""
    varietal: str = ""
    vintage: str = ""


def wine_to_dict(wine: Wine) -> dict:
    return {
        "id": wine.id,
        "display_order": wine.display_order,
        "is_archived": wine.is_archived,
        "archived_date": wine.archived_date,
        "replaced_by": wine.replaced_by,
        "position": wine.position,
        "name": wine.name,
        "vintage": wine.vintage,
        "type": wine.type,
        "grape": wine.grape,
        "grape_detail": wine.grape_detail,
        "region": wine.region,
        "appellation": wine.appellation,
        "country": wine.country,
        "winemaker": wine.winemaker,
        "tasting": wine.tasting,
        "alcohol": wine.alcohol,
        "notes": wine.notes,
        "body": wine.body,
        "aromatics": wine.aromatics,
        "palate": wine.palate,
        "structure": wine.structure,
        "finish": wine.finish,
        "winemaking": wine.winemaking,
        "story": wine.story,
        "pronunciation": wine.pronunciation,
        "pronunciation_guide_only": wine.pronunciation_guide_only,
        "tech_sheet_url": wine.tech_sheet_url,
        "food_pairings": [
            {"id": p.id, "item": p.item, "why": p.why, "sort_order": p.sort_order}
            for p in sorted(wine.food_pairings, key=lambda p: p.sort_order)
        ],
    }


@router.get("")
def list_wines(session: Session = Depends(get_session)):
    wines = session.exec(
        select(Wine).where(Wine.is_archived == False).order_by(Wine.display_order)
    ).all()
    return [wine_to_dict(w) for w in wines]


@router.get("/archived")
def list_archived_wines(session: Session = Depends(get_session)):
    wines = session.exec(
        select(Wine).where(Wine.is_archived == True).order_by(Wine.display_order)
    ).all()
    return [wine_to_dict(w) for w in wines]


@router.get("/{wine_id}")
def get_wine(wine_id: int, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    return wine_to_dict(wine)


@router.post("", dependencies=[Depends(admin_required)])
def create_wine(data: WineIn, session: Session = Depends(get_session)):
    max_order = session.exec(select(Wine.display_order).order_by(Wine.display_order.desc())).first()
    wine = Wine(
        **{k: v for k, v in data.model_dump().items() if k != "food_pairings"},
        display_order=(max_order or 0) + 1,
    )
    session.add(wine)
    session.flush()
    for i, p in enumerate(data.food_pairings):
        session.add(WineFoodPairing(wine_id=wine.id, item=p.item, why=p.why, sort_order=i))
    session.commit()
    session.refresh(wine)
    return wine_to_dict(wine)


@router.put("/{wine_id}", dependencies=[Depends(admin_required)])
def update_wine(wine_id: int, data: WineIn, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    for k, v in data.model_dump(exclude={"food_pairings"}).items():
        setattr(wine, k, v)
    # Replace pairings
    for p in wine.food_pairings:
        session.delete(p)
    session.flush()
    for i, p in enumerate(data.food_pairings):
        session.add(WineFoodPairing(wine_id=wine.id, item=p.item, why=p.why, sort_order=i))
    session.commit()
    session.refresh(wine)
    return wine_to_dict(wine)


@router.patch("/{wine_id}/archive", dependencies=[Depends(admin_required)])
def archive_wine(wine_id: int, data: ArchiveIn, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    wine.is_archived = True
    wine.archived_date = data.archived_date
    wine.replaced_by = data.replaced_by
    wine.position = None  # free the Enomatic slot
    session.commit()
    session.refresh(wine)
    return wine_to_dict(wine)


@router.patch("/{wine_id}/restore", dependencies=[Depends(admin_required)])
def restore_wine(wine_id: int, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    wine.is_archived = False
    wine.archived_date = None
    wine.replaced_by = None
    session.commit()
    session.refresh(wine)
    return wine_to_dict(wine)


@router.patch("/{wine_id}/reorder", dependencies=[Depends(admin_required)])
def reorder_wine(wine_id: int, data: ReorderIn, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    other = session.exec(
        select(Wine).where(Wine.display_order == data.new_order)
    ).first()
    if other:
        other.display_order = wine.display_order
        session.add(other)
    wine.display_order = data.new_order
    session.commit()
    return {"ok": True}


@router.patch("/{wine_id}/position", dependencies=[Depends(admin_required)])
def set_position(wine_id: int, data: PositionIn, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    if data.position is not None and not (1 <= data.position <= 24):
        raise HTTPException(status_code=400, detail="Position must be between 1 and 24")
    if data.position is not None:
        # Bump whatever active wine currently holds this slot back to waiting
        occupant = session.exec(
            select(Wine).where(
                Wine.position == data.position,
                Wine.is_archived == False,
                Wine.id != wine_id,
            )
        ).first()
        if occupant:
            occupant.position = None
            session.add(occupant)
    wine.position = data.position
    session.commit()
    session.refresh(wine)
    return wine_to_dict(wine)


@router.delete("/{wine_id}", dependencies=[Depends(admin_required)])
def delete_wine(wine_id: int, session: Session = Depends(get_session)):
    wine = session.get(Wine, wine_id)
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    for p in wine.food_pairings:
        session.delete(p)
    session.delete(wine)
    session.commit()
    return {"ok": True}


@router.post("/research", dependencies=[Depends(admin_required)])
async def research_wine_endpoint(data: ResearchIn):
    result = await research_wine(
        data.name,
        producer=data.producer,
        region=data.region,
        varietal=data.varietal,
        vintage=data.vintage,
    )
    return result
