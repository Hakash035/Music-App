from fastapi import APIRouter
from .. import database, models, schemas

router = APIRouter(
    tags = ["Recommend"]
)

@router.put('/recommend')
def recommend(request : schemas.Recommend, db : database.db_dependency):
    db_rec = models.Suggestion(byUser = request.byUser, toUser = request.toUser, typeOfSuggestion = request.typeOfSuggestion,  SuggestedItem = request.SuggestedItem)
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec