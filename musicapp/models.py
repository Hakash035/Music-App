from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Songs(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    songName = Column(String)
    fileName = Column(String)
    artistId = Column(Integer, ForeignKey("artist.id", ondelete="CASCADE"))
    genreId = Column(Integer, ForeignKey("genre.id"))
    albumId = Column(Integer, ForeignKey("album.id", ondelete="CASCADE"))

    artist = relationship("Artist", back_populates="songs")
    genre = relationship("Genre", back_populates="songs")
    album = relationship("Album", back_populates="songs")
    playlistSong = relationship("PlaylistSong", back_populates="songs")
    rating = relationship("Rating", back_populates="songs")
    

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    role = Column(Integer) # 1 - admin, 2 - user
    passwordHash = Column(String)

    playlists = relationship("Playlist", back_populates="users", cascade="all, delete")
    rating = relationship("Rating", back_populates="users")


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    playlistName = Column(String)
    userId = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    playlistSong = relationship("PlaylistSong", back_populates="playlists", cascade="all, delete")
    users = relationship("Users", back_populates="playlists")


class PlaylistSong(Base):
    __tablename__ = "playlistSong"

    id = Column(Integer, primary_key=True, index=True)
    playlistId = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"))
    songId = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"))

    playlists = relationship("Playlist", back_populates="playlistSong")
    songs = relationship("Songs", back_populates="playlistSong")


class Artist(Base):
    __tablename__ = "artist"

    id = Column(Integer, primary_key=True, index=True)
    artistName = Column(String)

    songs = relationship("Songs", back_populates="artist", cascade="all, delete")
    album = relationship("Album", back_populates='artist', cascade="all, delete")


class Genre(Base):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True, index=True)
    genreName = Column(String)

    songs = relationship("Songs", back_populates="genre")


class Album(Base):
    __tablename__ = "album"

    id = Column(Integer, primary_key=True, index=True)
    albumName = Column(String)
    artistId = Column(Integer, ForeignKey("artist.id", ondelete="CASCADE"))

    artist = relationship("Artist", back_populates="album")
    songs = relationship("Songs", back_populates="album")


class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, default=0) 
    songId = Column(Integer, ForeignKey("songs.id"))
    byUserId = Column(Integer, ForeignKey("users.id"))

    users = relationship("Users", back_populates="rating")
    songs = relationship("Songs", back_populates="rating")