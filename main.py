from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from . import models
from .database import SessionLocal
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

app = FastAPI(title="FitBuddy AI")
Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    workout_plan = f"""
7-DAY WORKOUT PLAN

Day 1 - Full Body
Warm-up: 5-10 minutes
Main workout: Bodyweight exercises
Cooldown: 5-10 minutes

Day 2 - Cardio
Warm-up: 5 minutes
Main workout: Moderate cardio
Cooldown: 5-10 minutes

Day 3 - Upper Body
Warm-up: 5-10 minutes
Main workout: Upper-body exercises
Cooldown: 5-10 minutes

Day 4 - Recovery
Light movement and stretching.

Day 5 - Lower Body
Warm-up: 5-10 minutes
Main workout: Lower-body exercises
Cooldown: 5-10 minutes

Day 6 - Core & Cardio
Warm-up: 5-10 minutes
Main workout: Core exercises and moderate cardio
Cooldown: 5-10 minutes

Day 7 - Rest / Recovery
Light stretching and recovery.

Goal: {goal}
Intensity: {intensity}
"""

    nutrition_tip = (
        f"For your goal of {goal}, focus on balanced meals, "
        "adequate hydration, and regular recovery. "
        "Include a suitable protein source with meals."
    )
    db = SessionLocal()

    try:
        user = models.User(
            user_id=user_id,
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

        db.add(user)

        workout = models.WorkoutPlan(
            user_id=user_id,
            workout_plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(workout)

        db.commit()

    finally:
        db.close()
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": username,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
        }
    )


@app.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...)
):
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": "User",
            "user_id": user_id,
            "age": "-",
            "weight": "-",
            "goal": "Updated plan",
            "intensity": "-",
            "workout_plan": (
                "Your feedback has been received.\n\n"
                f"Feedback: {feedback}\n\n"
                "AI-based plan updating will be connected in the next step."
            ),
            "nutrition_tip": (
                "Keep hydration, balanced nutrition, and recovery in mind."
            ),
        }
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "FitBuddy AI is running"
    }