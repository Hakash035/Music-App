from fastapi import APIRouter
from .. import database, models, schemas
from ..database import es
from .auth import user_dep


router = APIRouter(
    tags = ["Search"]
)


@router.post('/search')
def search_query(user: user_dep, request : schemas.SearchQuery):

    """
    Search for songs and playlists based on a given query.

    Parameters:
        query (str): The search query.
        user (user_dep): The authenticated user.

    Returns:
        list: A list of search results, including songs and playlists.
    """

    # Define a wildcard query for Elasticsearch
    wildcard_query = {
        "query": {
            "query_string": {
                "query": f"*{request.query}*"
            }
        },
        "size": 50
    }

    # Perform a search using Elasticsearch
    response = es.search(body=wildcard_query, index=["songs", "playlist"])

    # Return the search results
    return response['hits']['hits']


@router.post('/recommend')
def recommend_song(user: user_dep, db: database.db_dependency):

    """
    Get song recommendations based on the user's playlists.

    Parameters:
        user (user_dep): The authenticated user.
        db (database.db_dependency): The database dependency.

    Returns:
        list: A list of recommended songs based on the user's playlists.
    """

    # Retrieve the user's playlist from the database
    user_playlist = db.query(models.Users).filter(models.Users.id == user['id']).first()

    # Create a list to store all songs from the user's playlists
    all_songs = []

    # Iterate through each playlist and its associated songs
    for playlist in user_playlist.playlists:
        for rec in playlist.playlistSong:
            record = {
                "_index": "songs",
                "_id": rec.songId
            }
            all_songs.append(record)

    # Build a query for Elasticsearch using the "more_like_this" feature
    query = {
        "query": {
            "more_like_this": {
                "fields": ["artistName", "albumName", "genreName"],
                "like": all_songs,
                "min_term_freq": 1,
                "max_query_terms": 6,
                "min_doc_freq": 1
            },
        }
    }

    # Perform a search using Elasticsearch
    response = es.search(index="songs", body=query)

    # Return the recommended songs
    return response['hits']['hits']


@router.post('/suggest')
def suggest_item(db: database.db_dependency, user : user_dep, request : schemas.SuggestItem):
    db_instance = models.Suggestion(
        byUserId = user['id'], 
        toUserId = request.toUserId, 
        typeOfSuggestion = request.suggestedType, 
        suggestedItem = request.suggestedItem
    )

    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)

    return {"detail" : "Suggestion Sent Successfully"}