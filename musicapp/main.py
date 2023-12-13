from fastapi import FastAPI, Depends
from .database import get_db, es
from .routes import playlist, rating, songs, auth, genre, artist, album, search
from . import models, database

app = FastAPI()
app.include_router(playlist.router)
app.include_router(rating.router)
app.include_router(search.router)
app.include_router(songs.router)
app.include_router(auth.router)
app.include_router(genre.router)
app.include_router(artist.router)
app.include_router(album.router)

# Index name
index_name = "songs"

# Check if the index exists, if not, create it
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

models.Base.metadata.create_all(database.engine)

@app.get('/')
def index():
    return {"msg": "hello world"}