import csv
from fastapi import FastAPI, UploadFile, HTTPException, status
from . import models, database
from .routes import playlist, rating, songs, auth, genre, artist, album, search
from .database import es

app = FastAPI()
app.include_router(playlist.router)
app.include_router(rating.router)
app.include_router(search.router)
app.include_router(songs.router)
app.include_router(auth.router)
app.include_router(genre.router)
app.include_router(artist.router)
app.include_router(album.router)


index_name = "songs"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

index_name = "playlist"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)

models.Base.metadata.create_all(database.engine)

@app.post('/dump')
async def index(file : UploadFile, db : database.db_dependency):

    if file.content_type != 'text/csv':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please Upload a CSV file!")

    content = await file.read()
    content_str = content.decode("utf-8")

    csv_lines = csv.reader(content_str.splitlines())
    
    for row in csv_lines:

        artist = db.query(models.Artist).filter(models.Artist.artistName == row[1]).first()
        if not artist:
            artist = models.Artist(artistName = row[1])
            db.add(artist)
            db.commit()

        genre = db.query(models.Genre).filter(models.Genre.genreName == row[3]).first()
        if not genre:
            genre = models.Genre(genreName = row[3])
            db.add(genre)
            db.commit()

        album = db.query(models.Album).filter(models.Album.albumName == row[2]).first()
        if not album:
            album = models.Album(albumName = row[2], artistId = artist.id)
            db.add(album)
            db.commit()

        song_instance = db.query(models.Songs).filter(models.Songs.songName == row[0]).first()
        if not song_instance:
            song = models.Songs(songName = row[0], artistId = artist.id, genreId = genre.id, albumId = album.id)
            db.add(song)
            db.commit()

        document = {
            "songId" : song_instance.id, 
            "songName" : row[0],
            "artistName" : row[1],
            "genreName" : row[3],
            "albumName" : row[2]
        }
        response = es.index(index="songs", body=document, id=song_instance.id)
    
    raise HTTPException(status_code=status.HTTP_200_OK, detail="The Data is Added Successfully!")