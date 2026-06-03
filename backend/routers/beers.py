from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.auth import admin_required
from backend.database import get_session
from backend.models import Beer

router = APIRouter(prefix="/api/beers", tags=["beers"])


class BeerIn(BaseModel):
    name: str
    brewery: str = ""
    location: str = ""
    style: str = ""
    type: str = ""
    abv: str = ""
    body: str = ""
    tasting: str = ""
    notes: str = ""


def beer_to_dict(beer: Beer) -> dict:
    return {
        "id": beer.id,
        "display_order": beer.display_order,
        "name": beer.name,
        "brewery": beer.brewery,
        "location": beer.location,
        "style": beer.style,
        "type": beer.type,
        "abv": beer.abv,
        "body": beer.body,
        "tasting": beer.tasting,
        "notes": beer.notes,
    }


@router.get("")
def list_beers(session: Session = Depends(get_session)):
    beers = session.exec(select(Beer).order_by(Beer.display_order)).all()
    return [beer_to_dict(b) for b in beers]


@router.get("/{beer_id}")
def get_beer(beer_id: int, session: Session = Depends(get_session)):
    beer = session.get(Beer, beer_id)
    if not beer:
        raise HTTPException(status_code=404, detail="Beer not found")
    return beer_to_dict(beer)


@router.post("", dependencies=[Depends(admin_required)])
def create_beer(data: BeerIn, session: Session = Depends(get_session)):
    max_order = session.exec(select(Beer.display_order).order_by(Beer.display_order.desc())).first()
    beer = Beer(**data.model_dump(), display_order=(max_order or 0) + 1)
    session.add(beer)
    session.commit()
    session.refresh(beer)
    return beer_to_dict(beer)


@router.put("/{beer_id}", dependencies=[Depends(admin_required)])
def update_beer(beer_id: int, data: BeerIn, session: Session = Depends(get_session)):
    beer = session.get(Beer, beer_id)
    if not beer:
        raise HTTPException(status_code=404, detail="Beer not found")
    for k, v in data.model_dump().items():
        setattr(beer, k, v)
    session.commit()
    session.refresh(beer)
    return beer_to_dict(beer)


@router.patch("/{beer_id}/reorder", dependencies=[Depends(admin_required)])
def reorder_beer(beer_id: int, new_order: int, session: Session = Depends(get_session)):
    beer = session.get(Beer, beer_id)
    if not beer:
        raise HTTPException(status_code=404, detail="Beer not found")
    other = session.exec(select(Beer).where(Beer.display_order == new_order)).first()
    if other:
        other.display_order = beer.display_order
        session.add(other)
    beer.display_order = new_order
    session.commit()
    return {"ok": True}


@router.delete("/{beer_id}", dependencies=[Depends(admin_required)])
def delete_beer(beer_id: int, session: Session = Depends(get_session)):
    beer = session.get(Beer, beer_id)
    if not beer:
        raise HTTPException(status_code=404, detail="Beer not found")
    session.delete(beer)
    session.commit()
    return {"ok": True}
