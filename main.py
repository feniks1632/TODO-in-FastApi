from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List
from sqlalchemy import select, insert, update, delete

from database_model import database, Base, engine
from models import TaskCreate, TaskResponse, Task

# Асинхронный контекстный менеджер для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к базе данных при запуске приложения
    await database.connect()
    # Создание таблиц (если их нет)
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Отключение от базы данных при остановке приложения
    await database.disconnect()

# Создание FastAPI приложения с использованием lifespan
app = FastAPI(lifespan=lifespan)

# Получить список всех задач
@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks():
    query = select(Task)
    tasks = await database.fetch_all(query)
    return tasks

# Получить конкретную задачу по ID
@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    query = select(Task).where(Task.id == task_id)
    task = await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Нет такой задачи")
    return task

# Добавить задачу
@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    query = insert(Task).values(**task.model_dump())
    last_id = await database.execute(query)
    return {**task.model_dump(), "id": last_id}

# Обновить задачу по ID
@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, updated_task: TaskCreate):
    query = select(Task).where(Task.id == task_id)
    task = await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Нет такой задачи")
    update_query = update(Task).where(Task.id == task_id).values(**updated_task.model_dump())
    await database.execute(update_query)
    return {**updated_task.model_dump(), "id": task_id}

# Удалить задачу по ID
@app.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int):
    query = select(Task).where(Task.id == task_id)
    task = await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    delete_query = delete(Task).where(Task.id == task_id)
    await database.execute(delete_query)
    return task