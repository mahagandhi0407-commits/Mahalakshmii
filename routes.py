from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.ai.tips import generate_nutrition_tip_with_flash
from app.ai.workout import (
    generate_workout,
    update_workout_plan,
)
from app.auth import (
    authenticate,
    is_admin,
    login,
    logout,
)
from app.database import get_db
from app.models import User, WorkoutPlan
from app.schemas import UserInput
from app.utils import plan_to_json, pretty_plan


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "FitBuddy",
        },
    )


@router.post("/generate-workout")
def generate_workout_route(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user_input = UserInput(
            username=username.strip(),
            user_id=user_id.strip(),
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Invalid Input",
                "message": str(exc),
            },
            status_code=400,
        )

    existing_user = (
        db.query(User)
        .filter(User.user_id == user_input.user_id)
        .first()
    )

    if existing_user:
        user = existing_user

        user.username = user_input.username
        user.age = user_input.age
        user.weight = user_input.weight
        user.goal = user_input.goal
        user.intensity = user_input.intensity

    else:
        user = User(
            user_id=user_input.user_id,
            username=user_input.username,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
        )

        db.add(user)

    db.commit()

    try:
        workout = generate_workout(
            username=user_input.username,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
        )

        nutrition = generate_nutrition_tip_with_flash(
            user_input.goal
        )

    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "AI Error",
                "message": (
                    "The AI service could not generate "
                    f"the plan. Details: {exc}"
                ),
            },
            status_code=500,
        )

    workout_json = plan_to_json(workout)

    nutrition_text = (
        f"{nutrition.tip}\n\n"
        f"Hydration: {nutrition.hydration}\n\n"
        f"Recovery: {nutrition.recovery}"
    )

    plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.user_id == user_input.user_id
        )
        .first()
    )

    if plan:
        plan.original_plan = workout_json
        plan.updated_plan = None
        plan.nutrition_tip = nutrition_text
        plan.feedback = None
        plan.updated_at = None

    else:
        plan = WorkoutPlan(
            user_id=user_input.user_id,
            original_plan=workout_json,
            nutrition_tip=nutrition_text,
        )

        db.add(plan)

    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "Your FitBuddy Plan",
            "user": user,
            "plan": plan,
            "workout_plan": pretty_plan(
                workout_json
            ),
            "nutrition_tip": nutrition_text,
            "updated": False,
        },
    )


@router.post("/submit-feedback")
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    plan = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id)
        .first()
    )

    if not user or not plan:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "User Not Found",
                "message": "No workout plan was found for this User ID.",
            },
            status_code=404,
        )

    feedback = feedback.strip()

    if not feedback:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Feedback Required",
                "message": "Please enter some feedback.",
            },
            status_code=400,
        )

    try:
        updated = update_workout_plan(
            original_plan=plan.original_plan,
            feedback=feedback,
            username=user.username,
            goal=user.goal,
            intensity=user.intensity,
        )

        updated_json = plan_to_json(updated)

        plan.updated_plan = updated_json
        plan.feedback = feedback
        plan.updated_at = datetime.utcnow()

        db.commit()

    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Update Error",
                "message": str(exc),
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "title": "Updated FitBuddy Plan",
            "user": user,
            "plan": plan,
            "workout_plan": pretty_plan(
                updated_json
            ),
            "nutrition_tip": plan.nutrition_tip,
            "updated": True,
        },
    )


@router.get("/view-all-users")
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    if not is_admin(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    plans = (
        db.query(WorkoutPlan)
        .all()
    )

    plan_map = {
        plan.user_id: plan
        for plan in plans
    }

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "title": "Admin Dashboard",
            "users": users,
            "plan_map": plan_map,
        },
    )


@router.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={
            "title": "Admin Login",
        },
    )


@router.post("/admin/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if authenticate(username, password):
        login(request)

        return RedirectResponse(
            url="/view-all-users",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={
            "title": "Admin Login",
            "error": "Invalid username or password.",
        },
        status_code=401,
    )


@router.get("/admin/logout")
def admin_logout(request: Request):
    logout(request)

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@router.post("/admin/delete/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    if not is_admin(request):
        return RedirectResponse(
            url="/admin/login",
            status_code=303,
        )

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user:
        db.delete(user)

    plan = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id)
        .first()
    )

    if plan:
        db.delete(plan)

    db.commit()

    return RedirectResponse(
        url="/view-all-users",
        status_code=303,
    )