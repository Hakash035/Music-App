from fastapi import APIRouter
from .. import database, models, schemas
from ..database import es
from .auth import user_dep

router = APIRouter(
    tags = ["Search"]
)

#search by anything
@router.get('/search/{query}')
def search_query(query:str, user : user_dep):
    # document_query = {
    #     "query": {
    #         "multi_match": {
    #             "query": query,
    #             "fields": ["songName", "artistName", "albumName", "genreName"],
    #             "fuzziness": "AUTO"
    #         }
    #     }
    # }
    wildcard_query = {
        "query": {
            "query_string": {
                "query": f"*{query}*"
            }
        },
        "size" : 50
    }
    response = es.search(body=wildcard_query, index=["songs", "playlist"])

    # for res in response['hits']['hits']:
    #     if res['_index'] == "playlist" and res['_source']['creator'] == user['id']:
            
    return response['hits']['hits']


@router.get('/recommend')
def recommend_song(user : user_dep, db : database.db_dependency):
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()
    allSongs = []
    for playlist in user_playlist.playlists:
        for rec in playlist.playlistSong:
            record = {
                "_index" : "songs",
                "_id" : rec.songId
            }
            allSongs.append(record)
    print(allSongs)
    query = {
        "query" : {
            "more_like_this" : {
                "fields" : ["artistName", "albumName", "genreName"],
                "like" : allSongs,
                "min_term_freq": 1,
                "max_query_terms": 4
            }
        }
    }

    response = es.search(index="songs", body=query)
    
    return response['hits']['hits']
    # return 


# Fetch of users in the system, playlists in the system
# Search for songs, albums, """""playlist"""""

"""
1. add/show users to elastic search - easy
2. crud playlist in elastic search
2a. Think more like add songs to playlist !!!!
3. access control

4. Recommendation 
5. clean code/API Documentation         
"""                                                
# One user can recommend a particular song/an album/an artist/a genre to another user
# API Documentation

# s3?