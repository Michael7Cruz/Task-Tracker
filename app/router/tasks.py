from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel 
from typing import Annotated
import json
import datetime

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")

class Task(BaseModel):
    title: str
    description: str | None = None
    status: str = "todo"
    created_at: Annotated[datetime.datetime, datetime.datetime.now()] = datetime.datetime.now()
    updated_at: Annotated[datetime.datetime, datetime.datetime.now()] = datetime.datetime.now()

class Tasks(BaseModel):
    tasks: dict[int, Task]

def write_tasks_to_file(tasks: Tasks):
    with open("tasks.json", "w") as file:
        file.write(tasks.model_dump_json())

def read_tasks_from_file():
    with open("tasks.json", "r") as file:
        data = json.load(file)
        return Tasks.model_validate(data)

def delete_task_from_file(task_id: int):
    tasks = read_tasks_from_file()
    if task_id in tasks.tasks.keys():
        del tasks.tasks[task_id]
        write_tasks_to_file(tasks)

def mark_task_as_done(task_id: int):
    tasks = read_tasks_from_file()
    if task_id in tasks.tasks.keys():
        task = tasks.tasks[task_id]
        task.status = "done"
        task.updated_at = datetime.datetime.now()
        write_tasks_to_file(tasks)
    else:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

def mark_task_as_in_progress(task_id: int):
    tasks = read_tasks_from_file()
    if task_id in tasks.tasks.keys():
        task = tasks.tasks[task_id]
        task.status = "in-progress"
        task.updated_at = datetime.datetime.now()
        write_tasks_to_file(tasks)
    else:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

def mark_task_as_todo(task_id: int):
    tasks = read_tasks_from_file()
    if task_id in tasks.tasks:
        task = tasks.tasks[task_id]
        task.status = "todo"
        task.updated_at = datetime.datetime.now()
        write_tasks_to_file(tasks)
    else:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@router.post("/create")
async def create_tasks(tasks: Annotated[Tasks, Depends(write_tasks_to_file)]):
    return tasks

@router.post("/add")
async def add_task(task: Annotated[Task, Body()], tasks: Annotated[Tasks, Depends(read_tasks_from_file)]):
    task_id = max(tasks.tasks.keys(), default=0) + 1
    tasks.tasks[task_id] = task
    write_tasks_to_file(tasks)
    return {"message": f"Task added successfully with id {task_id}"}

@router.get("/read", response_class=HTMLResponse)
async def read_tasks(tasks: Annotated[Tasks, Depends(read_tasks_from_file)], request: Request):
    return templates.TemplateResponse(request=request, name="task.html", context=tasks.model_dump())

@router.put("/update/{task_id}")
async def update_task(task_id: int, task: Annotated[Task, Body()], tasks: Annotated[Tasks, Depends(read_tasks_from_file)]):
    stored_task = tasks.tasks[task_id]
    update_task = task.model_dump(exclude_unset=True)
    updated_tasks = stored_task.model_copy(update=update_task)
    write_tasks_to_file(Tasks(tasks={**tasks.tasks, task_id: updated_tasks}))
    return {"message": f"Task updated successfully"}

@router.put("/mark_done/{task_id}")
async def mark_task_done(task_id: int):
    mark_task_as_done(task_id)
    return {"message": f"Task with id {task_id} marked as done successfully"}

@router.put("/mark_in_progress/{task_id}")
async def mark_task_in_progress(task_id: int):
    mark_task_as_in_progress(task_id)
    return {"message": f"Task with id {task_id} marked as in-progress successfully"}

@router.put("/mark_todo/{task_id}")
async def mark_task_todo(task_id: int):
    mark_task_as_todo(task_id)
    return {"message": f"Task with id {task_id} marked as todo successfully"}

@router.delete("/delete/{task_id}")
async def delete_task(task_id: int):
    delete_task_from_file(task_id)
    return {"message": f"Task with id {task_id} deleted successfully"}

