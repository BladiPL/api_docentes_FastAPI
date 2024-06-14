from fastapi import APIRouter, Response
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from schema.user_schema import UserSchema
from config.db import engine
from model.users import users
from werkzeug.security import generate_password_hash,check_password_hash
from typing import List

user = APIRouter()

@user.get("/")
def root():
    return {"message": "Hi , soy el router"}

@user.get("/api/user", response_model=List[UserSchema])
def get_users():
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
        users_list = [dict(row._asdict()) for row in result]  # Usar _asdict() para convertir la fila a diccionario
        return users_list
    
@user.get("/api/user/dni={user_id}", response_model=UserSchema)
def get_users(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == user_id)).first()
        return result

@user.post("/api/user", status_code=HTTP_201_CREATED)
def create_user(data_user: UserSchema):
    with engine.connect() as conn:
        new_user = data_user.dict(exclude_none=True)
        new_user["user_passw"] = generate_password_hash(data_user.user_passw,"pbkdf2:sha256:30",30)
        conn.execute(users.insert().values(new_user))
        conn.commit()
        return Response(status_code=HTTP_201_CREATED)

@user.put("/api/user/{user_id}",response_model=UserSchema)
def update_user(data_update: UserSchema, user_id: int):  # Asegúrate de que user_id sea un int
    with engine.connect() as conn:
        encrypt_passw = generate_password_hash(data_update.user_passw, "pbkdf2:sha256:30")
        conn.execute(users.update().values(
            name=data_update.name,
            username=data_update.username,
            user_passw=encrypt_passw
        ).where(users.c.id == user_id))
            
        conn.commit()
            
        result = conn.execute(users.select().where(users.c.id == user_id)).first()
        return dict(result._mapping)  # Convertir la fila a diccionario

@user.delete("/api/user/{user_id}", status_code=HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    with engine.connect() as conn:
        conn.execute(users.delete().where(users.c.id == user_id))
        conn.commit()
        return Response(status_code=HTTP_204_NO_CONTENT)
