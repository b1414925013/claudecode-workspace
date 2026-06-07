from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search, play, download, lyrics, rankings

app = FastAPI(title="Music API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(play.router, prefix="/api/play", tags=["play"])
app.include_router(download.router, prefix="/api/download", tags=["download"])
app.include_router(lyrics.router, prefix="/api/lyrics", tags=["lyrics"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["rankings"])

@app.get("/")
def root():
    return {"message": "Music API Server"}