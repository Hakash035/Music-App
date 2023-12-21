# Introduction

## Objctive of the Task : 

  - MUSIC application which has a huge collection of songs. 
  - Songs are classified based on genre, artists, albums 
  - There are users who can login to the system to listen to the songs 
  - Each user can create his own playlist from the list of songs. Users can create more than one playlist. 
  - User can add or remove songs from their playlist 
  - One user can recommend a particular song/an album/an artist/a genre to another user 
  - Each user can rate any song 
  - User should be able to search a song by name/genre/artist/title 
  - System should be able to auto suggest songs to a user based on the songs that are present in their playlist. Can match to a genre/album/artist 
  - System should also be able to group songs and form playlists on its own based on any condition 

## Tech Stack Used : 

 - FastAPI
 - PosgreSQL
 - Elastic Search

## DB Schema :

Database Schema can be found in the below link

https://drawsql.app/teams/hakashs-team/diagrams/onboarding-task

## Elastic Search : 

For elastic search , there are 2 index 
 - songs
 - playlist

The Document in Songs will be of below format :
 - id( same as document ID )
 - songName
 - artistName
 - albumName
 - genreName

The Document in Songs will be of below format :
 - playlistId( same as document ID )
 - playlistName
 - creator( User ID )
 - playlistSong( array of songs )

## Authentication

The project is build on OAuth2 i.e password hashing, JWT Tokens. 

### Authentication Routes :

#### POST /token :

Endpoint to generate access token for user login.

    Parameters:
    - request: OAuth2PasswordRequestForm, Form containing username and password.
    - db: Session, Database session dependency.

    Returns:
    - dict: Access token and token type.

#### POST /signup

Endpoint to create a new user.

    Parameters:
    - request: CreateUser, Request body containing user information.
    - db: Session, Database session dependency.

    Returns:
    - Users: Newly created user.

### Song Routes :

#### GET /song/<span style="color:yellow;">{songID}</span>

Retrieve information about a specific song with songID.

    Parameters:
        db (database.db_dependency): The database dependency.
        songId (int): The unique identifier of the song.

    Returns:
        schemas.ShowSong: Details of the requested song.

    Raises:
        HTTPException: If the song with the specified ID is not found (HTTP 404).

#### PUT /song/upload

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

#### PUT /song/edit/<span style="color:yellow;">{songID}</span>

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

#### DELETE /song/delete/<span style="color:yellow;">{songID}</span>

Delete a song by its ID.

    Parameters:
        db (database.db_dependency): The database dependency.
        songId (int): The ID of the song to be deleted.
        user (user_dep): The current user's information.

    Raises:
        HTTPException: If the user is not an admin (HTTP 401),
                      if the song with the specified ID is not found (HTTP 404).

### Playlist Routes : 

#### GET /playlist/getall

Retrieve all playlists for the authenticated user.

    Parameters:
    - db: Session, Database session dependency.
    - user: dict, Current user details.

    Returns:
    - List[Playlist]: List of playlists for the user.

#### GET /playlist/info/<span style="color:yellow;">{PlaylistID}</span>

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

#### POST /playlist/create

Create a new playlist.

    Parameters:
        request (schemas.Playlist): The request payload containing the playlist information.
        db (database.db_dependency): The database dependency.
        user (user_dep): The current user's information.

    Returns:
        models.Playlist: The newly created playlist.

    Raises:
        HTTPException: Raised with a 302 status code if the playlist already exists.

#### POST /playlist/create/condition

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

#### PUT playlist/<span style="color:yellow;">{PlaylistID}</span>/add/<span style="color:yellow;">{SongID}</span>

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

#### DELETE /playlist/<span style="color:yellow;">{PlaylistID}</span>/remove/<span style="color:yellow;">{SongID}</span>

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

#### DELETE playlist/delete/<span style="color:yellow;">{PlaylistID}</span>

Delete a playlist.

    Parameters:
        user (user_dep): The current user's information.
        playlistId (int): The ID of the playlist to be deleted.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the playlist doesn't exist.
        HTTPException: Raised with a 403 status code if the playlist is not accessible by the user.
        HTTPException: Raised with a 200 status code if the playlist is deleted successfully.

### Search and Recommendaation Routes : 

This is achieved using Elastic Search querys

#### GET /search/Query

Search for songs and playlists based on a given query.

    Parameters:
        query (str): The search query.
        user (user_dep): The authenticated user.

    Returns:
        list: A list of search results, including songs and playlists.

#### GET /recommend

Get song recommendations based on the user's playlists.

    Parameters:
        user (user_dep): The authenticated user.
        db (database.db_dependency): The database dependency.

    Returns:
        list: A list of recommended songs based on the user's playlists.

### Rating Routes : 

#### GET /rate/<span style="color:yellow;">{SongID}</span>

Get the average rating for a song.

    Parameters:
        songId (int): The ID of the song for which to retrieve the rating.
        db (database.db_dependency): The database dependency.

    Raises:
        HTTPException: Raised with a 404 status code if the song doesn't exist.

    Returns:
        dict: A dictionary containing the average rating for the song.

#### POST /rate/<span style="color:yellow;">{SongID}</span>/<span style="color:yellow;">{Rating}</span>

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

#### PUT /rate/edit/<span style="color:yellow;">{SongID}</span>/<span style="color:yellow;">{Rating}</span>

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

#### DELETE rate/delete/<span style="color:yellow;">{SongID}</span>

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


### Genre Routes : 

#### GET /genre/all

Get a list of all genres.

    Parameters:
    - db (Session): Database session dependency.

    Returns:
    - List[Genre]: A list of all genres.

#### POST /genre/create/<span style="color:yellow;">{genre}</span>

Create a new genre. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - genre (str): Name of the new genre.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if creation is successful.

#### PUT /genre/edit/<span style="color:yellow;">{GenreID}</span/<span style="color:yellow;">{EditName}</span>

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

#### DELETE /genre/delete/<span style="color:yellow;">{GenreID}</span>

Delete a genre by ID. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - genreId (int): ID of the genre to be deleted.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if deletion is successful.

### Artist Routes : 

#### GET /artist/info/<span style="color:yellow;">{artistID}</span>

Get information about a specific artist.

    Parameters:
    - db (Session): Database session dependency.
    - artistId (int): ID of the artist to retrieve information for.

    Raises:
    - HTTPException: Raised with 404 status if the artist is not found.

    Returns:
    - ShowArtistDetails: Information about the artist.

#### POST /artist/create/<span style="color:yellow;">{artistName}</span>

Create a new artist. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - artist (str): Name of the new artist.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if creation is successful.

#### PUT /artist/update/<span style="color:yellow;">{artistID}</span/<span style="color:yellow;">{Name}</span>

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

#### DELETE /artist/delete/<span style="color:yellow;">{artistID}</span>

Delete a specific artist. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - artistId (int): ID of the artist to be deleted.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if deletion is successful.

### Album Routes : 

#### GET /album/info/<span style="color:yellow;">{albumID}</span>

Get information about a specific album.

    Parameters:
    - db (Session): Database session dependency.
    - albumId (int): ID of the album to retrieve information for.

    Raises:
    - HTTPException: Raised with 404 status if the album is not found.

    Returns:
    - AlbumInfo: Information about the album.

#### POST /album/create/<span style="color:yellow;">{artistID}</span>/<span style="color:yellow;">{albumName}</span>

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

#### PUT /album/update/<span style="color:yellow;">{albumID}</span>/<span style="color:yellow;">{name}</span>

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

#### DELETE /album/delete/<span style="color:yellow;">{albumID}</span>

Delete a specific album. Only admins are allowed to perform this operation.

    Parameters:
    - db (Session): Database session dependency.
    - albumId (int): ID of the album to be deleted.
    - user (dict): User information obtained from the dependency.

    Raises:
    - HTTPException: Raised for various HTTP status codes.

    Returns:
    - dict: Success message if deletion is successful.






