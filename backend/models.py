from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class WineFoodPairing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wine_id: int = Field(foreign_key="wine.id")
    item: str
    why: str
    sort_order: int = Field(default=0)

    wine: Optional["Wine"] = Relationship(back_populates="food_pairings")


class Wine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    display_order: int = Field(index=True, default=0)
    is_archived: bool = Field(default=False, index=True)
    archived_date: Optional[str] = None
    replaced_by: Optional[str] = None

    name: str
    vintage: str
    type: str
    grape: str
    grape_detail: str = Field(default="")
    region: str = Field(default="")
    appellation: str = Field(default="")
    country: str = Field(default="")
    winemaker: str = Field(default="")
    tasting: str = Field(default="")
    food: str = Field(default="")
    alcohol: str = Field(default="")
    serving: str = Field(default="")
    notes: str = Field(default="")
    # Guest-facing tasting breakdown
    body: str = Field(default="")
    aromatics: str = Field(default="")
    palate: str = Field(default="")
    structure: str = Field(default="")
    finish: str = Field(default="")
    winemaking: str = Field(default="")
    story: str = Field(default="")
    pronunciation: Optional[str] = None
    pronunciation_guide_only: bool = Field(default=False)
    tech_sheet_url: Optional[str] = None

    food_pairings: List[WineFoodPairing] = Relationship(back_populates="wine")


class Beer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    display_order: int = Field(index=True, default=0)
    name: str
    brewery: str = Field(default="")
    location: str = Field(default="")
    style: str = Field(default="")
    type: str = Field(default="")
    abv: str = Field(default="")
    body: str = Field(default="")
    tasting: str = Field(default="")
    notes: str = Field(default="")


class FoodItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True)
    display_order: int = Field(default=0)
    name: str
    price: Optional[str] = None
    type: str = Field(default="")
    description: str = Field(default="")
    pairings: Optional[str] = None
    origin: Optional[str] = None
    pronunciation: Optional[str] = None
