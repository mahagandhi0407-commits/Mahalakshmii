from fastapi import Request

from app.config import settings


SESSION_KEY = "fitbuddy_admin"


def is_admin(request: Request) -> bool:
    return bool(request.session.get(SESSION_KEY))


def authenticate(username: str, password: str) -> bool:
    return (
        username == settings.ADMIN_USERNAME
        and password == settings.ADMIN_PASSWORD
    )


def login(request: Request):
    request.session[SESSION_KEY] = True


def logout(request: Request):
    request.session.pop(SESSION_KEY, None)