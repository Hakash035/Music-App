from pydantic import BaseModel
from typing import List

class SongSchema(BaseModel):
    songname : str
    url : str

class CreateUser(BaseModel):
    username : str
    password : str
    confirmation : str

class Login(BaseModel):
    username : str
    password : str

class Playlist(BaseModel):
    playlistName : str
    listOfSongs : list

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class Song(BaseModel):
    songName : str
    genreName : str
    artistName : str

class Recommend(BaseModel):
    byUser: str
    toUser: str
    typeOfSuggestion : str
    SuggestedItem: str

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



class ShowSong(BaseModel):
    songName : str
    rating : float
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