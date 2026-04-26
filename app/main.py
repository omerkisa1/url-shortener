from fastapi import FastAPI
from app.config import settings
from app.database import get_db

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status" : "ok"
    }