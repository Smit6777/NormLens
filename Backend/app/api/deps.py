from fastapi import Request
from app.main import AppState

def get_services(request: Request) -> AppState:
    return request.app.state.services
