from sqlalchemy import String, ForeignKey,Integer,column,Boolean
from sqlalchemy.orm import Mapped, mapped_column,DeclarativeBase,relationship
 
class Base (DeclarativeBase):
    pass

class UserModel(Base):
     __tablename__="users"
     id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
     username:Mapped[str]=mapped_column(String(50),nullable=False)
     email:Mapped[str]=mapped_column(String(100),unique=True,index=True,nullable=False)
     password:Mapped[str]=mapped_column(String(255),nullable=False)
     age:Mapped[int]=mapped_column(Integer ,nullable=False) 
     is_active:Mapped[bool]=mapped_column(default=True)
     posts:Mapped[list["PostModel"]]=relationship(back_populates="author")

class PostModel(Base):
     __tablename__="posts"
     id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
     title:Mapped[str]=mapped_column(String,nullable=False)
     content:Mapped[str]=mapped_column(nullable=False)

     author:Mapped["UserModel"]=relationship(back_populates="posts"  )
     author_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
     
