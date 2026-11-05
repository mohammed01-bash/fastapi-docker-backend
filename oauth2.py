from fastapi import Depends,status , HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from database import get_db
from models import UserModel ,PostModel
from utils import SECRET_KEY,ALGORITHM


oauth2_schema= OAuth2PasswordBearer(tokenUrl="login")


def get_current_user( db:Session=Depends(get_db),token: str=Depends(oauth2_schema)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,
                                         detail="impossible de valider les identifiants",
                                         headers={"WWW-Authenticate":"Bearer"}
                                         )
    try :
        pyload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=pyload.get("user_id")
        if not user_id : 
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401 , detail="expired")
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user=db.query(UserModel).filter(UserModel.id==user_id).first()
    if not user :
        raise credentials_exception
    return user