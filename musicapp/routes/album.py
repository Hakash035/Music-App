from fastapi import APIRouter, HTTPException, status
from .. import database, models, schemas
from .auth import user_dep


router = APIRouter(
    tags = ["Album"],
    prefix="/album"
)


@router.get('/info/{albumId}', response_model=schemas.AlbumInfo)
def get_album(
    db: database.db_dependency,
    albumId: int
):
    
    """
    Get information about a specific album.

    Parameters:
    - db (Session): Database session dependency.
    - albumId (int): ID of the album to retrieve information for.

    Raises:
    - HTTPException: Raised with 404 status if the album is not found.

    Returns:
    - AlbumInfo: Information about the album.
    """

    # Retrieve the album by ID
    album = db.query(models.Album).filter(models.Album.id == albumId).first()

    # Check if the album exists
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Album Not Found"
        )

    # Return album information
    return album


@router.post('/create')
def create_album(
    db: database.db_dependency,
    user: user_dep,
    request : schemas.PostAlbum
):
    
    """
    Create a new album for a specific artist. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - albumName (str): Name of the new album.
    - artistId (int): ID of the artist for whom the album is created.
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
            detail="Only Admins can Create Albums!"
        )

    # Check if the album with the given name and artist ID already exists
    existing_album = db.query(models.Album).filter(
        models.Album.albumName == request.albumName,
        models.Album.artistId == request.artistId
    ).first()

    if existing_album:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Album Already Exists"
        )

    # Create a new album instance
    album = models.Album(albumName=request.albumName, artistId=request.artistId)

    # Add the new album to the database
    db.add(album)
    db.commit()
    db.refresh(album)

    # Return success message
    return {"detail": "Album Created Successfully"}


@router.put('/update')
def update_album(
    db: database.db_dependency,
    user: user_dep,
    request : schemas.EditAlbum
):
    
    """
    Update the name of a specific album. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - name (str): New name for the album.
    - albumId (int): ID of the album to be updated.
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
            detail="Only Admins can Update Albums!"
        )

    # Retrieve the album by ID
    album = db.query(models.Album).filter(models.Album.id == request.albumId).first()

    # Check if the album exists
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Album Not Found"
        )

    # Update the album name
    album.albumName = request.name
    db.commit()
    db.refresh(album)

    # Return success message
    return {"detail": "Album Updated Successfully"}


@router.delete('/delete/{albumId}')
def delete_album(
    db: database.db_dependency,
    albumId: int,
    user: user_dep
):
    
    """
    Delete a specific album. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - albumId (int): ID of the album to be deleted.
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
            detail="Only Admins can Delete Albums!"
        )

    # Retrieve the album by ID
    album = db.query(models.Album).filter(models.Album.id == albumId).first()

    # Check if the album exists
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Album Not Found"
        )

    # Delete the album
    db.delete(album)
    db.commit()

    # Return success message
    return {"detail": "Album Deleted Successfully"}


