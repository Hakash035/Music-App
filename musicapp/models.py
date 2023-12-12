from sqlalchemy import ARRAY, Column, Integer, String, Float, Boolean
from .database import Base

class Songs(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    songName = Column(String)
    fileName = Column(String)
    rating = Column(Float, default=0.0)
    noOfUsersRated = Column(Integer, default=0)
    artistName = Column(String)
    genreName = Column(String)
    albumName = Column(String)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    passwordHash = Column(String)
    # playlist = Column(ARRAY(Integer),  default=None, nullable=True)

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True, index=True)
    playlistName = Column(String)
    createdBy = Column(String)
    listOfSongs = Column(ARRAY(Integer)) 
    isAlbum = Column(Boolean, default=False)

class Artist(Base):
    __tablename__ = "artist"
    id = Column(Integer, primary_key=True, index=True)
    artistName = Column(String)

class Genre(Base):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True, index=True)
    genreName = Column(String)

class Suggestion(Base):
    __tablename__ = "suggest"
    id = Column(Integer, primary_key=True, index=True)
    byUser = Column(String)
    toUser = Column(String)
    typeOfSuggestion = Column(String)
    SuggestedItem = Column(String)
    # time




'''
songs
 - id
 - song name
 - summation of rating
 - no of users rated
 - artist
 - genre 
 - album
 - url

users
 - id
 - username
 - playlists
 - passwordhash

playlist
 - id 
 - playlist name
 - created by
 - isAlbum
 - list of songs(array of id)

artist
 - id
 - artist name

genre 
 - id
 - genre name

suggestions
 - id 
 - by 
 - to
 - type of suggestion(song/album/artist)
 - id of suggested item
'''




 