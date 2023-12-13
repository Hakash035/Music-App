from fastapi import APIRouter
from .. import database, models, schemas
from ..database import es

router = APIRouter(
    tags = ["Search"]
)

#search by anything
@router.get('/search/{query}')
def search_query(query:str):
    document_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["songName", "artistName", "albumName", "genreName"],
                "fuzziness": "AUTO"
            }
        }
    }
    wildcard_query = {
        "query": {
            "query_string": {
                "query": query
            }
        }
    }
    response = es.search(body=wildcard_query, index="songs")
    print(response['hits']['hits'])
    return {}


