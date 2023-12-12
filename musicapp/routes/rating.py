from fastapi import APIRouter
from .. import database, schemas, models

router = APIRouter(
    tags = ['Ratings']
)

@router.get('/{songId}/rating')
def get_rating(db: database.db_dependency, songId : int):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    return {"rating" : song.rating/song.noOfUsersRated}

@router.put('/{songId}/rate/{rating}')
def rate_song(songId : int, rating: float, db: database.db_dependency):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    song.rating = song.rating + rating
    song.noOfUsersRated += 1
    db.commit()
    db.refresh(song)
    return song