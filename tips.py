from app.ai.gemini_client import generate_structured
from app.config import settings
from app.schemas import NutritionTip


def generate_demo_tip(goal: str) -> NutritionTip:

    tips = {
        "weight loss": (
            "Build balanced meals around vegetables, "
            "whole grains and a protein source."
        ),
        "muscle gain": (
            "Include a protein-rich food in regular meals "
            "and stay hydrated."
        ),
        "general wellness": (
            "Aim for balanced meals, regular hydration "
            "and consistent sleep."
        ),
        "flexibility": (
            "Stay hydrated and include a variety of "
            "nutrient-rich foods."
        ),
        "strength": (
            "Include protein-rich foods and enough "
            "overall nutrition to support training."
        ),
    }

    return NutritionTip(
        tip=tips.get(
            goal,
            "Choose balanced meals and stay hydrated.",
        ),
        hydration="Drink water regularly throughout the day.",
        recovery="Prioritize adequate sleep and recovery.",
    )


def generate_nutrition_tip_with_flash(
    goal: str,
) -> NutritionTip:

    if not settings.GOOGLE_API_KEY:
        return generate_demo_tip(goal)

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Fitness goal:
{goal}

Provide a concise wellness-oriented nutrition/recovery tip.

Return:
- tip
- hydration
- recovery

Rules:
- Do not provide medical treatment.
- Do not prescribe supplements.
- Do not recommend extreme dieting.
- Do not give dangerous weight-loss instructions.
- Use general healthy-eating guidance.
- Keep the response concise and practical.

Return only the requested structured data.
"""

    return generate_structured(
        model=settings.GEMINI_TIP_MODEL,
        prompt=prompt,
        schema=NutritionTip,
    )