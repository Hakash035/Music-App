from fastapi import APIRouter
from .. import database, models, schemas

router = APIRouter(
    tags = ["Artist"]
)

@router.get('/artist/info/{artistId}', response_model=schemas.ShowArtistDetails)
def get_artist_info(db : database.db_dependency, artistId : str):
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()
    return artist

@router.post('/create-artist/{artist}')
def create_artist(db : database.db_dependency, artist: str):
    artist = models.Artist(artistName = artist)
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


