from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from itertools import product

from .. import models, schemas, database
from .auth import user_dep
from ..database import es

router = APIRouter(
    tags=["Playlist"],
    prefix="/playlist"
)

@router.get('/getall', status_code=status.HTTP_200_OK)
def get_user_playlist(db: database.db_dependency, user: user_dep):

    """
    Retrieve all playlists for the authenticated user.

    Parameters:
    - db: Session, Database session dependency.
    - user: dict, Current user details.

    Returns:
    - List[Playlist]: List of playlists for the user.
    """

    # Query the database to get all playlists for the user ID
    user_playlist = db.query(models.Playlist).filter(models.Playlist.userId == user['id']).all()
    
    # Check if any playlists were found
    if not user_playlist:
        # Raise an HTTPException with a 404 status code and a detail message
        raise HTTPException(
            status_code=404, 
            detail="No Playlist Found!"
        )
    
    # Return the found playlists
    return user_playlist


@router.get(
        "/info/{playlistId}", 
        response_model=schemas.ShowPlaylistInfo, 
        status_code=status.HTTP_200_OK    
    )
def show_all_songs(
        db: database.db_dependency, 
        playlistId: int, 
        user: user_dep
    ):

    """
    Retrieve information about a playlist.

    Parameters:
        db (database.db_dependency): The database dependency.
        playlistId (int): The ID of the playlist to retrieve information for.
        user (user_dep): The current user's information.

    Returns:
        schemas.ShowPlaylistInfo: The information about the playlist.

    Raises:
        HTTPException: Raised with a 404 status code if the playlist is not found.
        HTTPException: Raised with a 403 status code if the user doesn't have access to the playlist.
    """


    # Query the database to find the playlist by playlistId
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()

    # Check if the playlist exists
    if not playlist:
        # Raise an HTTPException with a 404 status code if the playlist is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Playlist Doesn't Exist!"
        )

    # Check if the user has access to the playlist
    if playlist.users.id != user['id']:
        # Raise an HTTPException with a 403 status code if the user doesn't have access
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Playlist is Not Accessible!"
        )

    # Return the playlist information
    return playlist


@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_playlist(
        request: schemas.Playlist, 
        db: database.db_dependency, 
        user: user_dep
    ):

    """
    Create a new playlist.

    Parameters:
        request (schemas.Playlist): The request payload containing the playlist information.
        db (database.db_dependency): The database dependency.
        user (user_dep): The current user's information.

    Returns:
        models.Playlist: The newly created playlist.

    Raises:
        HTTPException: Raised with a 302 status code if the playlist already exists.
    """

    # Check if the playlist with the given name already exists
    existing_playlist = db.query(models.Playlist).filter(models.Playlist.playlistName == request.playlistName).first()
    
    if existing_playlist and existing_playlist.userId == user['id']:
        # Raise an HTTPException with a 302 status code if the playlist already exists
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Playlist Already Exists!"
        )

    # Create a new playlist instance and add it to the database
    new_playlist = models.Playlist(playlistName=request.playlistName, userId=user['id'])
    db.add(new_playlist)
    db.commit()

    # Index the playlist information in Elasticsearch
    playlist_document = {
        "playlistName": request.playlistName,
        "playlistId": new_playlist.id,
        "creator": user['id'],
        "playlistSong": []
    }
    es.index(index="playlist", body=playlist_document, id=new_playlist.id)

    # Refresh the database instance
    db.refresh(new_playlist)

    # Return the newly created playlist
    return new_playlist


@router.post('/create/condition/', status_code=status.HTTP_201_CREATED)
def create_by_condition(
    db: database.db_dependency,
    user: user_dep,
    request: schemas.CreateByCondition,
    artists: list[str] = Query(None, title="List of artists", description="Specify one or more artists"),
    genres: list[str] = Query(None, title="List of genres", description="Specify one or more genres"),
):
    
    """
    Create a playlist based on specified conditions.

    Parameters:
        db (database.db_dependency): The database dependency.
        user (user_dep): The current user's information.
        request (schemas.CreateByCondition): The request payload containing the playlist information.
        artists (list[str]): List of artists to consider in the playlist.
        genres (list[str]): List of genres to consider in the playlist.

    Returns:
        models.Playlist: The newly created playlist.

    Raises:
        HTTPException: Raised with a 302 status code if the playlist already exists.
        HTTPException: Raised with a 204 status code if no songs match the specified conditions.
        HTTPException: Raised with a 201 status code if the playlist is created successfully.
    """

    # Check if the playlist with the given name already exists
    existing_playlist = db.query(models.Playlist).filter(models.Playlist.playlistName == request.playlist).first()
    
    if existing_playlist:
        # Raise an HTTPException with a 302 status code if the playlist already exists
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Playlist Already Exists!"
        )

    # Generate combinations of artists and genres
    combination = list(product(artists, genres))
    res = []

    # Search for songs based on the specified conditions
    for pair in combination:
        query = {
            "query": {
                "bool": {
                    "must": [{"match_phrase": {"artistName": pair[0]}}, {"match_phrase": {"genreName": pair[1]}}]
                }
            },
            "size": 5
        }
        response = es.search(index="songs", body=query)
        res += response['hits']['hits']

    if not res:
        # Raise an HTTPException with a 204 status code if no songs match the specified conditions
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, 
            detail="No Songs Match your description!"
        )

    # Create a new playlist and add songs to it
    new_playlist = models.Playlist(playlistName=request.playlist, userId=user['id'])
    db.add(new_playlist)
    db.commit()

    songs = []
    for result in res:
        playlist_song = models.PlaylistSong(playlistId=new_playlist.id, songId=result["_source"]["songId"])
        songs.append(result["_source"]["songId"])
        db.add(playlist_song)
    
    db.commit()

    # Index the playlist information in Elasticsearch
    playlist_document = {
        "playlistName": request.playlist,
        "playlistId": new_playlist.id,
        "creator": user['id'],
        "playlistSong": songs
    }
    es.index(index="playlist", body=playlist_document)

    return { "detail" : "Playlist Created Successfully" }


@router.patch('/{playlistId}/add/{songId}', status_code=status.HTTP_200_OK)
def add_song_to_playlist(
        playlistId: int, 
        songId: int, 
        db: database.db_dependency, 
        user: user_dep
    ):

    """
    Add a song to a playlist.

    Parameters:
        playlistId (int): The ID of the playlist.
        songId (int): The ID of the song to be added.
        db (database.db_dependency): The database dependency.
        user (user_dep): The current user's information.

    Raises:
        HTTPException: Raised with a 404 status code if the playlist doesn't exist.
        HTTPException: Raised with a 403 status code if the playlist is not accessible by the user.
        HTTPException: Raised with a 404 status code if the song doesn't exist.
        HTTPException: Raised with a 302 status code if the song is already in the playlist.
        HTTPException: Raised with a 201 status code if the song is added to the playlist successfully.
    """

    # Check if the playlist exists
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()

    if not playlist:
        # Raise an HTTPException with a 404 status code if the playlist doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Playlist Doesn't Exist!"
        )

    # Check if the playlist is accessible by the user
    if playlist.users.id != user['id']:
        # Raise an HTTPException with a 403 status code if the playlist is not accessible
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Playlist is Not Accessible!"
        )

    # Check if the song exists
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()

    if not song:
        # Raise an HTTPException with a 404 status code if the song doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song Doesn't Exist!"
        )

    # Check if the song is already in the playlist
    songs = [i.songId for i in playlist.playlistSong]
    if songId in songs:
        # Raise an HTTPException with a 302 status code if the song is already in the playlist
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            detail="Song Already in Playlist!"
        )

    # Add the song to the playlist
    playlist_song = models.PlaylistSong(playlistId=playlistId, songId=songId)
    db.add(playlist_song)
    db.commit()

    # Update the playlist in Elasticsearch
    songs.append(songId)
    es.update(index="playlist", id=playlistId, doc={"playlistSong": songs})
    db.refresh(playlist_song)

    return { "detail" : "Song Added to the Playlist Successfully" }


@router.patch('/{playlistId}/remove/{songId}')
def del_song_from_playlist(
        user: user_dep, 
        playlistId: int, 
        songId: int, 
        db: database.db_dependency
    ):

    """
    Remove a song from a playlist.

    Parameters:
        user (user_dep): The current user's information.
        playlistId (int): The ID of the playlist.
        songId (int): The ID of the song to be removed.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the playlist doesn't exist.
        HTTPException: Raised with a 403 status code if the playlist is not accessible by the user.
        HTTPException: Raised with a 404 status code if the song doesn't exist in the playlist.
        HTTPException: Raised with a 200 status code if the song is removed from the playlist successfully.
    """

    # Check if the playlist exists
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()

    if not playlist:
        # Raise an HTTPException with a 404 status code if the playlist doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Playlist Doesn't Exist!"
        )

    # Check if the playlist is accessible by the user
    if playlist.users.id != user['id']:
        # Raise an HTTPException with a 403 status code if the playlist is not accessible
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Playlist is Not Accessible!"
        )

    # Check if the song exists in the playlist
    playlist_instance = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlistId == playlistId, 
        models.PlaylistSong.songId == songId
    ).first()

    if not playlist_instance:
        # Raise an HTTPException with a 404 status code if the song doesn't exist in the playlist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Song Doesn't Exist in Your Playlist!"
        )

    # Remove the song from the playlist
    es_playlist = es.get(index="playlist", id=playlistId)
    es_playlist.body['_source']['playlistSong'].remove(songId)

    db.delete(playlist_instance)
    db.commit()

    # Update the playlist in Elasticsearch
    es.update(index="playlist", id=playlistId, doc={"playlistSong": es_playlist.body['_source']['playlistSong']})

    # Raise an HTTPException with a 200 status code if the song is removed from the playlist successfully
    return { "detail" : "Songs Removed from the Playlist" }


@router.delete('/delete/{playlistId}')
def delete_playlist(
        user: user_dep, 
        playlistId: int, 
        db: database.db_dependency
    ):

    """
    Delete a playlist.

    Parameters:
        user (user_dep): The current user's information.
        playlistId (int): The ID of the playlist to be deleted.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the playlist doesn't exist.
        HTTPException: Raised with a 403 status code if the playlist is not accessible by the user.
        HTTPException: Raised with a 200 status code if the playlist is deleted successfully.
    """

    # Check if the playlist exists
    playlist_object = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()

    if not playlist_object:
        # Raise an HTTPException with a 404 status code if the playlist doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Playlist Not Found")

    # Check if the playlist is accessible by the user
    if playlist_object.users.id != user['id']:
        # Raise an HTTPException with a 403 status code if the playlist is not accessible
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Playlist is Not Accessible!"
        )

    # Delete the playlist
    db.delete(playlist_object)
    db.commit()

    # Delete the playlist from Elasticsearch
    es.delete(index="playlist", id=playlistId)

    # Raise an HTTPException with a 200 status code if the playlist is deleted successfully
    raise HTTPException(
        status_code=status.HTTP_200_OK, 
        detail="Playlist Deleted Successfully!"
    )

