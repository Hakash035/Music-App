import csv
from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routes import rating, auth, genre, artist, album, search
from .database import es

app = FastAPI()

origins = [
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different endpoints
# app.include_router(playlist.router)
app.include_router(rating.router)
app.include_router(search.router)
# app.include_router(songs.router)
app.include_router(auth.router)
app.include_router(genre.router)
app.include_router(artist.router)
app.include_router(album.router)

# Elasticsearch index creation
index_names = ["songs", "playlist"]

for index_name in index_names:
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

# # Create database tables
models.Base.metadata.create_all(database.engine)


# @app.post('/dump')
# async def dump_csv_file(file: UploadFile, db: database.db_dependency):

#     """
#     Endpoint to process and import data from a CSV file.

#     Parameters:
#         file (UploadFile): The CSV file to import.
#         db (Session): SQLAlchemy database session.

#     Raises:
#         HTTPException: If the file format is not CSV.

#     Returns:
#         HTTPException: Success message if data is added successfully.
#     """

#     # Check if the uploaded file is a CSV file
#     if file.content_type != 'text/csv':
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please Upload a CSV file!")

#     # Read content from the CSV file
#     content = await file.read()
#     content_str = content.decode("utf-8")

#     # Parse CSV lines
#     csv_lines = csv.reader(content_str.splitlines())

#     # Process each row in the CSV file
#     for row in csv_lines:
#         # Check if artist exists or create a new one
#         artist = db.query(models.Artist).filter(models.Artist.artistName == row[1]).first()
#         if not artist:
#             artist = models.Artist(artistName=row[1])
#             db.add(artist)
#             db.commit()

#         # Check if genre exists or create a new one
#         genre = db.query(models.Genre).filter(models.Genre.genreName == row[3]).first()
#         if not genre:
#             genre = models.Genre(genreName=row[3])
#             db.add(genre)
#             db.commit()

#         # Check if album exists or create a new one
#         album = db.query(models.Album).filter(models.Album.albumName == row[2]).first()
#         if not album:
#             album = models.Album(albumName=row[2], artistId=artist.id)
#             db.add(album)
#             db.commit()

#         # Check if the song exists or create a new one
#         song_instance = db.query(models.Songs).filter(models.Songs.songName == row[0]).first()
#         if not song_instance:
#             song = models.Songs(songName=row[0], artistId=artist.id, genreId=genre.id, albumId=album.id)
#             db.add(song)
#             db.commit()

#         # Index the song data in Elasticsearch
#         document = {
#             "songId": song_instance.id,
#             "songName": row[0],
#             "artistName": row[1],
#             "genreName": row[3],
#             "albumName": row[2]
#         }
#         response = es.index(index="songs", body=document, id=song_instance.id)

#     # Return success message
#     return { "detail" : "The Data is Added Successfully!" } 
