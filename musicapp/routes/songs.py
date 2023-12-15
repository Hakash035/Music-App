from fastapi import APIRouter, HTTPException, status #, UploadFile
from .. import database, schemas, models
from ..database import es
from .auth import user_dep
# from uuid import uuid4

router = APIRouter(
    tags = ["Songs"]
)

@router.get('/song/{songId}', response_model=schemas.ShowSong)
def show_song(db : database.db_dependency, songId : int):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Not Found!")
    return song

@router.put('/song/upload', response_model=schemas.ShowSong)
async def upload_songs(db : database.db_dependency, songName : str, genreId : int, artistId : int, albumId : int, user : user_dep):
    # , file : UploadFile
    # file_id = uuid4()
    # data = await file.read()
    # file_name = f"{file_id}.{file.content_type.split("/")[1]}"
    # file_location = f"files/{file_id}.{file.content_type.split("/")[1]}"
    # with open(file_location, "wb+") as file_object:
    #     file_object.write(data)
    # file_object.close()
    #  fileName = file_name,
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can create song!")
    song = db.query(models.Songs).filter(models.Songs.songName == songName).first()
    if song:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Song already Exists!")
    album = db.query(models.Album).filter(models.Album.id == albumId).first()
    genre = db.query(models.Genre).filter(models.Genre.id == genreId).first()
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()
    if not (album and genre and artist):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Please Specify the valid Id for album/artist/genre")
    db_song = models.Songs(songName = songName, genreId = genreId, artistId = artistId, albumId = albumId)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    document = {
        "songName" : db_song.songName,
        "artistName" : db_song.artist.artistName,
        "genreName" : db_song.genre.genreName,
        "albumName" : db_song.album.albumName
    }
    response = es.index(index="songs", body=document)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Song is Added to the Database")

@router.put('/song/edit/{songId}')
def edit_song(db : database.db_dependency, songId : int, req : schemas.EditSongRequest, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can update song!")
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song Id Not Found")
    album = db.query(models.Album).filter(models.Album.id == req.albumId).first()
    genre = db.query(models.Genre).filter(models.Genre.id == req.genreId).first()
    artist = db.query(models.Artist).filter(models.Artist.id == req.artistId).first()
    if not (album and genre and artist):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Please Specify the valid Id for album/artist/genre")
    song.songName = req.songName
    song.albumId = req.albumId
    song.artistId = req.artistId
    song.genreId = req.genreId
    db.commit()
    db.refresh(song)
    document = {
        "songName" : song.songName,
        "artistName" : song.artist.artistName,
        "genreName" : song.genre.genreName,
        "albumName" : song.album.albumName
    }
    response = es.update(index="songs", id = song.id, doc = document)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Song Updated Successfully!")
    
@router.delete('/song/delete/{songId}')
def delete_genre(db : database.db_dependency, songId : int, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can delete song!")
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song Id Not Found")
    db.delete(song)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Song Deleted Successfully!")