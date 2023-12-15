from fastapi import APIRouter, HTTPException, status, Query
from .. import models, schemas, database
from .auth import user_dep
from ..database import es
from itertools import product

router = APIRouter(
    tags= ["Playlist"]
)

@router.get('/playlist/getall', status_code=200)
def get_user_playlist(db: database.db_dependency, user : user_dep):
    user_playlist = db.query(models.Playlist).filter(models.Playlist.userId == user['id']).all()
    if not user_playlist:
        raise HTTPException(status_code=404, detail="No Playlist Found!")
    return user_playlist

@router.get("/playlist/info/{playlistId}", response_model=schemas.ShowPlaylistInfo, status_code=200)
def show_all_songs(db : database.db_dependency, playlistId : int, user : user_dep):
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist Doesn't Exists!")
    if playlist not in user_playlist.playlists:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    return playlist

@router.post('/playlist/create', status_code=201)
def create_playlist(request : schemas.Playlist, db: database.db_dependency, user : user_dep):
    playlist = db.query(models.Playlist).filter(models.Playlist.playlistName == request.playlistName).first()
    if playlist:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Playlist Already Exists!")
    db_playlist = models.Playlist(playlistName = request.playlistName, userId = user['id'])
    db.add(db_playlist)
    db.commit()

    document = {
        "playlistName" : request.playlistName,
        "playlistId" : db_playlist.id,
        "creator" : user['id'],
        "playlistSong" : []
    }
    es.index(index="playlist", body = document, id = db_playlist.id)
    db.refresh(db_playlist)
    return db_playlist

@router.post('/playlist/create/condition/')
def create_by_condition(
    db : database.db_dependency,
    user: user_dep,
    request : schemas.CreateByCondition,
    artists: list[str] = Query(None, title="List of artists", description="Specify one or more artists"),
    genres: list[str] = Query(None, title="List of genres", description="Specify one or more genres"),
):
    
    combination = list(product(artists, genres))
    res = []
    for pair in combination:
        query = {
            "query" : {
                "bool" : {
                    "must" : [{"match_phrase" : {"artistName" : pair[0]}}, {"match_phrase" : {"genreName" : pair[1]}}]
                }
            },
            "size" : 25
        }
        response = es.search(index="songs", body=query)
        res = res + response['hits']['hits']

    if len(res) == 0:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No Songs Match your description!")
    
    playlist = models.Playlist(playlistName = request.playlist, userId = user['id'])
    db.add(playlist)
    db.commit()

    songs = []
    for result in res:
        playlistSong = models.PlaylistSong(playlistId = playlist.id, songId = result["_source"]["songId"])
        songs.append(result["_source"]["songId"])
        db.add(playlistSong)
    db.commit()

    document = {
        "playlistName" : request.playlist,
        "playlistId" : playlist.id,
        "creator" : user['id'],
        "playlistSong" : songs
    }

    es.index(index="playlist", body = document)

    return res
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Playlist Created Successfully" )

# add songs to playlist
@router.put('/playlist/{playlistId}/add/{songId}', status_code=201)
def add_song_to_playlist( playlistId : int, songId : int,  db: database.db_dependency, user : user_dep):
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    song = db.query(models.Songs).filter(models.Songs.id == songId).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist Doesn't Exists!")
    if playlist.users.id != user['id']:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Doesn't Exists!")
    songs = []
    for i in playlist.playlistSong:
        songs.append(i.songId)
        if i.songId == songId:
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Song Already in Playlist!")
    songs.append(songId)
    playlistSong = models.PlaylistSong(playlistId = playlistId, songId = songId)
    db.add(playlistSong)
    db.commit()

    es.update(index = "playlist", id = playlistId, doc={"playlistSong" : songs})
    db.refresh(playlistSong)
    raise HTTPException(status_code=200, detail="Song Added to the playlist")

# delete songs to playlist
@router.delete('/playlist/{playlistId}/remove/{songId}')
def del_song_to_playlist(user : user_dep, playlistId : int, songId : int,  db: database.db_dependency):
    playlist_instance = db.query(models.PlaylistSong).filter(models.PlaylistSong.playlistId == playlistId, models.PlaylistSong.songId == songId).first()
    playlist = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist Doesn't Exists!")
    if playlist.users.id != user['id']:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    if not playlist_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song Doesn't Exists in Your Playlist!")

    es_playlist = es.get(index="playlist", id = playlistId)
    es_playlist.body['_source']['playlistSong'].remove(songId)

    db.delete(playlist_instance)
    db.commit()

    es.update(index = "playlist", id = playlistId, doc={"playlistSong" : es_playlist.body['_source']['playlistSong']})

    raise HTTPException(status_code=status.HTTP_200_OK, detail="Songs Removed from the playlist")

@router.delete('/playlist/delete/{playlistId}')
def delete_playlist(user : user_dep, playlistId : int, db: database.db_dependency):
    playlist_object = db.query(models.Playlist).filter(models.Playlist.id == playlistId).first()
    if not playlist_object:
        raise HTTPException(status_code=404, detail="Playlist Not found")
    if playlist_object.users.id != user['id']:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Playlist is Not Accessable!")
    db.delete(playlist_object)
    db.commit()

    es.delete(index="playlist", id = playlistId)

    raise HTTPException(status_code=status.HTTP_200_OK, detail="Playlist Deleted Successfully!")