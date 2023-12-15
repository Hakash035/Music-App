from fastapi import APIRouter, HTTPException, status
from .. import database, schemas, models
from . import auth
from sqlalchemy import func


router = APIRouter(
    tags = ['Ratings']
)

@router.get('/rate/{songId}')
def get_rating(songId : int, db : database.db_dependency):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Not Found")
    average_rating = (
        db.query(func.avg(models.Rating.rating).label("average_rating"))
        .filter(models.Rating.songId == songId)
        .scalar()
    )
    if average_rating == None:
        average_rating = 0
    return {"rating" : average_rating}

@router.post('/rate/{songId}/{rating}')
def rate_song(user: auth.user_dep, songId : int, rating : float, db : database.db_dependency):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Not Found")
    if not (rating >= 0.0 or rating <= 5.0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be with the range of (0, 5)")
    rating_instance = db.query(models.Rating).filter(models.Rating.byUserId == user['id'], models.Rating.songId == songId).first()
    if rating_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You Have Rated this song Already!")
    rating = models.Rating(rating = rating, byUserId = user['id'], songId = songId)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Song is Rated Successfully!")

@router.put('/rate/edit/{songId}/{rating}')
def edit_rating(user: auth.user_dep, songId : int, rating : float, db : database.db_dependency):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Not Found")
    if not (rating >= 0.0 or rating <= 5.0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be with the range of (0, 5)")
    rating_instance = db.query(models.Rating).filter(models.Rating.byUserId == user['id'], models.Rating.songId == songId).first()
    if not rating_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You Haven't Rated this song yet!")
    rating_instance.rating = rating
    db.commit()
    db.refresh(rating_instance)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Song is Rating Updated!")

@router.delete('/rate/delete/{songId}')
def delete_rating(user: auth.user_dep, songId : int, db : database.db_dependency):
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Not Found")
    rating_instance = db.query(models.Rating).filter(models.Rating.byUserId == user['id'], models.Rating.songId == songId).first()
    if not rating_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You Haven't Rated this song yet!")
    db.delete(rating_instance)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Song is Rating Deleted!")