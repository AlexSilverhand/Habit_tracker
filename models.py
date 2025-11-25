from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from datetime import date


# --- Estados del hábito ---
class HabitState(str, Enum):
    ACTIVE = "Active"
    COMPLETED_TODAY = "CompletedToday"
    MISSED = "Missed"
    INACTIVE = "Inactive"


# --- Comandos ---
class CreateHabitCommand(BaseModel):
    name: str
    description: Optional[str] = ""
    goal_per_week: int


class MarkHabitDoneCommand(BaseModel):
    habit_id: str
    day: str  # YYYY-MM-DD


class DeactivateHabitCommand(BaseModel):
    habit_id: str


# --- Modelo del hábito ---
class HabitModel(BaseModel):
    id: str
    name: str
    description: str
    goal_per_week: int
    completions: List[str]  # lista de fechas en formato string
    state: HabitState