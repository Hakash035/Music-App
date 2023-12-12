from pydantic import BaseModel

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


