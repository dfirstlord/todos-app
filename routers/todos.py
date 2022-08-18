import sys

sys.path.append("..")
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_execption

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=11, description="between 1-10")
    complete: bool


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_execption()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()


# @app.get("/todos/{id}")
# async def read_todo_id(id: int, db: Session = Depends(get_db)):
#     selected = db.query(models.Todos).filter(models.Todos.id == id).first()
#     if selected is not None:
#         return selected
#     raise http_exception()

@router.get("/{id}")
async def read_todo_id(id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_execption()
    selected = db.query(models.Todos).filter(models.Todos.id == id).filter(
        models.Todos.owner_id == user.get("id")).first()
    if selected is not None:
        return selected
    raise http_exception()


# @app.post("/todos")
# async def create_todo(todo: Todo, db: Session = Depends(get_db)):
#     data = models.Todos()
#     data.priority = todo.priority
#     data.description = todo.description
#     data.complete = todo.complete
#     data.title = todo.title
#
#     db.add(data)
#     db.commit()
#
#     return successful_response(200)

@router.post("/")
async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    data = models.Todos()
    data.priority = todo.priority
    data.description = todo.description
    data.complete = todo.complete
    data.title = todo.title
    data.owner_id = user.get("id")

    db.add(data)
    db.commit()

    return successful_response(200)


@router.put("/{id}")
async def update_todo(id: int, todo: Todo, db: Session = Depends(get_db)):
    selected = db.query(models.Todos).filter(models.Todos.id == id).first()
    if selected is None:
        raise http_exception()
    selected.title = todo.title
    selected.description = todo.description
    selected.priority = todo.priority
    selected.complete = todo.complete

    db.add(selected)
    db.commit()

    return successful_response(200)


@router.delete("/{id}")
async def delete_todo(id: int, db: Session = Depends(get_db)):
    selected = db.query(models.Todos).filter(models.Todos.id == id).first()
    if selected is None:
        raise http_exception()
    db.query(models.Todos).filter(models.Todos.id == id).delete()
    db.commit()
    return successful_response(200)


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")


def successful_response(status_code: int):
    return {
        "status": status_code,
        "transaction": "successful"
    }
