from typing import Literal

from pydantic import BaseModel, Field


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "strength",
]

Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=300)
    goal: Goal
    intensity: Intensity


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=100)
    feedback: str = Field(min_length=3, max_length=2000)


class Exercise(BaseModel):
    name: str
    sets: str
    reps_or_duration: str
    rest: str


class WorkoutDay(BaseModel):
    day: str
    focus: str
    warm_up: list[str]
    exercises: list[Exercise]
    cool_down: list[str]
    recovery_note: str


class WorkoutPlan(BaseModel):
    title: str
    overview: str
    days: list[WorkoutDay]


class NutritionTip(BaseModel):
    tip: str
    hydration: str
    recovery: str