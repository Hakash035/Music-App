from pydantic import BaseModel
from typing import List


# Pydantic Models for Authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class CreateUser(BaseModel):
    username : str
    role : int
    password : str
    confirmation : str


# Below classes are defined for response model
class Artist(BaseModel):
    id : int
    artistName : str

    class Config:
        orm_mode = True

class Genre(BaseModel):
    genreName : str
    id : int

    class Config:
        orm_mode = True

class Album(BaseModel):
    albumName : str
    id : int

    class Config:
        orm_mode = True

class User(BaseModel):
    id : int
    username : str

class ShowRatingInfo(BaseModel):
    rating : float
    byUserId : User

class ShowSong(BaseModel):
    songName : str
    artist : Artist
    genre : Genre
    album : Album

    class Config:
        orm_mode = True

class AlbumInfo(BaseModel):
    id : int
    albumName : str
    songs : List[ShowSong]

    class Config:
        orm_mode = True

class PlaylistSongs(BaseModel):
    songs : ShowSong

    class Config:
        orm_mode = True

class ShowPlaylistInfo(BaseModel):
    id : int
    playlistName : str
    users : User
    playlistSong : List[PlaylistSongs]

    class Config:
        orm_mode = True

class ShowArtistDetails(BaseModel):
    id : int
    artistName : str
    songs : List[ShowSong]
    album : List[AlbumInfo]


# Below are Request Body Schemas
class CreateByCondition(BaseModel):
    playlist : str

class EditSongRequest(BaseModel):
    songName : str
    artistId : int
    genreId : int
    albumId : int

class Playlist(BaseModel):
    playlistName : str