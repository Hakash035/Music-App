from fastapi import APIRouter, HTTPException, status
from .. import database, models, schemas
from .auth import user_dep


router = APIRouter(
    tags = ["Artist"],
    prefix="/artist"
)


@router.get('/info/{artistId}', response_model=schemas.ShowArtistDetails)
def get_artist_info(
        db: database.db_dependency, 
        artistId: int
    ):

    """
    Get information about a specific artist.

    Parameters:
    - db (Session): Database session dependency.
    - artistId (int): ID of the artist to retrieve information for.

    Raises:
    - HTTPException: Raised with 404 status if the artist is not found.

    Returns:
    - ShowArtistDetails: Information about the artist.
    """

    # Retrieve the artist by ID
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()

    # Check if the artist exists
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Artist Not Found"
        )

    # Return artist information
    return artist


@router.post('/create')
def create_artist(
        db: database.db_dependency, 
        request : schemas.PostArtist, 
        user: user_dep
    ):

    """
    Create a new artist. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - artist (str): Name of the new artist.
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
            detail="Only Admins can Create Artists!"
        )

    # Check if the artist with the given name already exists
    existing_artist = db.query(models.Artist).filter(models.Artist.artistName == request.artist).first()
    if existing_artist:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Artist already Exists"
        )

    # Create a new artist instance
    new_artist = models.Artist(artistName=request.artist)

    # Add the new artist to the database
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)

    # Return success message
    return {"detail": "Artist Created Successfully"}


@router.put('/update')
def update_artist(
        db: database.db_dependency, 
        request: schemas.EditArtist,
        user: user_dep
    ):

    """
    Update the name of a specific artist. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - artistId (int): ID of the artist to be updated.
    - name (str): New name for the artist.
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
            detail="Only Admins can Update Artists!"
        )

    # Retrieve the artist by ID
    artist = db.query(models.Artist).filter(models.Artist.id == request.artistId).first()

    # Check if the artist exists
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Artist Not Found"
        )
    
    # Retrieve the artist by Name
    artist = db.query(models.Artist).filter(models.Artist.artistName == request.name).first()

    # Check if the artist exists
    if artist:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Artist already Exists"
        )

    # Update the artist name
    artist.artistName = request.name
    db.commit()
    db.refresh(artist)

    # Return success message
    return {"detail": "Artist Updated Successfully"}


@router.delete('/delete/{artistId}')
def delete_artist(
        db: database.db_dependency, 
        artistId: int, 
        user: user_dep
    ):

    """
    Delete a specific artist. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - artistId (int): ID of the artist to be deleted.
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
            detail="Only Admins can Delete Artists!"
        )

    # Retrieve the artist by ID
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()

    # Check if the artist exists
    if not artist:
        raise HTTPException(
            status_code=404, 
            detail="Artist Id Not Found"
        )

    # Delete the artist
    db.delete(artist)
    db.commit()

    # Return success message
    return {"detail": "Artist Deleted Successfully"}
