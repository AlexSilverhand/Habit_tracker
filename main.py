from fastapi import FastAPI
from models import (
    CreateHabitCommand, MarkHabitDoneCommand,
    DeactivateHabitCommand
)
from protocol import (
    execute_create_habit,
    execute_mark_habit_done,
    execute_deactivate_habit,
    load_state
)

app = FastAPI(title="Habit Tracker Protocol")


@app.post("/habit/create")
def create_habit(cmd: CreateHabitCommand):
    return execute_create_habit(cmd)


@app.post("/habit/done")
def mark_done(cmd: MarkHabitDoneCommand):
    return execute_mark_habit_done(cmd)


@app.post("/habit/deactivate")
def deactivate_habit(cmd: DeactivateHabitCommand):
    return execute_deactivate_habit(cmd)


@app.get("/habit/{habit_id}")
def get_habit(habit_id: str):
    state = load_state()
    return state.get(habit_id, {"error": "Habit not found"})


@app.get("/habits")
def list_habits():
    return load_state()