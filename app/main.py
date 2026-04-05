from fastapi import FastAPI, staticfiles
from .router import tasks
app = FastAPI()
app.include_router(tasks.router)