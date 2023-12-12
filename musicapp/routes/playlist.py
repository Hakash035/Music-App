from fastapi import APIRouter
from sqlalchemy.orm.attributes import flag_modified
from .. import models, schemas, database

router = APIRouter(
    tags= ["Playlist"]
)

@router.get('/{user}/playlists')
def get_user_playlist(user: str, db: database.db_dependency):
    user_playlist = db.query(models.Playlist).filter(models.Playlist.createdBy == user).all()
    return user_playlist

@router.post('/{user}/create/playlist')
def create_playlist(request : schemas.Playlist, user : str, db: database.db_dependency):
    db_playlist = models.Playlist(playlistName = request.playlistName, createdBy = user, listOfSongs = request.listOfSongs)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@router.delete('/{user}/delete/{playlistName}')
def delete_playlist(user : str, playlistName : str, db: database.db_dependency):
    playlist_object = db.query(models.Playlist).filter(models.Playlist.playlistName == playlistName).first()
    db.delete(playlist_object)
    db.commit()
    return playlist_object

# add songs to playlist
@router.put('/{user}/addsong/{playlist}/{songId}')
def add_song_to_playlist(user : str, playlist : str, songId : int,  db: database.db_dependency):
    playlist_instance = db.query(models.Playlist).filter(models.Playlist.playlistName == playlist).first()
    playlist_instance.listOfSongs = playlist_instance.listOfSongs + [songId]
    db.commit()
    db.refresh(playlist_instance)
    return playlist_instance

# delete songs to playlist
@router.put('/{user}/delsong/{playlist}/{songId}')
def del_song_to_playlist(user : str, playlist : str, songId : int,  db: database.db_dependency):
    playlist_instance = db.query(models.Playlist).filter(models.Playlist.playlistName == playlist).first()
    new_playlist = playlist_instance.listOfSongs
    new_playlist.remove(songId)
    print(new_playlist)
    playlist_instance.listOfSongs = new_playlist
    flag_modified(playlist_instance, "listOfSongs")
    db.commit()
    db.refresh(playlist_instance)
    return playlist_instance
