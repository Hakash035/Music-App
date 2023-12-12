from fastapi import APIRouter, HTTPException
from .. import database, models

router = APIRouter(
    tags = ["Genre"]
)

@router.get("/genre/all")
def get_all_genre(db : database.db_dependency):
    all_genre = db.query(models.Genre).all()
    return all_genre

@router.post('/genre/create/{genre}')
def create_genre(db : database.db_dependency, genre : str):
    db_genre = models.Genre(genreName = genre)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

@router.put('/genre/edit/{genreId}/{editName}')
def edit_genre(db : database.db_dependency, genreId : int, editName : str):
    genre_instance = db.query(models.Genre).filter(models.Genre.id == genreId).first()
    if not genre_instance:
        raise HTTPException(status_code=404, detail="Genre Id Not Found")
    else:
        genre_instance.genreName = editName
        db.commit()
        db.refresh(genre_instance)
        return genre_instance
    
@router.delete('/genre/delete/{genreId}')
def delete_genre(db : database.db_dependency, genreId : int):
    genre_instance = db.query(models.Genre).filter(models.Genre.id == genreId).first()
    if not genre_instance:
        raise HTTPException(status_code=404, detail="Genre Id Not Found")
    else:
        db.delete(genre_instance)
        db.commit()
        return genre_instance



