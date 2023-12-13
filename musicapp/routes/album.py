from fastapi import APIRouter, HTTPException, status
from .. import database, models, schemas

router = APIRouter(
    tags = ["Album"]
)

@router.get('/album/info/{albumId}', response_model=schemas.AlbumInfo)
def get_album(db : database.db_dependency, albumId : int):
    album = db.query(models.Album).filter(models.Album.id == albumId).first()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album Not Found")
    return album

@router.post('/album/create/{artistId}/{albumName}')
def create_album(db : database.db_dependency, albumName : str, artistId : int):
    album = models.Album(albumName = albumName, artistId = artistId)
    db.add(album)
    db.commit()
    db.refresh(album)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Album Created Succesfully")

@router.put('/album/update/{albumId}/{name}')
def update_album(db : database.db_dependency, name : str, albumId : int):
    album = db.query(models.Album).filter(models.Album.id == albumId).first()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album Not Found")
    album.albumName = name
    db.commit()
    db.refresh(album)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Album Updated Successfully")

@router.delete('/album/delete/{albumId}')
def delete_album(db : database.db_dependency, albumId : int):
    album = db.query(models.Album).filter(models.Album.id == albumId).first()
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album Not Found")
    db.delete(album)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Album Deleted Successfully")

