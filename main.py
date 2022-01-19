from fastapi import FastAPI

from api import main

app = FastAPI()
app.include_router(main.router)
