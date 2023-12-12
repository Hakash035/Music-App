from fastapi import APIRouter #, UploadFile
from .. import database, schemas, models
# from uuid import uuid4

router = APIRouter(
    tags = ["Songs"]
)

@router.put('/song/upload', response_model=schemas.ShowSong)
async def upload_songs(db : database.db_dependency, songName : str, genreId : int, artistId : int, albumId : int):
    # , file : UploadFile
    # file_id = uuid4()
    # data = await file.read()
    # file_name = f"{file_id}.{file.content_type.split("/")[1]}"
    # file_location = f"files/{file_id}.{file.content_type.split("/")[1]}"
    # with open(file_location, "wb+") as file_object:
    #     file_object.write(data)
    # file_object.close()
    #  fileName = file_name,
    db_song = models.Songs(songName = songName, genreId = genreId, artistId = artistId, albumId = albumId)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

@router.get('/song/{songId}', response_model=schemas.ShowSong)
def show_song(db : database.db_dependency, songId : int):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    return song
