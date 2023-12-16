from fastapi import APIRouter, HTTPException, status
from .. import database, models
from .auth import user_dep

router = APIRouter(
    tags = ["Genre"],
    prefix="/genre"
)


@router.get("/all")
def get_all_genre(db: database.db_dependency):

    """
    Get a list of all genres.

    Parameters:
    - db (Session): Database session dependency.

    Returns:
    - List[Genre]: A list of all genres.
    """

    all_genre = db.query(models.Genre).all()
    return all_genre


@router.post('/create/{genre}')
def create_genre(
    db: database.db_dependency,
    genre: str,
    user: user_dep
):
    
    """
    Create a new genre. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - genre (str): Name of the new genre.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if creation is successful.
    """

    # Check if the user is an admin
    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only Admins can Create Genre!"
        )

    # Check if the genre with the given name already exists
    existing_genre = db.query(models.Genre).filter(models.Genre.genreName == genre).first()
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Genre Already Exists!"
        )

    # Create a new genre instance
    db_genre = models.Genre(genreName=genre)

    # Add the new genre to the database
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)

    # Return success message
    return {"detail": "Genre Created Successfully"}


@router.put('/edit/{genreId}/{editName}')
def edit_genre(
    db: database.db_dependency,
    genreId: int,
    editName: str,
    user: user_dep
):
    
    """
    Update the name of a genre by ID. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - genreId (int): ID of the genre to be updated.
    - editName (str): New name for the genre.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if the update is successful.
    """

    # Check if the user is an admin
    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only Admins can Update Genre!"
        )

    # Retrieve the genre instance by ID
    genre_instance = db.query(models.Genre).filter(models.Genre.id == genreId).first()

    # Check if the genre with the given ID exists
    if not genre_instance:
        raise HTTPException(
            status_code=404, 
            detail="Genre ID Not Found"
        )

    # Check if a genre with the new name already exists
    existing_genre = db.query(models.Genre).filter(models.Genre.genreName == editName).first()
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Genre Already Exists!"
        )

    # Update the genre name
    genre_instance.genreName = editName
    db.commit()
    db.refresh(genre_instance)

    # Return success message
    return {"detail": "Genre Updated Successfully"}


@router.delete('/delete/{genreId}')
def delete_genre(
    db: database.db_dependency,
    genreId: int,
    user: user_dep
):
    
    """
    Delete a genre by ID. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - genreId (int): ID of the genre to be deleted.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if deletion is successful.
    """

    # Check if the user is an admin
    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only Admins can Delete Genre!"
        )

    # Retrieve the genre instance by ID
    genre_instance = db.query(models.Genre).filter(models.Genre.id == genreId).first()

    # Check if the genre exists
    if not genre_instance:
        raise HTTPException(
            status_code=404, 
            detail="Genre ID Not Found"
        )

    # Delete the genre
    db.delete(genre_instance)
    db.commit()

    # Return success message
    return {"detail": "Genre deleted successfully"}

