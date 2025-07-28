from fastapi import FastAPI
from . import connectTest

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "asta e API-u. felicitari, mergi pe /artists"}


@app.get("/artists/")
async def root():
    return connectTest.artists_test_query()
