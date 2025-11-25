import json
from uuid import uuid4
from datetime import date
from models import (
    HabitModel, HabitState,
    CreateHabitCommand, MarkHabitDoneCommand, DeactivateHabitCommand
)

STATE_FILE = "state_store.json"


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


# ------------------------------
# COMANDO: Crear hábito
# ------------------------------
def execute_create_habit(cmd: CreateHabitCommand):
    state = load_state()

    habit_id = str(uuid4())

    habit = HabitModel(
        id=habit_id,
        name=cmd.name,
        description=cmd.description,
        goal_per_week=cmd.goal_per_week,
        completions=[],
        state=HabitState.ACTIVE
    )

    state[habit_id] = habit.dict()
    save_state(state)

    return habit


# ------------------------------
# COMANDO: Marcar hábito como hecho
# ------------------------------
def execute_mark_habit_done(cmd: MarkHabitDoneCommand):
    state = load_state()

    if cmd.habit_id not in state:
        return {"error": "Habit not found"}

    habit = state[cmd.habit_id]

    if habit["state"] == HabitState.INACTIVE:
        return {"error": "Habit is inactive"}

    # Registrar la fecha de cumplimiento
    if cmd.day not in habit["completions"]:
        habit["completions"].append(cmd.day)

    habit["state"] = HabitState.COMPLETED_TODAY

    state[cmd.habit_id] = habit
    save_state(state)

    return habit


# ------------------------------
# COMANDO: Desactivar hábito
# ------------------------------
def execute_deactivate_habit(cmd: DeactivateHabitCommand):
    state = load_state()

    if cmd.habit_id not in state:
        return {"error": "Habit not found"}

    habit = state[cmd.habit_id]
    habit["state"] = HabitState.INACTIVE

    state[cmd.habit_id] = habit
    save_state(state)

    return habit