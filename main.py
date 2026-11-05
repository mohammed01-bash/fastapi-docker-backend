from fastapi import FastAPI, status,HTTPException , APIRouter,Depends , Response , BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import UserModel , PostModel
from schemas import UserCreate, UserResponse,UserUpdate , UserLogin,PostCreate,PostResponse , PostUpdate
from typing import List , Optional
from utils import hash_password , create_access_token,verify_password
from oauth2 import get_current_user
from fastapi.middleware.cors import CORSMiddleware 
import time

app=FastAPI()


origins=[
     "http://localhost:3000",
     "http://127.0.0.1:3000",
     "http://mon-app.com",
]
app.add_middleware(
     CORSMiddleware,
     allow_origins=origins,
     allow_credentials=True,
     allow_headers=["*"],
     allow_methods=["*"] ,
)


##simulation d'envoie d'un email de bienvenue (2 seconds)
def send_welcome_email(email:str , username:str):
     time.sleep(2)
     print(f"[BACKGROUND TASK] Email de bienvenue envoyé a {email} ({username})")



@app.post("/users",response_model= UserResponse,status_code=status.HTTP_201_CREATED)
def create_user(pyload:UserCreate,background_task:BackgroundTasks, db:Session=Depends(get_db)):
     user_exists = db.query(UserModel).filter(UserModel.email==pyload.email).first()
     if(user_exists):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"l'email{pyload.email}existe dans la base de données") 
     pyload.password=hash_password(pyload.password) #mot de pass hashé dans la BD
     new_user=UserModel(**pyload.model_dump())
     db.add(new_user)
     db.commit()
     db.refresh(new_user)
     background_task.add_task(send_welcome_email,email=new_user.email,username=new_user.username)
     return new_user


@app.get("/users",response_model=List[UserResponse])
def read_users(db:Session=Depends(get_db)):
    return db.query(UserModel).filter(UserModel.is_active==True).all()


@app.get("/users/{id}",response_model=UserResponse)
def read_user(id:int , db:Session=Depends(get_db)):
     active_user=db.query(UserModel).filter(UserModel.is_active==True,UserModel.id==id).first()
     if not(active_user) :
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No user with id {id}")
     else :
          return active_user  


@app.delete("/users/{id}", response_model=UserResponse)
def delete_user(id:int , db:Session=Depends(get_db)):
      user_active=db.query(UserModel).filter(UserModel.id==id,UserModel.is_active==True).first()
      if not (user_active) : 
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user {id} not found") 
      else : 
           user_active.is_active=False  
           db.commit()
           db.refresh(user_active)
      return user_active


@app.patch("/users/{id}",response_model=UserResponse)
def update_user(id:int , pyload:UserUpdate,db:Session=Depends(get_db)):
      user_to_update=db.query(UserModel).filter(UserModel.id==id,UserModel.is_active==True).first()
      if not (user_to_update):
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="not found")
      if pyload.email and pyload.email!=user_to_update.email:
           user_exists=db.query(UserModel).filter(UserModel.email==pyload.email).first()
           if(user_exists):
                 raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="email already exists")
      new_datas=pyload.model_dump(exclude_unset=True)
      for key , value in new_datas.items() :
          setattr(user_to_update,key,value)
      db.commit()
      db.refresh(user_to_update)
      return user_to_update   


@app.post("/posts",response_model=PostResponse)
def creat_post(pyload:PostCreate,db:Session=Depends(get_db), current_user:UserModel=Depends(get_current_user)):
     new_post=PostModel( **pyload.model_dump(),author_id=current_user.id)
     db.add(new_post)
     db.commit()
     db.refresh(new_post)
     return new_post

##Show all user posts by user id
@app.get("/users/{id}/posts",response_model=List [ PostResponse])
def read_user_posts(id:int , db:Session=Depends(get_db)):
     author_posts=db.query(PostModel).filter(PostModel.author_id==id).all()
     return author_posts

##Show only one post by id
@app.get("/posts/{id}",response_model=PostResponse)
def read_post(id:int, db:Session=Depends(get_db)):
     post=db.query(PostModel).filter(PostModel.id==id).first()   
     if not(post):
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
     return post


@app.delete("/users/{id}/posts",status_code=status.HTTP_200_OK)
def remove_all_posts(id:int , db:Session=Depends(get_db),current_user:UserModel=Depends(get_current_user)):
     if(id!=current_user.id):
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
     
     deleted_count=db.query(PostModel).filter(PostModel.author_id==id).delete(synchronize_session=False)
     db.commit()
     return{
          "message":"Les publication de l'utilisateur ont été supprimé avec succès" ,
          "deleted_count" : deleted_count
            }


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_post(id:int , db:Session=Depends(get_db),current_user:UserModel=Depends(get_current_user)):
     
     post_to_delete=db.query(PostModel).filter(PostModel.id==id).first()
     if not post_to_delete :
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
     if post_to_delete.author_id!=current_user.id :
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
     
     db.delete(post_to_delete)
     db.commit()
     return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch("/posts/{id}",response_model=PostResponse)
def update_post(id:int,pyload:PostUpdate,db:Session=Depends(get_db),current_user:UserModel=Depends(get_current_user)):
     post_to_update=db.query(PostModel).filter(PostModel.id==id).first()
     if not post_to_update:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
     if post_to_update.author_id != current_user.id :
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
     updated_post=pyload.model_dump(exclude_unset=True)
     for key, value in updated_post.items:
          setattr(post_to_update(),key,value)
     db.commit()
     db.refresh(post_to_update)
     return post_to_update


@app.post("/login",status_code=status.HTTP_200_OK)
def user_login(user_credentials:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):
      get_user=db.query(UserModel).filter(UserModel.email==user_credentials.username,UserModel.is_active==True).first()
      if not(get_user):
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User doesn't exist")
      if verify_password(user_credentials.password,get_user.password) :
          token_jwt = create_access_token({"user_id":get_user.id})
      else:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="info's dont match")
      return {"access_token":token_jwt,
             "token_type":"bearer"}


@app.get("/users/me",status_code=status.HTTP_200_OK)
def get_my_profile( current_user:UserModel=Depends(get_current_user)):

     return {"message":"Accès autorisé",
             "user":current_user}    


@app.get("/posts",response_model=list[PostResponse])
def search_posts(db:Session=Depends(get_db),limit:int=10,skip:int =0,search:Optional[str]=""):
     posts=( 
          db.query(PostModel)
          .filter(PostModel.title.contains(search))
          .limit(limit)
          .offset(skip)
          .all()
     )
     return posts
