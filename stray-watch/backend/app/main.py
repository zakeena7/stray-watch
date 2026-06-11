from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routes import dogs, localities, alerts
from apscheduler.schedulers.background import BackgroundScheduler
from app.routes.alerts import generate_alerts
from app.database import SessionLocal
# Create the FastAPI app instance
app = FastAPI(
    title="Stray Watch API",
    description="AI-powered stray dog registry and vaccination tracker",
    version="1.0.0",
)

# CORS middleware — this allows your React frontend (localhost:5173)
# to talk to this backend (localhost:8000) without browser errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This runs once when the server starts — creates all DB tables
@app.on_event("startup")
def startup():
    create_tables()
    print("Database tables ready.")

    def scheduled_job():
        db = SessionLocal()
        try:
            generate_alerts(db)
            print("Scheduled alert check complete.")
        finally:
            db.close()

    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, 'cron', hour=2, minute=0)
    scheduler.start()
    print("Scheduler started — alerts will run daily at 2AM.")

# Register all route files
app.include_router(dogs.router)
app.include_router(localities.router)
app.include_router(alerts.router)

# Health check — visit http://localhost:8000/ to confirm server is running
@app.get("/")
def root():
    return {"status": "Stray Watch API is running"}