from ..database import db_dependency as db
from .. import models
from fastapi import HTTPException, status


# General Database Services
def add_commit_refresh(obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)

def commit_refresh(obj):
    db.commit()
    db.refresh(obj)

def delete_commit(obj):
    db.delete(obj)
    db.commit()

# Genre Related Services
def check_if_genre_exist(request):
    existing_obj = db.query(models.Genre).filter(models.Genre.genreName == request.genre).first()
    if existing_obj:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Genre Already Exists!"
        )
    
def check_if_genreId_exist(request):
    genre_instance = db.query(models.Genre).filter(models.Genre.id == request.genreId).first()
    if not genre_instance:
        raise HTTPException(
            status_code=404, 
            detail="Genre ID Not Found"
        )
    
    return genre_instance

# Artist Related Services
def retrive_artist_by_id(artistId):
    # Retrieve the artist by ID
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()

    # Check if the artist exists
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Artist Not Found"
        )
    
    return artist

def check_if_artist_exist(request):
    existing_artist = db.query(models.Artist).filter(models.Artist.artistName == request.artist).first()
    if existing_artist:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Artist already Exists"
        )