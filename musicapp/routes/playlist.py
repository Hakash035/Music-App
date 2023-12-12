from fastapi import APIRouter, HTTPException
from sqlalchemy.orm.attributes import flag_modified
from .. import models, schemas, database

router = APIRouter(
    tags= ["Playlist"]
)

@router.get('/{userId}/playlists')
def get_user_playlist(userId: int, db: database.db_dependency):
    user_playlist = db.query(models.Playlist).filter(models.Playlist.userId == userId).all()
    return user_playlist

@router.post('/{userId}/create/playlist')
def create_playlist(request : schemas.Playlist, userId : int, db: database.db_dependency):
    db_playlist = models.Playlist(playlistName = request.playlistName, userId = userId)
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@router.get("/{playlistId}/show-all", response_model=schemas.ShowPlaylistInfo)
def show_all_songs(db : database.db_dependency, playlistId : int):
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    return playlist



# add songs to playlist
@router.put('/{user}/addsong/{playlistId}/{songId}')
def add_song_to_playlist(user : str, playlistId : int, songId : int,  db: database.db_dependency):
    # playlist_instance = db.query(models.Playlist).filter(models.Playlist.playlistName == playlist).first()
    # playlist_instance.listOfSongs = playlist_instance.listOfSongs + [songId]
    playlistSong = models.PlaylistSong(playlistId = playlistId, songId = songId)
    db.add(playlistSong)
    db.commit()
    db.refresh(playlistSong)
    return {"detail" : "song added to playlist"}

# delete songs to playlist
@router.delete('/{user}/delsong/{playlistId}/{songId}')
def del_song_to_playlist(user : str, playlistId : int, songId : int,  db: database.db_dependency):
    playlist_instance = db.query(models.PlaylistSong).filter(models.PlaylistSong.playlistId == playlistId, models.PlaylistSong.songId == songId).first()
    # new_playlist = playlist_instance.listOfSongs
    # new_playlist.remove(songId)
    # print(new_playlist)
    # playlist_instance.listOfSongs = new_playlist
    # flag_modified(playlist_instance, "listOfSongs")
    db.delete(playlist_instance)
    db.commit()
    return {"detail" : "song deleted from playlist"}

@router.delete('/playlist/{user}/delete/{playlistId}')
def delete_playlist(user : str, playlistId : int, db: database.db_dependency):
    playlist_object = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    if not playlist_object:
        raise HTTPException(status_code=404, detail="Playlist Not found")
    else:
        db.delete(playlist_object)
        db.commit()
        return playlist_object