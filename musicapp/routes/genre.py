from fastapi import APIRouter, HTTPException, status
from .. import database, models
from .auth import user_dep

router = APIRouter(
    tags = ["Genre"]
)

@router.get("/genre/all")
def get_all_genre(db : database.db_dependency):
    all_genre = db.query(models.Genre).all()
    return all_genre

@router.post('/genre/create/{genre}')
def create_genre(db : database.db_dependency, genre : str, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can create Genre!")
    genre_instance = db.query(models.Genre).filter(models.Genre.genreName == genre).first()
    if genre_instance:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Genre Already Exists!")
    db_genre = models.Genre(genreName = genre)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Genre Created Successfully")

@router.put('/genre/edit/{genreId}/{editName}')
def edit_genre(db : database.db_dependency, genreId : int, editName : str, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can update Genre!")
    genre_instance = db.query(models.Genre).filter(models.Genre.id == genreId).first()
    if not genre_instance:
        raise HTTPException(status_code=404, detail="Genre Id Not Found")
    genre_instance = db.query(models.Genre).filter(models.Genre.genreName == editName).first()
    if genre_instance:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Genre Already Exists!")
    genre_instance.genreName = editName
    db.commit()
    db.refresh(genre_instance)
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Genre Updated Successfully")
    
@router.delete('/genre/delete/{genreId}')
def delete_genre(db : database.db_dependency, genreId : int, user : user_dep):
    if user['role'] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Admins can Delete Genre!")
    genre_instance = db.query(models.Genre).filter(models.Genre.id == genreId).first()
    if not genre_instance:
        raise HTTPException(status_code=404, detail="Genre Id Not Found")
    db.delete(genre_instance)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Genre deleted Successfully")



