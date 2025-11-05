# main.py (or dependencies.py)
from .database import SessionLocal
from fastapi import FastAPI
from . import models, database
from .routers import users  # <-- Import your users.py router file

# Create the FastAPI app
app = FastAPI()

# Create database tables (only once)
models.Base.metadata.create_all(bind=database.engine)

# Include the router
app.include_router(users.router)

# Optional root route
@app.get("/")
def root():
    return {"message": "Welcome to the API!"}
