from app.ai.gemini_client import generate_structured
from app.config import settings
from app.schemas import WorkoutPlan


def generate_demo_workout(
    username: str,
    goal: str,
    intensity: str,
) -> WorkoutPlan:

    intensity_note = {
        "low": "Keep the pace comfortable and prioritize technique.",
        "medium": "Use a moderate effort and take adequate rest.",
        "high": "Use challenging but controlled effort and stop if you feel pain.",
    }[intensity]

    focuses = [
        "Full Body",
        "Lower Body",
        "Cardio",
        "Upper Body",
        "Core & Mobility",
        "Full Body",
        "Recovery & Flexibility",
    ]

    days = []

    for index, focus in enumerate(focuses, start=1):

        days.append(
            {
                "day": f"Day {index}",
                "focus": focus,
                "warm_up": [
                    "5 minutes of easy movement",
                    "Gentle dynamic mobility",
                ],
                "exercises": [
                    {
                        "name": "Bodyweight Squat",
                        "sets": "2",
                        "reps_or_duration": "8-12 reps",
                        "rest": "60-90 seconds",
                    },
                    {
                        "name": "Wall Push-up",
                        "sets": "2",
                        "reps_or_duration": "8-12 reps",
                        "rest": "60-90 seconds",
                    },
                    {
                        "name": "Easy March",
                        "sets": "1",
                        "reps_or_duration": "5 minutes",
                        "rest": "As needed",
                    },
                ],
                "cool_down": [
                    "Gentle stretching",
                    "Slow breathing",
                ],
                "recovery_note": intensity_note,
            }
        )

    return WorkoutPlan(
        title=f"FitBuddy 7-Day Plan for {username}",
        overview=(
            f"This is a demo {intensity}-intensity plan "
            f"designed around the goal of {goal}. "
            "Adjust activity to your comfort level."
        ),
        days=days,
    )


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> WorkoutPlan:

    prompt = f"""
You are FitBuddy, a wellness-oriented workout planning assistant.

Create a structured 7-day workout plan.

User information:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}

Requirements:

1. Return exactly 7 days.
2. Each day must have:
   - day
   - focus
   - warm_up
   - exercises
   - cool_down
   - recovery_note
3. Each exercise must include:
   - name
   - sets
   - reps_or_duration
   - rest
4. Keep the plan practical and beginner-friendly.
5. Do not recommend extreme exercise.
6. Do not diagnose medical conditions.
7. Do not prescribe medical treatment.
8. Do not recommend dangerous activities.
9. Include rest/recovery appropriately.
10. If an activity causes pain, advise stopping and seeking appropriate professional guidance.
11. Avoid calorie restriction or extreme weight-loss instructions.
12. Keep the plan concise and easy to follow.

Return only data matching the provided schema.
"""

    return generate_structured(
        model=settings.GEMINI_WORKOUT_MODEL,
        prompt=prompt,
        schema=WorkoutPlan,
    )


def generate_workout(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> WorkoutPlan:

    if not settings.GOOGLE_API_KEY:
        return generate_demo_workout(
            username,
            goal,
            intensity,
        )

    return generate_workout_gemini(
        username=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )


def update_workout_plan(
    original_plan: str,
    feedback: str,
    username: str,
    goal: str,
    intensity: str,
) -> WorkoutPlan:

    if not settings.GOOGLE_API_KEY:
        demo = generate_demo_workout(
            username=username,
            goal=goal,
            intensity=intensity,
        )

        demo.overview += (
            f" Feedback incorporated: {feedback}"
        )

        return demo

    prompt = f"""
You are updating an existing FitBuddy workout plan.

User:
Name: {username}
Goal: {goal}
Intensity: {intensity}

Original plan:
{original_plan}

User feedback:
{feedback}

Create a revised 7-day plan.

Requirements:
- Preserve useful parts of the original plan.
- Apply the user's feedback where reasonable.
- Keep exactly 7 days.
- Maintain warm-up, exercises, cool-down and recovery.
- Keep the plan safe and practical.
- Do not prescribe medical treatment.
- Do not recommend extreme dieting or exercise.
- Do not diagnose health conditions.
- If the requested change could be unsafe, use a safer alternative.

Return only the structured plan matching the provided schema.
"""

    return generate_structured(
        model=settings.GEMINI_WORKOUT_MODEL,
        prompt=prompt,
        schema=WorkoutPlan,
    )