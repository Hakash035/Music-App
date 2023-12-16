from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from .. import database, models
from . import auth


router = APIRouter(
    tags = ['Ratings'],
    prefix="/rate"
)


@router.get('/{songId}')
def get_rating(songId: int, db: database.db_dependency):

    """
    Get the average rating for a song.

    Parameters:
        songId (int): The ID of the song for which to retrieve the rating.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the song doesn't exist.

    Returns:
        dict: A dictionary containing the average rating for the song.
    """

    # Check if the song exists
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    if not song:
        # Raise an HTTPException with a 404 status code if the song doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song Not Found"
        )

    # Calculate the average rating for the song
    average_rating = (
        db.query(func.avg(models.Rating.rating).label("average_rating"))
        .filter(models.Rating.songId == songId)
        .scalar()
    )

    # Set average_rating to 0 if it is None
    average_rating = average_rating or 0

    # Return a dictionary containing the average rating
    return {"rating": average_rating}


@router.post('/{songId}/{rating}')
def rate_song(user: auth.user_dep, songId: int, rating: float, db: database.db_dependency):

    """
    Rate a song.

    Parameters:
        user (auth.user_dep): The authenticated user making the rating.
        songId (int): The ID of the song to be rated.
        rating (float): The rating to be given to the song.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the song doesn't exist.
        HTTPException: Raised with a 400 status code if the rating is not within the valid range.
        HTTPException: Raised with a 404 status code if the user has already rated the song.

    Returns:
        dict: A dictionary indicating the success of the rating operation.
    """

    # Check if the song exists
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    if not song:
        # Raise an HTTPException with a 404 status code if the song doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song Not Found"
        )

    # Check if the rating is within the valid range (0 to 5)
    if not (0.0 <= rating <= 5.0):
        # Raise an HTTPException with a 400 status code if the rating is not within the valid range
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Rating must be within the range of (0, 5)"
        )

    # Check if the user has already rated the song
    rating_instance = db.query(models.Rating).filter(
        models.Rating.byUserId == user['id'],
        models.Rating.songId == songId
    ).first()

    if rating_instance:
        # Raise an HTTPException with a 404 status code if the user has already rated the song
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="You Have Rated this song Already!"
        )

    # Create a new rating instance and add it to the database
    new_rating = models.Rating(rating=rating, byUserId=user['id'], songId=songId)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    # Return a dictionary indicating the success of the rating operation
    return {"detail": "Song is Rated Successfully!"}


@router.put('/edit/{songId}/{rating}')
def edit_rating(user: auth.user_dep, songId: int, rating: float, db: database.db_dependency):

    """
    Edit the rating of a song.

    Parameters:
        user (auth.user_dep): The authenticated user editing the rating.
        songId (int): The ID of the song whose rating is to be edited.
        rating (float): The new rating to be assigned to the song.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the song doesn't exist.
        HTTPException: Raised with a 400 status code if the rating is not within the valid range.
        HTTPException: Raised with a 404 status code if the user hasn't rated the song yet.

    Returns:
        dict: A dictionary indicating the success of the rating update operation.
    """

    # Check if the song exists
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    if not song:
        # Raise an HTTPException with a 404 status code if the song doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song Not Found"
        )

    # Check if the rating is within the valid range (0 to 5)
    if not (0.0 <= rating <= 5.0):
        # Raise an HTTPException with a 400 status code if the rating is not within the valid range
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Rating must be within the range of (0, 5)"
        )

    # Check if the user has rated the song
    rating_instance = db.query(models.Rating).filter(
        models.Rating.byUserId == user['id'],
        models.Rating.songId == songId
    ).first()

    if not rating_instance:
        # Raise an HTTPException with a 404 status code if the user hasn't rated the song yet
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="You Haven't Rated this song yet!"
        )

    # Update the rating of the song
    rating_instance.rating = rating
    db.commit()
    db.refresh(rating_instance)

    # Return a dictionary indicating the success of the rating update operation
    return {"detail": "Song Rating Updated Successfully!"}


@router.delete('/rate/delete/{songId}')
def delete_rating(user: auth.user_dep, songId: int, db: database.db_dependency):

    """
    Delete the rating of a song.

    Parameters:
        user (auth.user_dep): The authenticated user deleting the rating.
        songId (int): The ID of the song whose rating is to be deleted.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the song doesn't exist.
        HTTPException: Raised with a 404 status code if the user hasn't rated the song yet.

    Returns:
        dict: A dictionary indicating the success of the rating deletion operation.
    """

    # Check if the song exists
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    if not song:
        # Raise an HTTPException with a 404 status code if the song doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song Not Found"
        )

    # Check if the user has rated the song
    rating_instance = db.query(models.Rating).filter(
        models.Rating.byUserId == user['id'],
        models.Rating.songId == songId
    ).first()

    if not rating_instance:
        # Raise an HTTPException with a 404 status code if the user hasn't rated the song yet
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="You Haven't Rated this song yet!"
        )

    # Delete the rating of the song
    db.delete(rating_instance)
    db.commit()

    # Return a dictionary indicating the success of the rating deletion operation
    return {"detail": "Song Rating Deleted Successfully!"}
