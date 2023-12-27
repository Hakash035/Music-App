from fastapi import APIRouter, HTTPException, status
from .. import database, models, schemas
from .auth import user_dep
from ..services import accessControl, databaseServices

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


@router.post('/create')
def create_genre(
    db: database.db_dependency,
    user: user_dep,
    request : schemas.PostGenre
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
    accessControl.admin_access(user, "Create", "Genre")

    # Check if the genre with the given name already exists
    databaseServices.check_if_genre_exist(request)

    # Create a new genre instance
    db_genre = models.Genre(genreName=request.genre)

    # Add the new genre to the database
    databaseServices.add_commit_refresh(db_genre)

    # Return success message
    return {"detail": "Genre Created Successfully"}


@router.put('/edit')
def edit_genre(
    db: database.db_dependency,
    user: user_dep,
    request : schemas.EditGenre
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
    accessControl.admin_access(user, "Update", "Genre")

    # Check if the genre with the given ID exists
    genre_instance = databaseServices.check_if_genreId_exist(request)

    # Check if a genre with the new name already exists
    databaseServices.check_if_genre_exist(request)

    # Update the genre name
    genre_instance.genreName = request.genre
    databaseServices.commit_refresh(genre_instance)

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
    accessControl.admin_access(user, "Delete", "Genre")

    # Check if the genre exists
    genre_instance = databaseServices.check_if_genreId_exist(request={genreId : genreId})

    # Delete the genre
    databaseServices.delete_commit(genre_instance)

    # Return success message
    return {"detail": "Genre deleted successfully"}

