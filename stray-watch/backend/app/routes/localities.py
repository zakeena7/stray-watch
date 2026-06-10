from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Locality, Dog

router = APIRouter(prefix="/localities", tags=["localities"])


# ─── GET /localities ───────────────────────────────────────────────────────────
# Returns all localities with their risk score and live vaccination stats.
# This is what powers the map view and the dashboard cards.
@router.get("/")
def list_localities(db: Session = Depends(get_db)):
    localities = db.query(Locality).all()

    result = []
    for loc in localities:
        total      = len(loc.dogs)
        vaccinated = sum(1 for d in loc.dogs if d.vaccinated)
        coverage   = round((vaccinated / total * 100), 1) if total > 0 else 0.0

        result.append({
            "id":           loc.id,
            "name":         loc.name,
            "lat":          loc.lat,
            "lng":          loc.lng,
            "risk_score":   loc.risk_score,
            "last_survey":  loc.last_survey,
            "stats": {
                "total_dogs":       total,
                "vaccinated":       vaccinated,
                "unvaccinated":     total - vaccinated,
                "coverage_percent": coverage,
            }
        })

    return result


# ─── GET /localities/{id}/dogs ─────────────────────────────────────────────────
# Returns all dogs belonging to a specific locality.
# Optional filter: ?vaccinated=false to see only unvaccinated dogs
@router.get("/{locality_id}/dogs")
def dogs_in_locality(
    locality_id: int,
    vaccinated:  bool = None,  # optional filter
    db: Session = Depends(get_db)
):
    locality = db.query(Locality).filter(Locality.id == locality_id).first()
    if not locality:
        raise HTTPException(status_code=404, detail="Locality not found")

    query = db.query(Dog).filter(Dog.locality_id == locality_id)
    if vaccinated is not None:
        query = query.filter(Dog.vaccinated == vaccinated)

    dogs = query.all()

    return {
        "locality": locality.name,
        "count":    len(dogs),
        "dogs": [
            {
                "id":         d.id,
                "dog_code":   d.dog_code,
                "sex":        d.sex,
                "color":      d.color,
                "vaccinated": d.vaccinated,
                "vax_expiry": d.vax_expiry,
                "sterilized": d.sterilized,
            }
            for d in dogs
        ]
    }

class LocalityCreate(BaseModel):
    name: str
    lat: float
    lng: float

@router.post("/", status_code=201)
def create_locality(data: LocalityCreate, db: Session = Depends(get_db)):
    existing = db.query(Locality).filter(Locality.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Locality already exists")
    loc = Locality(name=data.name, lat=data.lat, lng=data.lng, risk_score=0)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return {"message": "Locality created", "id": loc.id, "name": loc.name}