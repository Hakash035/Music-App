from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .. import schemas, models, database
from passlib.context import CryptContext

router = APIRouter(
    tags = ["Auth"]
)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash(password):
    return password_context.hash(password)

def verify_password(hashed_pass, plain_text):
    return password_context.verify(plain_text, hash=hashed_pass)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "247a39a660e0bd66be91493d7887ce1ba1f964e3c94462443275b1e4edf45840"
ALGORITHM = "HS256"

# creating the access token (JWT)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decoding the JWT to get user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # print(token, "here")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = {
        "username" : username,
        "id" : payload.get("id")
    }
    if user is None:
        raise credentials_exception
    return user


user_dep = Annotated[dict , Depends(get_current_user)]

@router.post('/token', response_model=schemas.Token, status_code=200)
async def login_token(request : Annotated[OAuth2PasswordRequestForm, Depends()], db: database.db_dependency):
    user = db.query(models.Users).filter(models.Users.username == request.username).first()
    if user:
       hash_pass = verify_password(user.passwordHash, request.password)
       if hash_pass:
        token = create_access_token({"username" : user.username, "id" : user.id, "role" : user.role})

        return {"access_token" : token, "token_type" : "bearer"}
       else:
        user = None
        raise HTTPException(status_code=401, detail="Password Incorrect")
    else:
        user = None
        raise HTTPException(status_code=404, detail="User Doesn't Exist")


@router.post('/signup', status_code=200)
def create_user(request:schemas.CreateUser, db: database.db_dependency):
    if request.password == request.confirmation:
        hash_pass = generate_hash(request.password)
        db_user = models.Users(username = request.username, passwordHash = hash_pass, role = request.role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password Don't Match")
    
