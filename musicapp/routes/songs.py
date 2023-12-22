from fastapi import APIRouter, HTTPException, status, UploadFile
from uuid import uuid4
from .. import database, schemas, models
from ..database import es
from .auth import user_dep

router = APIRouter(
    tags = ["Songs"],
    prefix="/song"
)


@router.get('/{songId}', response_model=schemas.ShowSong)
def show_song(db: database.db_dependency, songId: int):
    """
    Retrieve information about a specific song.

    Parameters:
        db (database.db_dependency): The database dependency.
        songId (int): The unique identifier of the song.

    Returns:
        schemas.ShowSong: Details of the requested song.

    Raises:
        HTTPException: If the song with the specified ID is not found (HTTP 404).
    """
    # Query the database to retrieve information about the song
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    # Check if the song exists
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Not Found!")

    # Return details of the requested song
    return song


@router.post('/upload', response_model=schemas.ShowSong)
async def upload_songs(
    db: database.db_dependency,
    songName: str,
    genreId: int,
    artistId: int,
    albumId: int,
    user: user_dep,
    file: UploadFile
):
    
    """
    Upload a new song to the database.

    Parameters:
        db (database.db_dependency): The database dependency.
        songName (str): The name of the song.
        genreId (int): The ID of the genre associated with the song.
        artistId (int): The ID of the artist associated with the song.
        albumId (int): The ID of the album associated with the song.
        user (user_dep): The current user's information.
        file (UploadFile): The audio file to be uploaded.

    Returns:
        schemas.ShowSong: Details of the uploaded song.

    Raises:
        HTTPException: If the user is not an admin (HTTP 401),
                       if the song with the specified name already exists (HTTP 302),
                       if the specified album, artist, or genre is not found (HTTP 404).
    """

    # Generate a unique file ID for the uploaded song
    file_id = uuid4()

    # Read the file data
    data = await file.read()

    # Create file name and location
    file_name = f"{file_id}.{file.content_type.split('/')[1]}"
    file_location = f"files/{file_name}"

    # Write the file to the specified location
    with open(file_location, 'wb+') as file_object:
        file_object.write(data)

    file_object.close()

    # Check if the user has admin privileges
    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Only Admins can create a song!"
        )

    # Check if the song with the specified name already exists
    existing_song = db.query(models.Songs).filter(models.Songs.songName == songName).first()
    if existing_song:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Song already exists!"
        )

    # Query the database for album, artist, and genre
    album = db.query(models.Album).filter(models.Album.id == albumId).first()
    genre = db.query(models.Genre).filter(models.Genre.id == genreId).first()
    artist = db.query(models.Artist).filter(models.Artist.id == artistId).first()

    # Check if the specified album, artist, and genre exist
    if not (album and genre and artist):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Please specify valid IDs for album, artist, and genre."
        )

    # Add the song to the database
    db_song = models.Songs(
        songName=songName,
        genreId=genreId,
        artistId=artistId,
        albumId=albumId
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)

    # Index the song in Elasticsearch
    document = {
        "songName": db_song.songName,
        "artistName": db_song.artist.artistName,
        "genreName": db_song.genre.genreName,
        "albumName": db_song.album.albumName
    }
    es.index(index="songs", body=document)

    # Return details of the uploaded song
    return db_song


@router.put('/edit/{songId}')
def edit_song(
    db: database.db_dependency,
    songId: int,
    req: schemas.EditSongRequest,
    user: user_dep
):
    
    """
    Edit details of an existing song.

    Parametrs:
        db (database.db_dependency): The database dependency.
        songId (int): The ID of the song to be edited.
        req (schemas.EditSongRequest): The request body containing updated song details.
        user (user_dep): The current user's information.

    Raises:
        HTTPException: If the user is not an admin (HTTP 401),
                       if the song with the specified ID is not found (HTTP 404),
                       if the specified album, artist, or genre is not found (HTTP 404).
    """

    # Check if the user has admin privileges
    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Only Admins can update a song!"
        )

    # Query the database for the existing song
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    # Check if the song with the specified ID exists
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song ID not found"
        )

    # Query the database for the specified album, artist, and genre
    album = db.query(models.Album).filter(models.Album.id == req.albumId).first()
    genre = db.query(models.Genre).filter(models.Genre.id == req.genreId).first()
    artist = db.query(models.Artist).filter(models.Artist.id == req.artistId).first()

    # Check if the specified album, artist, and genre exist
    if not (album and genre and artist):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Please specify valid IDs for album, artist, and genre."
        )

    # Update the song details
    song.songName = req.songName
    song.albumId = req.albumId
    song.artistId = req.artistId
    song.genreId = req.genreId

    # Commit changes to the database
    db.commit()
    db.refresh(song)

    # Update the indexed document in Elasticsearch
    document = {
        "songName": song.songName,
        "artistName": song.artist.artistName,
        "genreName": song.genre.genreName,
        "albumName": song.album.albumName
    }
    es.update(index="songs", id=song.id, doc=document)

    # Return success message
    return { "detail" : "Song updated successfully!" }


@router.delete('/delete/{songId}')
def delete_song(
    db: database.db_dependency,
    songId: int,
    user: user_dep
):
    
    """
    Delete a song by its ID.

    Parameters:
        db (database.db_dependency): The database dependency.
        songId (int): The ID of the song to be deleted.
        user (user_dep): The current user's information.

    Raises:
        HTTPException: If the user is not an admin (HTTP 401),
                      if the song with the specified ID is not found (HTTP 404).
    """

    # Check if the user has admin privileges

    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Only Admins can delete a song!"
        )

    # Query the database for the existing song
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    # Check if the song with the specified ID exists
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song ID not found"
        )

    # Delete the song from the database
    db.delete(song)
    db.commit()

    # Return success message
    return { "detail" : "Song deleted successfully!" }
