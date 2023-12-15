from fastapi import APIRouter, HTTPException, status
from .. import database, models, schemas
from .auth import user_dep

router = APIRouter(
    tags = ["Artist"]
)

@router.get('/artist/info/{artistId}', response_model=schemas.ShowArtistDetails)
def get_artist_info(db : database.db_dependency, artistId : str):
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist Not Found")
    return artist

@router.post('/artist/create/{artist}')
def create_artist(db : database.db_dependency, artist: str, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can create Artist!")
    artist = db.query(models.Artist).filter(models.Artist.artistName == artist).first()
    if artist:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Artist already Exists")
    artist = models.Artist(artistName = artist)
    db.add(artist)
    db.commit()
    db.refresh(artist)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Artist Created Successfully")

@router.put('/artist/update/{artistId}/{name}')
def update_artist(db : database.db_dependency, artistId : int, name : str, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can update Artist!")
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist Not Found")
    artist = db.query(models.Artist).filter(models.Artist.artistName == name).first()
    if artist:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Artist already Exists")
    artist.artistName = name
    db.add(artist)
    db.commit()
    db.refresh(artist)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Artist Updated Successfully")

@router.delete('/artist/delete/{artistId}')
def delete_genre(db : database.db_dependency, artistId : int,user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can delete Artist!")
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist Id Not Found")
    db.delete(artist)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Artist Deleted Successfully")


