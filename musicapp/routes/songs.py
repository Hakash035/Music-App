from fastapi import APIRouter, UploadFile
from .. import database, schemas, models
from uuid import uuid4

router = APIRouter(
    tags = ["Songs"]
)

@router.put('/song/upload')
async def upload_songs(db : database.db_dependency, file : UploadFile, songName : str, genreName : str, artistName : str):
    file_id = uuid4()
    data = await file.read()
    file_name = f"{file_id}.{file.content_type.split("/")[1]}"
    file_location = f"files/{file_id}.{file.content_type.split("/")[1]}"
    with open(file_location, "wb+") as file_object:
        file_object.write(data)
    file_object.close()
    db_song = models.Songs(songName = songName, genreName = genreName, artistName = artistName, fileName = file_name, albumName = "dummy")
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song