from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Dog, Locality
from datetime import datetime
import shutil, os, json

router = APIRouter(prefix="/dogs", tags=["dogs"])

UPLOAD_DIR = "uploads/dogs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── Helper: generate next dog code ───────────────────────────────────────────
def generate_dog_code(db: Session) -> str:
    count = db.query(Dog).count()
    return f"DOG-{str(count + 1).zfill(4)}"  # DOG-0001, DOG-0002 ...


# ─── GET /dogs ─────────────────────────────────────────────────────────────────
# Returns every dog in the registry.
# Optional query param: ?locality_id=2 to filter by area
@router.get("/")
def list_dogs(locality_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Dog)
    if locality_id:
        query = query.filter(Dog.locality_id == locality_id)
    dogs = query.all()

    return [
        {
            "id":          d.id,
            "dog_code":    d.dog_code,
            "locality_id": d.locality_id,
            "sex":         d.sex,
            "color":       d.color,
            "photo_path":  d.photo_path,
            "vaccinated":  d.vaccinated,
            "vax_expiry":  d.vax_expiry,
            "sterilized":  d.sterilized,
            "notes":       d.notes,
            "created_at":  d.created_at,
        }
        for d in dogs
    ]


# ─── GET /dogs/{id} ────────────────────────────────────────────────────────────
# Returns full detail for one specific dog by its numeric ID
@router.get("/{dog_id}")
def get_dog(dog_id: int, db: Session = Depends(get_db)):
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    return {
        "id":               dog.id,
        "dog_code":         dog.dog_code,
        "locality":         {"id": dog.locality.id, "name": dog.locality.name},
        "sex":              dog.sex,
        "color":            dog.color,
        "photo_path":       dog.photo_path,
        "vaccinated":       dog.vaccinated,
        "vax_date":         dog.vax_date,
        "vax_expiry":       dog.vax_expiry,
        "sterilized":       dog.sterilized,
        "notes":            dog.notes,
        "created_at":       dog.created_at,
        "sightings_count":  len(dog.sightings),
    }


# ─── POST /dogs ────────────────────────────────────────────────────────────────
# Registers a new dog. Send as multipart/form-data so you can include a photo.
@router.post("/", status_code=201)
def register_dog(
    locality_id: int,
    sex:         str  = "unknown",
    color:       str  = None,
    vaccinated:  bool = False,
    vax_date:    str  = None,   # pass as "YYYY-MM-DD"
    vax_expiry:  str  = None,   # pass as "YYYY-MM-DD"
    sterilized:  bool = False,
    notes:       str  = None,
    photo:       UploadFile = File(None),  # optional photo upload
    db:          Session = Depends(get_db),
):
    # 1. Check the locality actually exists
    locality = db.query(Locality).filter(Locality.id == locality_id).first()
    if not locality:
        raise HTTPException(status_code=404, detail="Locality not found")

    # 2. Save the photo file if one was uploaded
    photo_path = None
    if photo:
        filename   = f"{generate_dog_code(db)}_{photo.filename}"
        photo_path = os.path.join(UPLOAD_DIR, filename)
        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    # 3. Parse date strings into Python date objects
    parsed_vax_date   = datetime.strptime(vax_date,   "%Y-%m-%d") if vax_date   else None
    parsed_vax_expiry = datetime.strptime(vax_expiry, "%Y-%m-%d") if vax_expiry else None

    # 4. Create and save the dog record
    new_dog = Dog(
        dog_code    = generate_dog_code(db),
        locality_id = locality_id,
        sex         = sex,
        color       = color,
        photo_path  = photo_path,
        vaccinated  = vaccinated,
        vax_date    = parsed_vax_date,
        vax_expiry  = parsed_vax_expiry,
        sterilized  = sterilized,
        notes       = notes,
    )
    db.add(new_dog)
    db.commit()
    db.refresh(new_dog)

    return {"message": "Dog registered", "dog_code": new_dog.dog_code, "id": new_dog.id}


# ─── POST /dogs/identify ───────────────────────────────────────────────────────
# Upload a photo → AI compares it to all stored dogs → returns best match
@router.post("/identify")
def identify_dog(
    photo: UploadFile = File(...),
    db:    Session    = Depends(get_db),
):
    # Save the uploaded photo temporarily
    temp_path = f"uploads/temp_{photo.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    # Import the ML module and get embedding for the uploaded photo
    from app.ml.embeddings import get_embedding, cosine_similarity

    new_embedding = get_embedding(temp_path)
    os.remove(temp_path)  # clean up temp file

    # Fetch all dogs that have a stored embedding vector
    all_dogs = db.query(Dog).filter(Dog.embedding_vector != None).all()

    if not all_dogs:
        return {"match": None, "message": "No dogs with embeddings in registry yet"}

    # Compare new embedding against every stored one
    best_dog   = None
    best_score = -1.0

    for dog in all_dogs:
        stored_vector = dog.embedding_vector  # already a list (stored as JSON)
        score = cosine_similarity(new_embedding, stored_vector)
        if score > best_score:
            best_score = score
            best_dog   = dog

    confidence = round(best_score * 100, 1)

    # Confidence thresholds:
    #   >= 90  → auto match (very likely same dog)
    #   70–89  → needs human review (could be look-alike)
    #   < 70   → no match (register as new dog)
    if confidence >= 90:
        status = "matched"
    elif confidence >= 70:
        status = "needs_review"
    else:
        status = "no_match"

    return {
        "status":     status,
        "confidence": confidence,
        "match": {
            "id":        best_dog.id,
            "dog_code":  best_dog.dog_code,
            "color":     best_dog.color,
            "locality":  best_dog.locality.name,
            "vaccinated": best_dog.vaccinated,
        } if status != "no_match" else None,
        "message": {
            "matched":      "Dog already registered — no duplicate needed.",
            "needs_review": "Possible match found. Volunteer should confirm manually.",
            "no_match":     "No similar dog found. Please register as new.",
        }[status]
    }