from sqlalchemy.orm import Session,selectinload,joinedload
from sqlalchemy import  select,func,or_
from typing import Optional,List,Tuple
from math import ceil
from app.model import UserORM,AnalisisORM
from app.api.v1.users.schemas import UserCreate
from pydantic import EmailStr


class UserRepository:
    def __init__(self, db : Session):
        self.db = db

    def get(self,post_id:int ) ->Optional[UserORM]:
                #select si es más sencible y poner filtros 
        post_find = select(UserORM).where(UserORM.id == post_id) #sirve para buscar por el id 
        post = self.db.execute(post_find).scalar_one_or_none()
        return post 

    def create(self, name:str,email:str,password:str)-> UserORM:

        new_user = UserORM(name = name,email=email,password=password)

        self.db.add(new_user)
        self.db.flush()
        self.db.refresh(new_user)

        return new_user
        

    def get_by_id(self, user_id: int)-> UserORM | None:
        user_find = select(UserORM).where(UserORM.id == user_id)
        user = self.db.execute(user_find).scalar_one_or_none()
        return user
    

    def get_all_users(self)-> List[UserORM]:
        query = select(UserORM)
        result = self.db.execute(query)
        return result.scalar_one_or_none()
    
    def search(self,
               query: Optional[str],
               order_by:str,
               direction:str,
               page:int,
               per_page:int
               )-> Tuple[int,List[UserORM]]:
        
        results = select(UserORM)

        if query:
            # Busca si el query coincide con el email O con el name
            results = results.where(
                or_(
                    UserORM.email.ilike(f"%{query}%"),
                    UserORM.name.ilike(f"%{query}%")
                )
            )

        total = self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
        if total == 0:
            return 0,[]
        
        total_pages = ceil(total/per_page)

        current_page = min(page,max(1,total_pages))

        if order_by == "name":
            order_col = UserORM.name
        else:
            order_col = UserORM.email
        
        results = results.order_by(order_col.asc() if direction == "asc" else order_col.desc())

        start = (current_page - 1) * per_page
        items = self.db.execute(results.limit(per_page).offset(start)).scalars().all()

        return total,items

    def update_user(self,user_id:int, updates:dict) -> UserORM:
        for key, value in updates.items():
            setattr(user_id, key, value)

        self.db.add(user_id)
        # self.db.refresh(post)
        return user_id
    
    def get_by_email(self, email: str) -> Optional[UserORM]:
        query = select(UserORM).where(UserORM.email == email)
        result = self.db.execute(query).scalar_one_or_none()
        return result