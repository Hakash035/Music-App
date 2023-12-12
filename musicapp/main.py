from fastapi import FastAPI, Depends
from .database import get_db
from .routes import playlist, rating, recommend, songs, auth, genre, artist, album
from . import models, database

app = FastAPI()
app.include_router(playlist.router)
app.include_router(rating.router)
app.include_router(recommend.router)
app.include_router(songs.router)
app.include_router(auth.router)
app.include_router(genre.router)
app.include_router(artist.router)
app.include_router(album.router)

models.Base.metadata.create_all(database.engine)

@app.get('/')
def index():
    return {"msg": "hello world"}