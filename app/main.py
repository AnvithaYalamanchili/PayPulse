from .database import SessionLocal
from fastapi import FastAPI
from . import models, database
from .routers import users,plans

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(users.router)
app.include_router(plans.router)
@app.get("/")
def root():
    return {"message": "Welcome to the API!"}
