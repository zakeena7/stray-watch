from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Alert, Locality, Dog
from app.ml.risk_score import calculate_risk_score
from datetime import datetime, timedelta

router = APIRouter(prefix="/alerts", tags=["alerts"])


# ─── GET /alerts ───────────────────────────────────────────────────────────────
# Returns all unresolved alerts, sorted with highest severity first.
# Frontend uses this to populate the Alerts page.
@router.get("/")
def get_alerts(db: Session = Depends(get_db)):
    # Severity order for sorting: high first, then medium, then info
    severity_order = {"high": 0, "medium": 1, "info": 2}

    alerts = db.query(Alert).filter(Alert.is_resolved == False).all()
    alerts.sort(key=lambda a: severity_order.get(a.severity, 3))

    return [
        {
            "id":           a.id,
            "type":         a.type,
            "severity":     a.severity,
            "message":      a.message,
            "locality":     a.locality.name if a.locality else None,
            "is_resolved":  a.is_resolved,
            "created_at":   a.created_at,
        }
        for a in alerts
    ]


# ─── POST /alerts/generate ─────────────────────────────────────────────────────
# This is the brain of the alert system.
# Call this endpoint to:
#   1. Recalculate risk scores for all localities
#   2. Scan for problems and create new alert records
# In production this runs automatically every night via APScheduler.
# During development you can trigger it manually from Thunder Client.
@router.post("/generate")
def generate_alerts(db: Session = Depends(get_db)):
    localities   = db.query(Locality).all()
    new_alerts   = []
    today        = datetime.utcnow()
    in_14_days   = today + timedelta(days=14)

    for loc in localities:
        dogs  = loc.dogs
        total = len(dogs)
        if total == 0:
            continue

        # ── Step 1: Recalculate risk score using your algorithm ──────────────
        vaccinated_count  = sum(1 for d in dogs if d.vaccinated)
        days_since_survey = (
            (today - loc.last_survey).days if loc.last_survey else 30
        )
        new_score = calculate_risk_score(
            total             = total,
            vaccinated        = vaccinated_count,
            days_since_survey = days_since_survey,
        )
        loc.risk_score = new_score  # update in DB

        # ── Step 2: Check if vaccination coverage is critically low ──────────
        coverage = vaccinated_count / total
        if coverage < 0.40:
            pct = round(coverage * 100)
            new_alerts.append(Alert(
                type        = "low_coverage",
                locality_id = loc.id,
                severity    = "high",
                message     = (
                    f"{loc.name}: only {pct}% of {total} dogs are vaccinated. "
                    f"Immediate vaccination drive recommended."
                ),
            ))

        # ── Step 3: Check for vaccines expiring within 14 days ───────────────
        expiring_soon = [
            d for d in dogs
            if d.vax_expiry and today <= d.vax_expiry <= in_14_days
        ]
        if expiring_soon:
            codes = ", ".join(d.dog_code for d in expiring_soon[:3])
            new_alerts.append(Alert(
                type        = "vax_expiring",
                locality_id = loc.id,
                severity    = "medium",
                message     = (
                    f"{loc.name}: {len(expiring_soon)} dog(s) have vaccinations "
                    f"expiring within 14 days ({codes}...)."
                ),
            ))

        # ── Step 4: Check if locality hasn't been surveyed in 7+ days ────────
        if days_since_survey >= 7:
            new_alerts.append(Alert(
                type        = "survey_overdue",
                locality_id = loc.id,
                severity    = "medium",
                message     = (
                    f"{loc.name} has not been surveyed in {days_since_survey} days. "
                    f"Schedule a volunteer visit."
                ),
            ))

    # Save all new alerts and updated risk scores to the database
    db.add_all(new_alerts)
    db.commit()

    return {
        "message":        "Alert generation complete",
        "alerts_created": len(new_alerts),
        "localities_updated": len(localities),
    }