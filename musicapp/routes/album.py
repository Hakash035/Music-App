from fastapi import APIRouter
from .. import database, models

router = APIRouter(
    tags = ["Album"]
)

@router.post('/create-album/{albumName}/{artistId}')
def create_album(db : database.db_dependency, albumName : str, artistId : int):
    album = models.Album(albumName = albumName, artistId = artistId)
    db.add(album)
    db.commit()
    db.refresh(album)
    return album
