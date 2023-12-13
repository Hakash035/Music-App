from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm.attributes import flag_modified
from .. import models, schemas, database
from .auth import user_dep

router = APIRouter(
    tags= ["Playlist"]
)

@router.get('/playlist/getall', status_code=200)
def get_user_playlist(userId: int, db: database.db_dependency, user : user_dep):
    user_playlist = db.query(models.Playlist).filter(models.Playlist.userId == user['id']).all()
    if not user_playlist:
        raise HTTPException(status_code=404, detail="No Playlist Found!")
    return user_playlist

@router.post('/playlist/create', status_code=201)
def create_playlist(request : schemas.Playlist, db: database.db_dependency, user : user_dep):
    playlist = db.query(models.Playlist).filter(models.Playlist.playlistName == request.playlistName).first()
    if playlist:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Playlist Already Exists!")
    db_playlist = models.Playlist(playlistName = request.playlistName, userId = user['id'])
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@router.get("/playlist/info/{playlistId}", response_model=schemas.ShowPlaylistInfo, status_code=200)
def show_all_songs(db : database.db_dependency, playlistId : int, user : user_dep):
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist Doesn't Exists!")
    if playlist not in user_playlist.playlists:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    return playlist

# add songs to playlist
@router.put('/playlist/{playlistId}/add/{songId}', status_code=201)
def add_song_to_playlist( playlistId : int, songId : int,  db: database.db_dependency, user : user_dep):
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist Doesn't Exists!")
    if playlist not in user_playlist.playlists:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Doesn't Exists!")
    playlistSong = models.PlaylistSong(playlistId = playlistId, songId = songId)
    db.add(playlistSong)
    db.commit()
    db.refresh(playlistSong)
    raise HTTPException(status_code=200, detail="Song Added to the playlist")

# delete songs to playlist
@router.delete('/playlist/{playlistId}/remove/{songId}')
def del_song_to_playlist(user : user_dep, playlistId : int, songId : int,  db: database.db_dependency):
    playlist_instance = db.query(models.PlaylistSong).filter(models.PlaylistSong.playlistId == playlistId, models.PlaylistSong.songId == songId).first()
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist Doesn't Exists!")
    if playlist not in user_playlist.playlists:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    if not playlist_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Doesn't Exists in Your Playlist!")
    db.delete(playlist_instance)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Songs Removed from the playlist")

@router.delete('/playlist/delete/{playlistId}')
def delete_playlist(user : user_dep, playlistId : int, db: database.db_dependency):
    playlist_object = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()
    if not playlist_object:
        raise HTTPException(status_code=404, detail="Playlist Not found")
    if playlist_object not in user_playlist.playlists:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    db.delete(playlist_object)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Playlist Deleted Successfully!")